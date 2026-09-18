from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps
from django.db import models


class Command(BaseCommand):
    help = 'Check foreign key constraints in the database against Django models'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Query to get foreign key information from PostgreSQL
            cursor.execute("""
                SELECT
                    tc.table_name, kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    rc.delete_rule
                FROM
                    information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                    JOIN information_schema.referential_constraints AS rc
                      ON rc.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
            """)
            db_fks = cursor.fetchall()

        for table_name, column_name, foreign_table_name, foreign_column_name, delete_rule in db_fks:
            # Find the corresponding Django model and field
            model = next((m for m in apps.get_models() if m._meta.db_table == table_name), None)

            if model:
                field = next((f for f in model._meta.fields if f.column == column_name and isinstance(f, models.ForeignKey)), None)
                if field:
                    # Check if the on_delete behavior matches
                    django_delete_rule = self.get_django_delete_rule(field.remote_field.on_delete)
                    if django_delete_rule != delete_rule:
                        self.stdout.write(self.style.WARNING(
                            f"Mismatch in {model.__name__}.{field.name}: "
                            f"Django uses {django_delete_rule}, DB uses {delete_rule}"
                        ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"Foreign key {column_name} in table {table_name} not found in Django model {model.__name__}"
                    ))
            else:
                self.stdout.write(self.style.ERROR(f"Model for table {table_name} not found"))

    def get_django_delete_rule(self, on_delete):
        if on_delete == models.CASCADE:
            return 'CASCADE'
        elif on_delete == models.RESTRICT:
            return 'RESTRICT'
        elif on_delete == models.SET_NULL:
            return 'SET NULL'
        elif on_delete == models.PROTECT:
            return 'RESTRICT'  # PROTECT in Django is similar to RESTRICT in PostgreSQL
        elif on_delete == models.SET_DEFAULT:
            return 'SET DEFAULT'
        elif on_delete == models.DO_NOTHING:
            return 'NO ACTION'
        else:
            return 'UNKNOWN'
