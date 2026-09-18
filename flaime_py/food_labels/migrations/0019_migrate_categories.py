from django.db import migrations
from django.utils import timezone
from django.conf import settings


def migrate_category_data(apps, schema_editor):
    Product = apps.get_model('food_labels', 'Product')
    ManualProductCategory = apps.get_model('food_labels', 'ManualProductCategory')
    User = apps.get_model(settings.AUTH_USER_MODEL.split('.')[0], settings.AUTH_USER_MODEL.split('.')[1])

    system_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
    
    if not system_user:
        raise Exception("No users found in the database to associate with historical category data")

    batch_size = 1000
    product_ids = Product.objects.values_list('id', flat=True)
    total_products = len(product_ids)

    for start in range(0, total_products, batch_size):
        end = min(start + batch_size, total_products)
        batch_ids = product_ids[start:end]
        products_batch = Product.objects.filter(id__in=batch_ids)
        
        manual_categories = []
        for product in products_batch:
            for category in product.categories.all():
                manual_categories.append(
                    ManualProductCategory(
                        product=product,
                        category=category,
                        user=system_user,
                        date_added=timezone.now(),
                        problematic_flag=False
                    )
                )
        
        if manual_categories:
            ManualProductCategory.objects.bulk_create(manual_categories)
            print(f"Migrated categories for products {start} to {end} of {total_products}")


def reverse_migrate_category_data(apps, schema_editor):
    Product = apps.get_model('food_labels', 'Product')
    ManualProductCategory = apps.get_model('food_labels', 'ManualProductCategory')

    batch_size = 1000
    for i in range(0, ManualProductCategory.objects.count(), batch_size):
        batch = ManualProductCategory.objects.all()[i:i + batch_size]
        for manual_cat in batch:
            manual_cat.product.categories.add(manual_cat.category)
        print(f"Reversed migration for batch starting at {i}")

class Migration(migrations.Migration):
    dependencies = [
        ('food_labels', '0018_add_new_predicted_manual_categories'),
    ]

    operations = [
        migrations.RunPython(
            migrate_category_data,
            reverse_migrate_category_data
        )
    ]