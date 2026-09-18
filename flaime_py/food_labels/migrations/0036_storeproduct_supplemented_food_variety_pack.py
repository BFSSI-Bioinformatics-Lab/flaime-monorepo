"""Restore the two Product flags the FSDH migration scripts dropped on the floor.

migrate.py backfilled ingredient_en/ingredient_fr from products onto
store_products and preserved the category labels, but it dropped `products`
without carrying over `supplemented_food` or `variety_pack_flag`. Both are still
used by the app: supplemented_food drives the supplemented-food display in
flaime-2.0, the `--supplemented-food` flag on import_store_products and the
barcode lookup in load_supplemented_nft; variety_pack_flag is a column in the
export CSV.

Unlike 0035 these changes were NOT made by the migration scripts, so run this one
for real against the FSDH database. It adds the columns empty (default false) —
the values themselves are backfilled separately by nutrient-migration/phase4.py,
which reads them from the source database (that one still has products).

The RunSQL step drops the leftover store_products.product_id column: migrate.py
NULLed it but never dropped it, so it survives on the FSDH database. On a fresh
database 0035 has already removed it and the IF EXISTS makes this a no-op.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0035_fsdh_schema'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeproduct',
            name='supplemented_food',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='storeproduct',
            name='variety_pack_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.RunSQL(
            sql='ALTER TABLE store_products DROP COLUMN IF EXISTS product_id;',
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
