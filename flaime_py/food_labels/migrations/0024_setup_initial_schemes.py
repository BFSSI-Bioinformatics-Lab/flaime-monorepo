from django.db import migrations


def create_schemes_and_link(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE categories 
            SET scheme_id = schemes.id
            FROM (
                SELECT id, name 
                FROM category_schemes
                WHERE name IN ('reference amount', 'Sodium')
            ) as schemes
            WHERE categories.scheme = schemes.name
        """)


def reverse_scheme_setup(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE categories
            SET scheme = schemes.name
            FROM category_schemes as schemes
            WHERE categories.scheme_id = schemes.id
        """)


class Migration(migrations.Migration):
    dependencies = [
        ('food_labels', '0023_update_category_relationships'),
    ]
    
    operations = [
        migrations.RunSQL(
            """
            INSERT INTO category_schemes (name, description)
            VALUES 
                ('reference amount', 'Reference amount categories'),
                ('Sodium', 'Sodium-related categories')
            """
        ),
        migrations.RunPython(create_schemes_and_link, reverse_scheme_setup)
    ]