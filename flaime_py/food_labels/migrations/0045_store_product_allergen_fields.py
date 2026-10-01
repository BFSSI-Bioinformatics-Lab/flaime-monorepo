from django.db import migrations, models

"""
Allergen statements move onto store_products. They used to be shared allergens_warnings
rows linked through store_product_allergens_warnings, so correcting one product's
statement changed every product that shared the row.

About 1,700 products have more than one link. Almost all are an original pipeline link
plus the corrected one added by the 2026-01-28 backfill (upload_allergens_warnings.py,
20:00-21:00 UTC), which did not remove the original. One link is kept per product, in
this order:
  1. a link added by hand in the admin (created_by is NULL);
  2. a link from the 2026-01-28 backfill;
  3. any other pipeline link.
Ties go to a link with some text, then to the newest.
Migration 0046 drops the old tables.
"""

COPY_SQL = """
UPDATE store_products sp
SET contains_en = w.contains_en,
    contains_fr = w.contains_fr,
    may_contain_en = w.may_contain_en,
    may_contain_fr = w.may_contain_fr
FROM (
    SELECT DISTINCT ON (l.store_product_id)
           l.store_product_id, a.contains_en, a.contains_fr, a.may_contain_en, a.may_contain_fr
    FROM store_product_allergens_warnings l
    JOIN allergens_warnings a ON a.id = l.allergens_warning_id
    WHERE NOT l.deleted AND NOT a.deleted
    ORDER BY l.store_product_id,
             l.created_by IS NULL DESC,
             l.created_datetime >= '2026-01-28 20:00+00'
                 AND l.created_datetime < '2026-01-28 21:00+00' DESC,
             concat(a.contains_en, a.contains_fr, a.may_contain_en, a.may_contain_fr) <> '' DESC,
             l.created_datetime DESC,
             l.id DESC
) w
WHERE w.store_product_id = sp.id
"""


class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0044_source_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeproduct',
            name='contains_en',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='storeproduct',
            name='contains_fr',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='storeproduct',
            name='may_contain_en',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='storeproduct',
            name='may_contain_fr',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RunSQL(COPY_SQL, migrations.RunSQL.noop),
    ]
