from django.core.management.base import BaseCommand, CommandError
from flaime_py.food_labels.models import StoreProduct
from flaime_py.food_labels.exports import NUTRIENT_ORDER, iter_full_rows
from django.db import connection
import csv
import logging
from pathlib import Path
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)

__all__ = ["Command", "NUTRIENT_ORDER"]


class Command(BaseCommand):
    help = '''Export FLAIMEshot data to CSV with various filtering and formatting options.
    
Export Modes:
  full            Complete nutrient data export with all fields and optional supplementation info
  manual-review   Products flagged for manual verification with review reasons
  random-sample   Random sample of products (excludes manually flagged items)
  snapshot        All products in batch/source with basic identifying information

Examples:
  # Full export with all nutrients
  python manage.py export --mode full --output data.csv --supplemented
  
  # Products needing manual review
  python manage.py export --mode manual-review --batch 10,11,12
  
  # 20% random sample for quality checks
  python manage.py export --mode random-sample --source 5 --sample-rate 0.20
  
  # Complete snapshot of a batch
  python manage.py export --mode snapshot --batch 15
'''

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, default=None, 
                          help='Output file path (auto-generated if not provided)')
        
        parser.add_argument('--mode', type=str, choices=['full', 'manual-review', 'random-sample', 'snapshot'],
                          default='full', help='Export mode (default: full)')
        
        parser.add_argument('--batch', type=str, help='Comma-separated batch IDs to filter by')
        parser.add_argument('--source', type=str, help='Comma-separated source IDs to filter by')
        
        parser.add_argument('--batch-size', type=int, default=1000, 
                          help='Batch size for processing (full mode only)')
        parser.add_argument('--supplemented', action='store_true', 
                          help='Include supplemented nutrients and label flags (full mode only)')
        parser.add_argument('--all-barcodes', action='store_true', 
                          help='Export all barcodes separated by | (full mode only)')
        parser.add_argument('--include-description', action='store_true',
                          help='Include product description in export (full mode only)')
        
        parser.add_argument('--sample-rate', type=float, default=0.15,
                          help='Sampling rate as decimal (random-sample mode only, default: 0.15)')

    def handle(self, *args, **options):
        mode = options['mode']
        
        if mode == 'full':
            self._handle_full_export(options)
        elif mode == 'manual-review':
            self._handle_manual_review(options)
        elif mode == 'random-sample':
            self._handle_random_sample(options)
        elif mode == 'snapshot':
            self._handle_snapshot(options)

    def _get_filter_params(self, options):
        batch_ids = options.get('batch')
        source_ids = options.get('source')
        
        if batch_ids and source_ids:
            raise CommandError('Cannot provide both --batch and --source')
        
        filters = {}
        filter_type = None
        filter_values = None
        
        if batch_ids:
            id_list = [int(x.strip()) for x in batch_ids.split(',')]
            filters['scrape_batch_id__in'] = id_list
            filter_type = 'batch'
            filter_values = id_list
        elif source_ids:
            id_list = [int(x.strip()) for x in source_ids.split(',')]
            filters['source_id__in'] = id_list
            filter_type = 'source'
            filter_values = id_list
        
        return filters, filter_type, filter_values

    def _get_output_path(self, options, default_prefix):
        output_file = options.get('output')
        if output_file is None:
            date_prefix = datetime.now().strftime('%Y%m%d')
            output_file = f'{date_prefix}_{default_prefix}.csv'
        
        if Path(output_file).is_absolute():
            return output_file
        return Path(settings.BASE_DIR) / output_file

    def _handle_full_export(self, options):
        output_file = options.get('output')
        batch_size = options['batch_size']
        include_supplemented = options['supplemented']
        all_barcodes = options['all_barcodes']
        include_description = options['include_description']

        if output_file is None:
            output_file = self._get_output_path(options, 'flaimeshot_export')

        filters, filter_type, filter_values = self._get_filter_params(options)

        queryset = StoreProduct.objects.all()
        queryset = queryset.filter(**filters) if filters else queryset

        def _progress(start, end, total):
            self.stdout.write(f"Processing records {start + 1} to {end} of {total}")

        # Row/header logic is shared with the /api/storeproducts/export/ endpoint
        # (flaime_py.food_labels.exports); the first yield is the header row.
        rows = iter_full_rows(
            queryset,
            supplemented=include_supplemented,
            all_barcodes=all_barcodes,
            include_description=include_description,
            batch_size=batch_size,
            progress=_progress,
        )

        total_count = 0
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for index, row in enumerate(rows):
                writer.writerow(row)
                if index:  # skip the header row in the count
                    total_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully exported data to {output_file}'))
        self.stdout.write(f"Total records exported: {total_count}")
        self.stdout.write(f"Total number of queries: {len(connection.queries)}")

    def _handle_manual_review(self, options):
        output_file = self._get_output_path(options, 'manual_review_export')
        
        filters, filter_type, filter_values = self._get_filter_params(options)
        
        if not filters:
            raise CommandError('Must provide either --batch or --source for manual-review mode')
        
        filters['needs_manual_verification'] = True
        filters['verified'] = False
        
        products = StoreProduct.objects.filter(**filters).select_related('source').values(
            'id', 'site_name', 'manual_verification_reason', 'scrape_batch_id', 'source__name'
        )
        
        if not products.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'No products requiring manual review found for {filter_type}(s) {filter_values}'
                )
            )
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'FLAIME_id', 'product_name', 'automatic_review_reason',
                'batch_id', 'source_name', 'url'
            ])
            
            for product in products:
                writer.writerow([
                    product['id'],
                    product['site_name'],
                    product['manual_verification_reason'] or '',
                    product['scrape_batch_id'],
                    product['source__name'] or '',
                    f"https://flaime.scdc-bio.ca/tools/product-browser/{product['id']}"
                ])
        
        count = products.count()
        self.stdout.write(self.style.SUCCESS(f'Exported {count} products to {output_file}'))

    def _handle_random_sample(self, options):
        output_file = self._get_output_path(options, 'product_sample_export')
        sample_rate = options['sample_rate']
        
        if not 0 < sample_rate <= 1:
            raise CommandError('Sample rate must be between 0 and 1')
        
        filters, filter_type, filter_values = self._get_filter_params(options)
        
        if not filters:
            raise CommandError('Must provide either --batch or --source for random-sample mode')
        
        filters['needs_manual_verification'] = False
        filters['verified'] = False
        
        total_count = StoreProduct.objects.filter(**filters).count()
        
        if total_count == 0:
            self.stdout.write(
                self.style.WARNING(f'No products found for {filter_type}(s) {filter_values}')
            )
            return
        
        sample_size = max(1, int(total_count * sample_rate))
        
        products = StoreProduct.objects.filter(**filters).select_related('source').order_by('?')[:sample_size].values(
            'id', 'site_name', 'scrape_batch_id', 'source__name'
        )
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['FLAIME_id', 'product_name', 'batch_id', 'source_name', 'url'])
            
            for product in products:
                writer.writerow([
                    product['id'],
                    product['site_name'],
                    product['scrape_batch_id'],
                    product['source__name'] or '',
                    f"https://flaime.scdc-bio.ca/tools/product-browser/{product['id']}"
                ])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Exported {sample_size} products ({sample_rate*100:.1f}% of {total_count}) to {output_file}'
            )
        )

    def _handle_snapshot(self, options):
        output_file = self._get_output_path(options, 'product_snapshot')
        
        filters, filter_type, filter_values = self._get_filter_params(options)
        
        if not filters:
            raise CommandError('Must provide either --batch or --source for snapshot mode')
        
        products = StoreProduct.objects.filter(**filters).select_related('source').values(
            'id', 'site_name', 'scrape_batch_id', 'source__name'
        )
        
        total_count = products.count()
        
        if total_count == 0:
            self.stdout.write(
                self.style.WARNING(f'No products found for {filter_type}(s) {filter_values}')
            )
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['FLAIME_id', 'product_name', 'batch_id', 'source_name', 'url'])
            
            for product in products:
                writer.writerow([
                    product['id'],
                    product['site_name'],
                    product['scrape_batch_id'],
                    product['source__name'] or '',
                    f"https://flaime.scdc-bio.ca/tools/product-browser/{product['id']}"
                ])
        
        self.stdout.write(self.style.SUCCESS(f'Exported {total_count} products to {output_file}'))
