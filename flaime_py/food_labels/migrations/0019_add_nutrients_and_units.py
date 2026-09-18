from django.db import migrations


def add_missing_nutrients_and_units(apps, schema_editor):
    Nutrient = apps.get_model('food_labels', 'Nutrient')
    Unit = apps.get_model('food_labels', 'Unit')

    # Add missing units
    new_units = [
        {
            'name': 'ug DFE',
            'description': 'Micrograms Dietary Folate Equivalent',
            'created_by': 'data_migration'
        },

    ]

    for unit_data in new_units:
        existing_unit = Unit.objects.filter(name=unit_data['name']).first()
        if not existing_unit:
            Unit.objects.create(**unit_data)

    missing_nutrients = [
        {
            'nutrient_code': 0,
            'name': 'TAURINE',
            'symbol': 'Taurine',
            'created_by': 'data_migration'
        }
    ]

    # Create missing nutrients
    for idx, nutrient_data in enumerate(missing_nutrients):

        # Check if nutrient already exists
        existing = Nutrient.objects.filter(name=nutrient_data['name']).first()
        if not existing:
            Nutrient.objects.create(**nutrient_data)


def remove_added_data(apps, schema_editor):
    Nutrient = apps.get_model('food_labels', 'Nutrient')
    Unit = apps.get_model('food_labels', 'Unit')

    # Remove the nutrients and units added by this migration
    Nutrient.objects.filter(name='TAURINE').delete()
    Unit.objects.filter(name='ug DFE').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0018_denote_supplemented_nutrition_facts'),
    ]

    operations = [
        migrations.RunPython(add_missing_nutrients_and_units, remove_added_data),
    ]
