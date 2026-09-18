from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q, Value, F
from django.db.models.functions import LTrim
import pandas as pd
import re
from flaime_py.food_labels.models import (
    StoreProduct, StoreProductNutritionFact, UPC, StoreProductUPC, Nutrient, Unit
)

class Command(BaseCommand):
    help = 'Load supplemented food NFT data from Google Sheets export'
    
    NUTRIENT_MAPPING = {
        'Calories': 'Energy',
        'Total Fat (g)': 'FAT (TOTAL LIPIDS)',
        'Saturated Fat (g)': 'FATTY ACIDS, SATURATED, TOTAL',
        'Trans Fat (g)': 'FATTY ACIDS, TRANS, TOTAL',
        'Total Carbohydrate (g)': 'Carbohydrate, total',
        'Dietary Fiber (g)': 'Fibre, total dietary',
        'Total Sugars (g)': 'Sugars, total',
        'Protein (g)': 'Protein',
        'Cholesterol (mg)': 'Cholesterol',
        'Sodium (mg)': 'Sodium',
        'Potassium (mg)': 'Potassium',
        'Calcium (mg)': 'Calcium',
        'Iron (mg)': 'Iron',
    }
    
    SUPPLEMENTAL_MAPPING = {
        'pantothenicacid': 'PANTOTHENIC ACID',
        'vitaminb6': 'VITAMIN B-6',
        'vitaminb12': 'VITAMIN B-12',
        'vitaminc': 'VITAMIN C',
        'vitamina': 'VITAMIN A (MICROGRAMS)',
        'vitamind': 'VITAMIN D (MICROGRAMS)',
        'vitamine': 'VITAMIN E, TOTAL TOCOPHEROLS',
        'vitamink': 'VITAMIN K',
        'thiamine': 'THIAMINE',
        'riboflavin': 'RIBOFLAVIN',
        'niacin': 'NIACIN (NICOTINIC ACID) PREFORMED',
        'folate': 'FOLIC ACID',
        'biotin': 'BIOTIN',
        'choline': 'CHOLINE, TOTAL',
        'phosphorus': 'PHOSPHORUS',
        'iodine': 'IODIDE',
        'magnesium': 'MAGNESIUM',
        'zinc': 'ZINC',
        'selenium': 'SELENIUM',
        'copper': 'COPPER',
        'manganese': 'MANGANESE',
        'chromium': 'CHROMIUM',
        'molybdenum': 'MOLYBDENUM',
        'chloride': 'CHLORIDE',
        'caffeine': 'CAFFEINE',
        'taurine': 'TAURINE',
        'potassium': 'POTASSIUM',
        'calcium': 'CALCIUM',
        'vitaminaretinol': 'VITAMIN A (MICROGRAMS)',
        'thiaminevitaminb1': 'THIAMINE',
        'lisoleucine': 'ISOLEUCINE',
        'lleucine': 'LEUCINE',
        'lvaline': 'VALINE',
        'glycine': 'GLYCINE',
        'lalanine': 'ALANINE',
        'lglutamine': 'GLUTAMINE',
        'lphenylalanine': 'phenylalanine',
        'llysine': 'LYSINE',
        'larginine': 'ARGININE',
    }

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='CSV export from Google Sheets')
        parser.add_argument('--dry-run', action='store_true', help='Preview without loading')
        parser.add_argument('--clear-existing', action='store_true', help='Clear existing NFT data')
    
    def handle(self, *args, **options):
        file_path = options['file']
        dry_run = options['dry_run']
        clear_existing = options['clear_existing']
        
        self.stdout.write(f'Reading {file_path}...')
        df = pd.read_csv(file_path)
        
        df['Barcode'] = df['Barcode'].astype(str).str.strip()
        
        self.stdout.write(f'Found {len(df)} products\n')
        
        if dry_run:
            self._dry_run(df)
            return
        
        self._load_data(df, clear_existing)

    def _dry_run(self, df):
        self.stdout.write(self.style.WARNING('=== DRY RUN ===\n'))
        
        would_update = 0
        would_skip = 0
        not_found = []
        
        for _, row in df.iterrows():
            barcode = row['Barcode']
            product_name = row.get('Product Name', 'Unknown')
            
            standard_nft, supplemental_nft, serving_size_info = self._parse_row_to_nft(row)
            
            store_products = self._find_store_products_by_barcode(barcode)

            if store_products:
                for store_product in store_products:
                    serving_desc = serving_size_info.get('serving_description', 'N/A')
                    serving_size = serving_size_info.get('serving_size', 'N/A')
                    serving_unit = serving_size_info.get('serving_unit', 'N/A')

                    changes = self._compare_store_product_data(
                        store_product, standard_nft, supplemental_nft, serving_size_info)

                    self.stdout.write(
                        f'  ✓ {barcode} ({product_name})\n'
                        f'    → Store product {store_product.id}: {store_product.site_name}\n'
                        f'    → Serving: {serving_desc} ({serving_size} {serving_unit})'
                    )
                    
                    if changes['serving_changed']:
                        self.stdout.write(self.style.WARNING(
                            f'    → Serving size would change: '
                            f'{changes["old_serving"]} → {changes["new_serving"]}'
                        ))
                    
                    if changes['new_nutrients']:
                        self.stdout.write(
                            f'    → Would add {len(changes["new_nutrients"])} new nutrients'
                        )
                        for nutrient_name, data in list(changes['new_nutrients'].items())[:3]:
                            self.stdout.write(f'        + {nutrient_name}: {data["amount"]} {data["unit"]}')
                        if len(changes['new_nutrients']) > 3:
                            self.stdout.write(f'        ... and {len(changes["new_nutrients"]) - 3} more')
                    
                    if changes['changed_nutrients']:
                        self.stdout.write(
                            f'    → Would update {len(changes["changed_nutrients"])} nutrients'
                        )
                        for nutrient_name, diff in list(changes['changed_nutrients'].items())[:3]:
                            self.stdout.write(
                                f'        ~ {nutrient_name}: {diff["old"]} → {diff["new"]}'
                            )
                        if len(changes['changed_nutrients']) > 3:
                            self.stdout.write(f'        ... and {len(changes["changed_nutrients"]) - 3} more')
                    
                    if changes['unchanged_nutrients']:
                        self.stdout.write(
                            f'    → {len(changes["unchanged_nutrients"])} nutrients already match'
                        )
                    
                    if not changes['serving_changed'] and not changes['new_nutrients'] and not changes['changed_nutrients']:
                        self.stdout.write('    → No changes needed')
                    
                    would_update += 1
            else:
                not_found.append({'barcode': barcode, 'name': product_name})
                self.stdout.write(
                    self.style.WARNING(
                        f'  ✗ {barcode} ({product_name})\n'
                        f'    → No product found\n'
                        f'    → Would have loaded {len(standard_nft) + len(supplemental_nft)} nutrients'
                    )
                )
            
            self.stdout.write('')
        
        self._print_summary(would_update, would_skip, not_found, dry_run=True)

    def _load_data(self, df, clear_existing):
        updated_store_products = 0
        skipped = 0
        not_found = []

        with transaction.atomic():
            for _, row in df.iterrows():
                barcode = row['Barcode']
                product_name = row.get('Product Name', 'Unknown')

                store_products = self._find_store_products_by_barcode(barcode)

                if not store_products:
                    not_found.append({'barcode': barcode, 'name': product_name})
                    self.stdout.write(
                        self.style.WARNING(f'  ✗ {barcode} ({product_name}): No product found')
                    )
                    continue

                standard_nft, supplemental_nft, serving_size_info = self._parse_row_to_nft(row)

                serving_size_unit = None
                if 'serving_unit' in serving_size_info:
                    serving_size_unit = self._get_unit(serving_size_info['serving_unit'])

                for store_product in store_products:
                    if clear_existing:
                        deleted = StoreProductNutritionFact.objects.filter(
                            store_product=store_product
                        ).delete()
                        self.stdout.write(f'    Cleared {deleted[0]} existing nutrition facts')

                    if 'serving_size' in serving_size_info:
                        store_product.serving_size = serving_size_info['serving_size']
                        store_product.serving_size_unit = serving_size_unit
                        store_product.save()

                    standard_count = self._load_nft_for_store_product(
                        store_product, standard_nft, supplemented=False)
                    supplemental_count = self._load_nft_for_store_product(
                        store_product, supplemental_nft, supplemented=True)

                    updated_store_products += 1

                    serving_desc = serving_size_info.get('serving_description', 'N/A')
                    self.stdout.write(
                        f'  ✓ {barcode} ({product_name})\n'
                        f'    → Store product {store_product.id} updated:\n'
                        f'       • Serving: {serving_desc}\n'
                        f'       • {standard_count} standard nutrients (supplemented=False)\n'
                        f'       • {supplemental_count} supplemental nutrients (supplemented=True)'
                    )

        self._print_summary(updated_store_products, skipped, not_found,
                          dry_run=False, updated_store_products=updated_store_products)

    def _print_summary(self, updated, skipped, not_found, dry_run=False, updated_store_products=0):
        self.stdout.write('\n' + '='*60)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN SUMMARY'))
        else:
            self.stdout.write(self.style.SUCCESS('SUMMARY'))
        
        self.stdout.write('='*60)
        
        total = updated + skipped + len(not_found)
        self.stdout.write(f'Total products in file: {total}')
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'Would update: {updated} products'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated: {updated} products'))
            if updated_store_products:
                self.stdout.write(self.style.SUCCESS(f'Updated: {updated_store_products} store products'))
        
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'Skipped: {skipped} products'))
        
        if not_found:
            self.stdout.write(self.style.ERROR(f'Not found: {len(not_found)} products'))
            self.stdout.write('')
            self.stdout.write('Products not found:')
            for item in not_found:
                self.stdout.write(f'  • Barcode: {item["barcode"]} - {item["name"]}')
        
        self.stdout.write('='*60 + '\n')

    def _compare_store_product_data(self, store_product, standard_nft, supplemental_nft, serving_size_info):
        changes = {
            'serving_changed': False,
            'old_serving': None,
            'new_serving': None,
            'new_nutrients': {},
            'changed_nutrients': {},
            'unchanged_nutrients': []
        }
        
        if 'serving_size' in serving_size_info:
            new_serving_size = serving_size_info['serving_size']
            new_serving_unit = self._get_unit(serving_size_info.get('serving_unit'))
            
            old_serving = f"{store_product.serving_size} {store_product.serving_size_unit.name if store_product.serving_size_unit else 'N/A'}"
            new_serving = f"{new_serving_size} {new_serving_unit.name if new_serving_unit else 'N/A'}"

            if (store_product.serving_size != new_serving_size or
                store_product.serving_size_unit != new_serving_unit):
                changes['serving_changed'] = True
                changes['old_serving'] = old_serving
                changes['new_serving'] = new_serving
        
        all_nft = {**standard_nft, **supplemental_nft}
        
        for nutrient_name, data in all_nft.items():
            if nutrient_name.startswith('_'):
                continue
            
            nutrient = self._get_nutrient(nutrient_name)
            if not nutrient:
                continue
            
            existing = StoreProductNutritionFact.objects.filter(
                store_product=store_product,
                nutrient=nutrient
            ).first()
            
            if not existing:
                changes['new_nutrients'][nutrient_name] = data
            else:
                new_amount = data['amount']
                new_dv = data['daily_value']
                new_unit = self._get_unit(data['unit']) if data['unit'] else None
                
                amount_changed = existing.amount != new_amount
                dv_changed = existing.daily_value != new_dv
                unit_changed = existing.amount_unit != new_unit
                
                if amount_changed or dv_changed or unit_changed:
                    old_str = f"{existing.amount} {existing.amount_unit.name if existing.amount_unit else 'N/A'}"
                    new_str = f"{new_amount} {new_unit.name if new_unit else 'N/A'}"
                    if dv_changed:
                        old_str += f" ({existing.daily_value}% DV)"
                        new_str += f" ({new_dv}% DV)"
                    changes['changed_nutrients'][nutrient_name] = {
                        'old': old_str,
                        'new': new_str
                    }
                else:
                    changes['unchanged_nutrients'].append(nutrient_name)
        
        return changes

    def _parse_row_to_nft(self, row):
        standard_nft = {}
        supplemental_nft = {}
        serving_size_info = {}
        
        for col_name, nutrient_name in self.NUTRIENT_MAPPING.items():
            if col_name in row and pd.notna(row[col_name]):
                amount = row[col_name]
                
                if amount == 0 or amount == '0':
                    continue
                
                unit_match = re.search(r'\((\w+)\)', col_name)
                unit = unit_match.group(1) if unit_match else None
                
                dv_col = f"{col_name.split('(')[0].strip()} %DV"
                daily_value = row.get(dv_col) if dv_col in row and pd.notna(row.get(dv_col)) else None
                
                standard_nft[nutrient_name] = {
                    'amount': float(amount),
                    'unit': unit,
                    'daily_value': int(daily_value) if daily_value else None
                }
        
        if 'Supplemental Nutrients' in row and pd.notna(row['Supplemental Nutrients']):
            supplemental_nft = self._parse_supplemental_nutrients(row['Supplemental Nutrients'])
        
        if 'Serving Amount' in row and pd.notna(row['Serving Amount']):
            serving_size_info['serving_size'] = int(row['Serving Amount'])
        
        if 'Serving Unit' in row and pd.notna(row['Serving Unit']):
            serving_size_info['serving_unit'] = row['Serving Unit']
        
        if 'Serving Description' in row and pd.notna(row['Serving Description']):
            serving_size_info['serving_description'] = row['Serving Description']
        
        return standard_nft, supplemental_nft, serving_size_info
        
    def _parse_supplemental_nutrients(self, supplemental_str):
        nft_data = {}
        
        nutrients = supplemental_str.split(';')
        
        for nutrient in nutrients:
            nutrient = nutrient.strip()
            if not nutrient:
                continue
            
            match = re.match(
                r'(\w+):\s*([0-9.]+)\s*(\w+)\s*(?:\(([0-9.]+)%\s*DV\))?',
                nutrient,
                re.IGNORECASE
            )
            
            if match:
                raw_name = match.group(1).lower().strip()
                amount = float(match.group(2))
                unit = match.group(3)
                daily_value = float(match.group(4)) if match.group(4) else None
                
                standard_name = self.SUPPLEMENTAL_MAPPING.get(raw_name)
                
                if standard_name:
                    nft_data[standard_name] = {
                        'amount': amount,
                        'unit': unit,
                        'daily_value': int(daily_value) if daily_value else None
                    }
                else:
                    self.stdout.write(
                        self.style.WARNING(f'    ⚠ Unknown supplemental nutrient: {raw_name}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'    ⚠ Could not parse: {nutrient}')
                )
        
        return nft_data
    
    def _load_nft_for_store_product(self, store_product, nft_data, supplemented):
        loaded_count = 0

        for nutrient_name, data in nft_data.items():
            if nutrient_name.startswith('_'):
                continue

            nutrient = self._get_nutrient(nutrient_name)
            unit = self._get_unit(data['unit']) if data['unit'] else None

            if not nutrient:
                self.stdout.write(
                    self.style.WARNING(f'      ⚠ Nutrient not found: {nutrient_name}')
                )
                continue

            StoreProductNutritionFact.objects.update_or_create(
                store_product=store_product,
                nutrient=nutrient,
                defaults={
                    'amount': data['amount'],
                    'amount_unit': unit,
                    'daily_value': data['daily_value'],
                    'supplemented': supplemented,
                    'created_by': 'supplemented_nft_loader',
                    'modified_by': 'supplemented_nft_loader'
                }
            )
            loaded_count += 1

        return loaded_count


    def _calculate_upc_check_digit(self, barcode):
        barcode = barcode.rstrip()[:11]
        
        if not barcode.isdigit():
            return None
            
        barcode = barcode.zfill(11)
        
        odd_sum = sum(int(barcode[i]) for i in range(0, 11, 2))
        even_sum = sum(int(barcode[i]) for i in range(1, 11, 2))
        
        total = odd_sum * 3 + even_sum
        check_digit = (10 - (total % 10)) % 10
        
        return str(check_digit)

    def _find_store_products_by_barcode(self, barcode):
        normalized = barcode.lstrip('0') or '0'

        store_product_upc = self._lookup_store_product_upc(normalized)

        if not store_product_upc and 7 <= len(normalized) <= 11:
            check_digit = self._calculate_upc_check_digit(normalized)

            if check_digit is not None:
                store_product_upc = self._lookup_store_product_upc(normalized + check_digit)

        return [store_product_upc.store_product] if store_product_upc else []

    def _lookup_store_product_upc(self, barcode):
        return StoreProductUPC.objects.filter(
            upc__code__regex=r'^0*' + barcode + '$',
            upc__deleted=False,
            store_product__supplemented_food=True
        ).select_related('store_product').order_by('-store_product__created_datetime').first()
    
    def _get_nutrient(self, name):
        return Nutrient.objects.filter(name__icontains=name, deleted=False).first()
    
    def _get_unit(self, name):
        if not name:
            return None
        if name == 'mcg':
            return Unit.objects.filter(name__iexact='ug').first()
        return Unit.objects.filter(name__iexact=name, deleted=False).first()