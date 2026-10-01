from django.db import migrations, models

"""
`verified` is the only verified flag. verified_nft_ingredients held only 'unknown' plus
'false'/'true' strings written by the old pipeline's boolean bug, so it is dropped.
manual_verification_reason becomes a TextField: QC writes one issue per line.
"""


class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0046_drop_allergens_warnings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storeproduct',
            name='verified_nft_ingredients',
        ),
        migrations.AlterField(
            model_name='storeproduct',
            name='manual_verification_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
