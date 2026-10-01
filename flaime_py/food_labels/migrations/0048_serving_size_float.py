from django.db import migrations, models

"""
serving_size becomes a float: labels print sizes like 8.3 g, which an integer column truncated.
Existing integers convert exactly.
"""


class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0047_drop_verified_nft_ingredients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storeproduct',
            name='serving_size',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
