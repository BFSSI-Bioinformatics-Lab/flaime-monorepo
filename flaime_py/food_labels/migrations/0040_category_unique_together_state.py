from django.db import migrations

"""
0001_initial declared unique_together {(code, scheme), (name, scheme)} on Category.
Those constraints were never in the database (it predates this app), and the model no
longer declares them, so makemigrations keeps generating AlterUniqueTogether(set()),
which fails because there is nothing to drop. This records the change in Django's
state only; the database is left alone. (name, scheme) has legitimate duplicates.
"""


class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0039_store_product_location_and_sizes'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterUniqueTogether(name='category', unique_together=set()),
            ],
            database_operations=[],
        ),
    ]
