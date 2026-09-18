from django.db import migrations


def verify_post_migration():
    from django.db import connection
    
    with connection.cursor() as cursor:
        # After migration, every category should have a scheme
        # This query checks if any were missed
        cursor.execute("""
            SELECT COUNT(*) 
            FROM categories
            WHERE scheme_id IS NULL
        """)
        categories_without_scheme = cursor.fetchone()[0]
        
        # This checks if any product-category relationships are broken
        # Important because we're changing foreign key relationships
        cursor.execute("""
            SELECT COUNT(*) 
            FROM manual_product_categories mpc
            LEFT JOIN products p ON mpc.product_id = p.id
            WHERE p.id IS NULL
        """)
        broken_references = cursor.fetchone()[0]
        
        return {
            'categories_without_scheme': categories_without_scheme,
            'broken_references': broken_references
        }


def migrate_category_data(apps, schema_editor):
    # Get your models
    CategoryScheme = apps.get_model('food_labels', 'CategoryScheme')
    Category = apps.get_model('food_labels', 'Category')
    
    # Create default scheme
    default_scheme, created = CategoryScheme.objects.get_or_create(
        name='Default',
        description='Legacy category scheme'
    )
    
    # Update categories in batches to avoid memory issues
    for batch in Category.objects.iterator(chunk_size=1000):
        if batch.scheme is None:
            batch.scheme = default_scheme
            batch.save()
    
    # Run post-migration checks
    post_check = verify_post_migration()
    if post_check['categories_without_scheme'] > 0:
        raise Exception("Migration failed: found categories without schemes")


class Migration(migrations.Migration):
    dependencies = [
        ("food_labels", "0021_5_add_category_scheme_id"),
    ]
    
    operations = [
        migrations.RunPython(migrate_category_data, migrations.RunPython.noop),
    ]