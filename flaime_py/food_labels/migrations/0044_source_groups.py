import django.db.models.deletion
from django.db import migrations, models

"""
Source groups: where a collection came from (Nielsen, FLIP, Total Diet Study, Label
Collection). The app labels a Source "Collection" and a SourceGroup "Source".
Also makes the label-collection names match the fanddaf batch labels exactly, since
flaime-ingress matches a fanddaf batch to its source by name; names FLIP by its year like
Nielsen; and adds the collections that are new in fanddaf (2026 Total Diet Study,
2026 Shelf Stable Sides and Entrees Collection).
"""

RENAMES = {
    "FLIP": "FLIP 2017",
    "2025 Frozen Entree collection": "2025 Frozen Entrees Collection",
    "2025 Supp food collection": "2025 Supplemented Food Collection",
}

NEW_SOURCES = ["2026 Total Diet Study", "2026 Shelf Stable Sides and Entrees Collection"]

# Sources not listed here (e.g. "Web Scrape") get no group.
GROUPS = {
    "FLIP": ["FLIP 2017"],
    "Nielsen": ["Nielsen 2017"],
    "Total Diet Study": ["2025 Total Diet Study", "2026 Total Diet Study"],
    "Label Collection": [
        "2025 Frozen Entrees Collection",
        "2025 Supplemented Food Collection",
        "2026 Baked Goods Collection",
        "SNAP-CAN 2025",
        "2026 Snack Foods Collection",
        "2026 Frozen and Refrigerated Appetizers Collection",
        "2026 Refrigerated Sides and Entrees Collection",
        "2026 Meat and Alternatives Collection",
        "2026 Fish and Seafood Collection",
        "2026 Shelf Stable Sides and Entrees Collection",
    ],
}


def forwards(apps, schema_editor):
    Source = apps.get_model("food_labels", "Source")
    SourceGroup = apps.get_model("food_labels", "SourceGroup")
    for old, new in RENAMES.items():
        if not Source.objects.filter(name=new, deleted=False).exists():
            Source.objects.filter(name=old, deleted=False).update(name=new, modified_by="migration")
    for name in NEW_SOURCES:
        Source.objects.get_or_create(
            name=name, deleted=False,
            defaults={"created_by": "migration", "modified_by": "migration"},
        )
    for group_name, source_names in GROUPS.items():
        group, _ = SourceGroup.objects.get_or_create(
            name=group_name, deleted=False,
            defaults={"created_by": "migration", "modified_by": "migration"},
        )
        Source.objects.filter(name__in=source_names, deleted=False).update(group=group)


def backwards(apps, schema_editor):
    Source = apps.get_model("food_labels", "Source")
    Source.objects.filter(name__in=NEW_SOURCES, created_by="migration", storeproduct__isnull=True).delete()
    for old, new in RENAMES.items():
        Source.objects.filter(name=new, deleted=False).update(name=old)


class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0043_store_names_and_bc_location'),
    ]

    operations = [
        migrations.CreateModel(
            name='SourceGroup',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(blank=True, max_length=256, null=True)),
                ('modified_datetime', models.DateTimeField(auto_now=True)),
                ('modified_by', models.CharField(blank=True, max_length=256, null=True)),
                ('deleted_datetime', models.DateTimeField(blank=True, null=True)),
                ('deleted_by', models.CharField(blank=True, max_length=256, null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name': 'Source',
                'verbose_name_plural': 'Sources',
                'db_table': 'source_groups',
                'managed': True,
                'unique_together': {('name', 'deleted')},
            },
        ),
        migrations.AddField(
            model_name='source',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='food_labels.sourcegroup', verbose_name='Source'),
        ),
        migrations.AlterModelOptions(
            name='source',
            options={'managed': True, 'verbose_name': 'Collection', 'verbose_name_plural': 'Collections'},
        ),
        migrations.AlterField(
            model_name='storeproduct',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='food_labels.source', verbose_name='Collection'),
        ),
        migrations.RunPython(forwards, backwards),
    ]
