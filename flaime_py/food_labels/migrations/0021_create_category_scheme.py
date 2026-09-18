from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("food_labels", "0020_remove_old_categories"),
    ]
    
    operations = [
        migrations.CreateModel(
            name="CategoryScheme",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Category Scheme",
                "verbose_name_plural": "Category Schemes",
                "db_table": "category_schemes",
                "managed": True,
            },
        ),
        migrations.AlterModelOptions(
            name="manualproductcategory",
            options={
                "verbose_name": "Manually Verified Category",
                "verbose_name_plural": "Manually Verified Categories",
            },
        ),
        migrations.AlterField(
            model_name="manualproductcategory",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="predictedproductcategory",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]