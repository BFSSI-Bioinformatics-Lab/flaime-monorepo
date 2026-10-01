from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0045_store_product_allergen_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storeproduct',
            name='allergens_warnings',
        ),
        migrations.DeleteModel(
            name='StoreProductAllergensWarning',
        ),
        migrations.DeleteModel(
            name='AllergensWarning',
        ),
    ]
