import django.db.models.deletion
from django.db import migrations, models

"""
Ingest runs replace scrape batches.

ingest_runs records each run of the flaime-ingress pipeline, and ingest_attempts
what happened to each fanddaf product in it. Every scrape batch becomes an ingest
run with the same id and date, and its products point to that run, so products
keep their date (search sorts and filters by it) and their grouping (export --run).
A batch's store and region are already on its products (store_products.store_id,
location_id); any region not yet carried to location is copied before the table
is dropped. Batch counts and notes were pipeline bookkeeping; the notes go into
the run's command.
"""

# scrape_batches.region -> locations.code, as in nutrient-migration's finalize.
REGIONS = "('ON', 'ON'), ('ONTARIO', 'ON'), ('QC', 'QC'), ('QUEBEC', 'QC'), ('BC', 'BC'), ('BRITISH COLUMBIA', 'BC')"

BATCHES_TO_RUNS = f"""
-- Check the deferred foreign keys now: the ALTER TABLEs that follow refuse to run
-- while trigger events from these updates are still pending.
SET CONSTRAINTS ALL IMMEDIATE;

UPDATE store_products sp SET location_id = l.id
FROM scrape_batches b
JOIN (VALUES {REGIONS}) r(region, code) ON r.region = upper(btrim(b.region))
JOIN locations l ON l.code = r.code AND NOT l.deleted
WHERE sp.scrape_batch_id = b.id AND sp.location_id IS NULL;

INSERT INTO ingest_runs (id, created_datetime, created_by, modified_datetime, modified_by,
                         deleted_datetime, deleted_by, deleted,
                         started, finished, status, command, eligible, loaded, skipped, failed)
SELECT b.id, b.created_datetime, b.created_by, b.modified_datetime, b.modified_by,
       b.deleted_datetime, b.deleted_by, b.deleted,
       b.scrape_datetime, b.scrape_datetime, 'succeeded',
       left(COALESCE('scrape batch: ' || NULLIF(btrim(b.notes), ''), 'scrape batch'), 512),
       0, (SELECT COUNT(*) FROM store_products sp WHERE sp.scrape_batch_id = b.id), 0, 0
FROM scrape_batches b;

UPDATE store_products SET ingest_run_id = scrape_batch_id WHERE scrape_batch_id IS NOT NULL;

SELECT setval(pg_get_serial_sequence('ingest_runs', 'id'), GREATEST((SELECT MAX(id) FROM ingest_runs), 1));
"""


class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0048_serving_size_float'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngestRun',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(blank=True, max_length=256, null=True)),
                ('modified_datetime', models.DateTimeField(auto_now=True)),
                ('modified_by', models.CharField(blank=True, max_length=256, null=True)),
                ('deleted_datetime', models.DateTimeField(blank=True, null=True)),
                ('deleted_by', models.CharField(blank=True, max_length=256, null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('started', models.DateTimeField()),
                ('finished', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('running', 'Running'), ('succeeded', 'Succeeded'), ('failed', 'Failed')], default='running', max_length=16)),
                ('command', models.CharField(max_length=512)),
                ('code_version', models.CharField(blank=True, max_length=64, null=True)),
                ('eligible', models.IntegerField(default=0)),
                ('loaded', models.IntegerField(default=0)),
                ('skipped', models.IntegerField(default=0)),
                ('failed', models.IntegerField(default=0)),
                ('error', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'ingest_runs',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='IngestAttempt',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(blank=True, max_length=256, null=True)),
                ('modified_datetime', models.DateTimeField(auto_now=True)),
                ('modified_by', models.CharField(blank=True, max_length=256, null=True)),
                ('deleted_datetime', models.DateTimeField(blank=True, null=True)),
                ('deleted_by', models.CharField(blank=True, max_length=256, null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('fanddaf_id', models.BigIntegerField(db_index=True)),
                ('outcome', models.CharField(choices=[('loaded', 'Loaded'), ('skipped', 'Skipped'), ('failed', 'Failed')], max_length=16)),
                ('stage', models.CharField(max_length=32)),
                ('message', models.TextField(blank=True, null=True)),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='food_labels.ingestrun')),
            ],
            options={
                'db_table': 'ingest_attempts',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='storeproduct',
            name='ingest_run',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='store_products', to='food_labels.ingestrun'),
        ),
        migrations.RunSQL(BATCHES_TO_RUNS),
        migrations.RemoveField(
            model_name='storeproduct',
            name='scrape_batch',
        ),
        migrations.DeleteModel(
            name='Batch',
        ),
    ]
