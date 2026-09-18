from django.core.management.base import BaseCommand, CommandError
import pandas as pd
from flaime_py.food_labels.models import (
    StoreProductPredictedCategory,
    StoreProductManualCategory,
    StoreProduct,
    Category,
    StoreProductUPC,
    UPC
)
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Load predicted or manual product categories from CSV'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)
        parser.add_argument(
            '--manual',
            action='store_true',
            help='Upload manual product categories instead of predicted'
        )
        parser.add_argument('--source-id', type=int, nargs='+', help='Filter to store products from these sources')
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip predictions that already exist for the same product and model'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Validate and report without writing to the database'
        )

    def handle(self, *args, **options):
        if options['manual']:
            self.handle_manual(options)
        else:
            self.handle_predicted(options)

    def handle_manual(self, options):
        df = pd.read_csv(options['file'], dtype={'Label UPC': str})
        dry_run = options['dry_run']

        db_user = User.objects.get(email='bfssi.kate.cook@gmail.com')

        upc_codes = set(df['Label UPC'].astype(str))

        source_ids = options['source_id']
        store_product_upcs = StoreProductUPC.objects.filter(
            upc__code__in=upc_codes
        ).select_related('store_product', 'upc')

        if source_ids:
            store_product_upcs = store_product_upcs.filter(
                store_product__source_id__in=source_ids
            )

        upc_map = {}

        for pu in store_product_upcs:
            key = str(pu.upc.code)
            if key in upc_map:
                #print(f'Warning: multiple StoreProducts for UPC {key}')
                upc_map[key].append(pu.store_product)
            else:
                upc_map[key] = [pu.store_product]

        category_codes = set(df['RA_category'].astype(str)) | set(df['RA_item'].astype(str))
        category_map = {
            c.code: c
            for c in Category.objects.filter(code__in=category_codes)
        }

        skipped = 0
        created = 0
        updated = 0

        for _, row in df.iterrows():
            upc = str(row['Label UPC'])
            external_id = str(row['External ID'])
            ra_category_code = str(row['RA_category'])
            ra_item_code = str(row['RA_item'])

            if upc not in upc_map:
                #self.stderr.write(f'Warning: no StoreProduct found for UPC {upc}, external ID {external_id}, skipping')
                skipped += 1
                continue

            for store_product in upc_map[upc]:
                categories_to_assign = []

                for code in (ra_category_code, ra_item_code):
                    if code not in category_map:
                        self.stderr.write(f'Warning: category code {code} not found for upc {upc}, skipping row')
                        break
                    categories_to_assign.append(category_map[code])
                else:
                    for category in categories_to_assign:
                        if dry_run:
                            existing = StoreProductManualCategory.objects.filter(
                                store_product=store_product,
                                category__level=category.level,
                                category__scheme=category.scheme,
                            ).first()
                            if existing:
                                updated += 1
                                print(existing)
                            else:
                                created += 1
                                print(f'Created: store product id {store_product.id} category id {category.id}')
                            continue

                        obj, was_created = StoreProductManualCategory.objects.update_or_create(
                            store_product=store_product,
                            category__level=category.level,
                            category__scheme=category.scheme,
                            defaults={
                                'category': category,
                                'user': db_user,
                            }
                        )
                        if was_created:
                            created += 1
                        else:
                            updated += 1

        prefix = '[DRY RUN] ' if dry_run else ''
        self.stdout.write(f'{prefix}Skipped {skipped} rows')
        self.stdout.write(self.style.SUCCESS(f'{prefix}Created {created}, updated {updated} manual product categories'))

    def handle_predicted(self, options):
        dry_run = options['dry_run']
        df = pd.read_csv(options['file'])

        if df.isnull().any().any():
            raise CommandError('Found null values in data')

        # products was dropped in the FSDH migration; predictions now attach to store
        # products. Accept the legacy `product_id` header as an alias so existing
        # prediction CSVs keep loading — the ids were 1:1 across the migration.
        id_column = 'store_product_id' if 'store_product_id' in df.columns else 'product_id'
        if id_column not in df.columns:
            raise CommandError('CSV must have a store_product_id (or product_id) column')

        store_product_ids = set(df[id_column])
        category_ids = set(df['category_id'])

        existing_store_products = set(StoreProduct.objects.filter(
            id__in=store_product_ids
        ).values_list('id', flat=True))
        existing_categories = set(Category.objects.filter(
            id__in=category_ids
        ).values_list('id', flat=True))

        missing_store_products = store_product_ids - existing_store_products
        missing_categories = category_ids - existing_categories

        if missing_store_products:
            raise CommandError(f'Store products not found: {missing_store_products}')
        if missing_categories:
            raise CommandError(f'Categories not found: {missing_categories}')

        if options['skip_existing']:
            existing_predictions = set(
                StoreProductPredictedCategory.objects.filter(
                    store_product_id__in=store_product_ids
                ).values_list('store_product_id', 'model_id')
            )
            predictions = [
                StoreProductPredictedCategory(
                    store_product_id=row[id_column],
                    category_id=row['category_id'],
                    confidence=row['confidence'],
                    model_id=row['model_id']
                )
                for _, row in df.iterrows()
                if (row[id_column], row['model_id']) not in existing_predictions
            ]
            skipped = len(df) - len(predictions)
            if skipped:
                self.stdout.write(f'Skipped {skipped} existing predictions')
        else:
            predictions = [
                StoreProductPredictedCategory(
                    store_product_id=row[id_column],
                    category_id=row['category_id'],
                    confidence=row['confidence'],
                    model_id=row['model_id']
                )
                for _, row in df.iterrows()
            ]

        if not dry_run:
            StoreProductPredictedCategory.objects.bulk_create(predictions)

        model_ids = df['model_id'].unique()
        prefix = '[DRY RUN] ' if dry_run else ''
        self.stdout.write(
            self.style.SUCCESS(
                f'{prefix}Loaded {len(predictions)} predictions for models: {", ".join(model_ids)}'
            )
        )