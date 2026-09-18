from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('food_labels', '0019_migrate_categories'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='categories',
        ),
    ]