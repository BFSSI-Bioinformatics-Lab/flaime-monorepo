from django.db import migrations


def migrate_subcategories(apps, schema_editor):
    Category = apps.get_model('food_labels', 'Category')
    Subcategory = apps.get_model('food_labels', 'Subcategory')

    # Update existing categories to level 1
    Category.objects.all().update(level=1)

    # Migrate subcategories to categories
    for subcategory in Subcategory.objects.all():
        Category.objects.create(
            name=subcategory.name,
            code=subcategory.code,
            scheme=subcategory.category.scheme,
            parent_category=subcategory.category,
            level=2,
            created_datetime=subcategory.created_datetime,
            created_by=subcategory.created_by,
            modified_datetime=subcategory.modified_datetime,
            modified_by=subcategory.modified_by,
            deleted_datetime=subcategory.deleted_datetime,
            deleted_by=subcategory.deleted_by,
            deleted=subcategory.deleted
        )


class Migration(migrations.Migration):
    dependencies = [
        ("food_labels", "0004_remove_category_indices"),
    ]

    operations = [
        migrations.RunPython(migrate_subcategories),
    ]
