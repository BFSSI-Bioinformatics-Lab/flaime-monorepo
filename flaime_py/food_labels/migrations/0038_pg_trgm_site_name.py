"""Trigram search support for store_products.site_name.

`pg_trgm` accelerates the case-insensitive substring match used by
`POST /api/storeproducts/search/` (site_name ILIKE '%term%').

The extension is created with IF NOT EXISTS, so it is a harmless no-op where a
DBA has already enabled it (e.g. the Azure production database).  The index is
built CONCURRENTLY, so this migration is not atomic.

Kept out of `StoreProduct.Meta.indexes` on purpose: the test suite builds its
schema with `--no-migrations` (from model state) against a database that may not
have `pg_trgm`, and search correctness only needs plain ILIKE, not the index.
"""

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("food_labels", "0037_merge_20260831_1347"),
    ]

    operations = [
        TrigramExtension(),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS "
                "store_products_site_name_trgm "
                "ON store_products USING gin (site_name gin_trgm_ops);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS store_products_site_name_trgm;"
            ),
        ),
    ]
