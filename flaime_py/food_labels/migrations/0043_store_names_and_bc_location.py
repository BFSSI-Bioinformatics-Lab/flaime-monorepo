from django.db import migrations

"""
Store names as they appear on the store list (2026-09-25), with the province dropped:
that now lives in store_products.location. The existing stores are renamed and the
missing ones added. The 'NA' and 'Nielsen' placeholders are left as they are.
Also adds British Columbia as a location for future data.
"""

RENAMES = {
    "COSTCO": "Costco",
    "LOBLAWS": "Loblaws",
    "LONGOS": "Longo's",
    "METRO": "Metro",
    "NOFRILLS": "No Frills",
    "PROVIGO": "Provigo",
    "SAVEONFOODS": "Save-On-Foods",
    "VOILA": "Voila",
    "WALMART": "Walmart",
}

NEW_STORES = [
    "Farm Boy",
    "Food Basics",
    "FreshCo",
    "IGA/IGA extra",
    "Maxi & Cie",
    "Sobeys",
    "Super C",
    "Superstore",
]

NEW_LOCATIONS = [("British Columbia", "BC")]


def forwards(apps, schema_editor):
    Store = apps.get_model("food_labels", "Store")
    Location = apps.get_model("food_labels", "Location")
    for old, new in RENAMES.items():
        if not Store.objects.filter(name=new, deleted=False).exists():
            Store.objects.filter(name=old, deleted=False).update(name=new, modified_by="migration")
    for name in NEW_STORES:
        Store.objects.get_or_create(
            name=name, deleted=False,
            defaults={"created_by": "migration", "modified_by": "migration"},
        )
    for name, code in NEW_LOCATIONS:
        Location.objects.get_or_create(
            code=code, deleted=False,
            defaults={"name": name, "created_by": "migration", "modified_by": "migration"},
        )


def backwards(apps, schema_editor):
    Store = apps.get_model("food_labels", "Store")
    Location = apps.get_model("food_labels", "Location")
    for code in (code for _, code in NEW_LOCATIONS):
        Location.objects.filter(code=code, created_by="migration", storeproduct__isnull=True).delete()
    Store.objects.filter(name__in=NEW_STORES, created_by="migration",
                         storeproduct__isnull=True, batch__isnull=True).delete()
    for old, new in RENAMES.items():
        Store.objects.filter(name=new, deleted=False).update(name=old)


class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0042_drop_duplicate_foreign_keys'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
