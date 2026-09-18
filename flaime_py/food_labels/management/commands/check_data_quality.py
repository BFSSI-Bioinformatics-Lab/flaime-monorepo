from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef, Count, Q
from flaime_py.food_labels.models import StoreProduct, StoreProductNutritionFact, StoreProductImage
from datetime import datetime

class Command(BaseCommand):
    help = 'Check data quality for a specified subset of store products and report issues'

    def add_arguments(self, parser):
        parser.add_argument('--source', type=str, choices=['Nielsen', 'FLIP'], help='Check products from a specific source')
        parser.add_argument('--batch', type=int, help='Check products from a specific batch ID')
        parser.add_argument('--date', type=str, help='Check products from a specific date (YYYY-MM-DD)')
        parser.add_argument('--category', type=int, help='Check products from a specific category ID')
        parser.add_argument('--limit', type=int, default=None, help='Limit the number of products to check')

    def handle(self, *args, **options):
        store_products = self.get_store_products(options)
        self.check_and_display_results(store_products, options['limit'])

    def get_store_products(self, options):
        queryset = StoreProduct.objects.all()

        if options['source']:
            source_name = "Nielsen 2017" if options['source'] == 'Nielsen' else options['source']
            queryset = queryset.filter(source__name=source_name)

        if options['batch']:
            queryset = queryset.filter(scrape_batch_id=options['batch'])
        if options['date']:
            date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            queryset = queryset.filter(created_datetime__date=date)
        if options['category']:
            queryset = queryset.filter(manual_categories__category_id=options['category'])

        return queryset

    def check_and_display_results(self, queryset, limit):
        # manufacturers/product_profiles were dropped in the FSDH migration, so the
        # manufacturer column is gone; company is the surviving equivalent.
        queryset = queryset.annotate(
            has_nft_data=Exists(StoreProductNutritionFact.objects.filter(store_product=OuterRef('pk'))),
            has_photo=Exists(StoreProductImage.objects.filter(store_product=OuterRef('pk'))),
            category_count=Count('manual_categories'),
        ).select_related('company')

        if limit:
            queryset = queryset[:limit]

        headers = [
            "Store Product ID", "Name", "NFT Flag", "NFT Data",
            "Ingredients", "Photo", "Has Category", "Has Company", "All Data"
        ]
        self.stdout.write('\t'.join(headers))

        count = 0
        issues_count = 0

        for sp in queryset.iterator(chunk_size=2000):
            nft_flag = sp.nutrition_available_flag
            nft_data = sp.has_nft_data
            ingredients = bool(sp.ingredient_en)
            photo = sp.has_photo
            has_category = sp.category_count > 0
            has_company = sp.company_id is not None
            all_data = nft_flag and nft_data and ingredients and photo and has_category and has_company

            if not all_data:
                row = [
                    str(sp.id),
                    (sp.site_name or 'N/A')[:50],
                    'Yes' if nft_flag else 'No',
                    'Yes' if nft_data else 'No',
                    'Yes' if ingredients else 'No',
                    'Yes' if photo else 'No',
                    'Yes' if has_category else 'No',
                    'Yes' if has_company else 'No',
                    'No'  # All Data is always No if we're printing this row
                ]
                self.stdout.write('\t'.join(row))
                issues_count += 1

            count += 1

        self.stdout.write(self.style.SUCCESS(f"\nChecked {count} store products. Found issues with {issues_count} products."))