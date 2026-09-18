from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("food_labels", "0022_migrate_category_data"),
    ]
    
    operations = [
        migrations.RemoveField(
            model_name="product",
            name="manual_categories",
        ),
        migrations.RemoveField(
            model_name="product",
            name="predicted_categories",
        ),
        migrations.AlterField(
            model_name="manualproductcategory",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="manual_categories",
                to="food_labels.product",
            ),
        ),
        migrations.AlterField(
            model_name="predictedproductcategory",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="predicted_categories",
                to="food_labels.product",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="scheme",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="food_labels.categoryscheme",
            ),
        ),
    ]