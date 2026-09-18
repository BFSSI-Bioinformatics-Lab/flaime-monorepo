from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0003_category_level_category_parent_category'),  # Make sure this is the correct previous migration
    ]

    operations = [
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS "IX_categories_name_scheme";',
            reverse_sql='CREATE UNIQUE INDEX "IX_categories_name_scheme" ON public.categories USING btree (name, scheme);'
        ),
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS "IX_categories_code_scheme";',
            reverse_sql='CREATE UNIQUE INDEX "IX_categories_code_scheme" ON public.categories USING btree (code, scheme);'
        ),
    ]
