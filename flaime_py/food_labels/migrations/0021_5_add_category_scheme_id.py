from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("food_labels", "0021_create_category_scheme"),
    ]
    operations = [
        migrations.AddField(
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