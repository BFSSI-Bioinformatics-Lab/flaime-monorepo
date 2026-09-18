from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('food_labels', '0017_add_ra_and_suppfood_flag'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManualProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('problematic_flag', models.BooleanField(default=False)),
                ('category', models.ForeignKey(on_delete=models.CASCADE, to='food_labels.category')),
                ('product', models.ForeignKey(on_delete=models.CASCADE, to='food_labels.product')),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Manual Product Category',
                'verbose_name_plural': 'Manual Product Categories',
                'db_table': 'manual_product_categories',
            },
        ),
        migrations.CreateModel(
            name='PredictedProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_id', models.CharField(max_length=256)),
                ('date_predicted', models.DateTimeField(auto_now_add=True)),
                ('confidence', models.FloatField()),
                ('category', models.ForeignKey(on_delete=models.CASCADE, to='food_labels.category')),
                ('product', models.ForeignKey(on_delete=models.CASCADE, to='food_labels.product')),
            ],
            options={
                'verbose_name': 'Predicted Product Category',
                'verbose_name_plural': 'Predicted Product Categories',
                'db_table': 'predicted_product_categories',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='manual_categories',
            field=models.ManyToManyField(related_name='manually_categorized_products', through='food_labels.ManualProductCategory', to='food_labels.category'),
        ),
        migrations.AddField(
            model_name='product',
            name='predicted_categories',
            field=models.ManyToManyField(related_name='predicted_products', through='food_labels.PredictedProductCategory', to='food_labels.category'),
        ),
    ]