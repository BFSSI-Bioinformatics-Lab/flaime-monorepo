from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Q, Exists, OuterRef


class Command(BaseCommand):
    help = 'Assigns parent categories to products that have level 2 categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without executing',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            default=1,
            help='User ID to assign to new records (default: 1)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        user_id = options['user_id']

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    mpc.product_id,
                    c.parent_category_id as category_id_to_insert,
                    pc.name as parent_category_name,
                    c.name as source_child_category
                FROM manual_product_categories mpc
                JOIN categories c ON mpc.category_id = c.id
                JOIN categories pc ON c.parent_category_id = pc.id
                WHERE c.level = 2
                    AND c.parent_category_id IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 
                        FROM manual_product_categories mpc2
                        WHERE mpc2.product_id = mpc.product_id
                            AND mpc2.category_id = c.parent_category_id
                    )
                ORDER BY mpc.product_id, c.parent_category_id
            """)
            
            rows = cursor.fetchall()
            
            if not rows:
                self.stdout.write(self.style.SUCCESS('No parent categories need to be assigned'))
                return

            self.stdout.write(f'Found {len(rows)} parent categories to assign:')
            
            for product_id, category_id, parent_name, child_name in rows[:10]:
                self.stdout.write(
                    f'  Product {product_id}: {parent_name} (from child: {child_name})'
                )
            
            if len(rows) > 10:
                self.stdout.write(f'  ... and {len(rows) - 10} more')

            if dry_run:
                self.stdout.write(self.style.WARNING('\nDry run mode - no changes made'))
                return

            cursor.execute("""
                INSERT INTO manual_product_categories (product_id, category_id, user_id, problematic_flag, date_added, notes)
                SELECT DISTINCT
                    mpc.product_id,
                    c.parent_category_id,
                    %s,
                    false,
                    NOW(),
                    'Auto-assigned parent category'
                FROM manual_product_categories mpc
                JOIN categories c ON mpc.category_id = c.id
                WHERE c.level = 2
                    AND c.parent_category_id IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 
                        FROM manual_product_categories mpc2
                        WHERE mpc2.product_id = mpc.product_id
                            AND mpc2.category_id = c.parent_category_id
                    )
            """, [user_id])
            
            inserted = cursor.rowcount
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully assigned {inserted} parent categories')
            )