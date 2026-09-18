from django.db import migrations

def update_fk_constraints(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        # List of all constraints to update
        constraints = [
            ('companies', 'FK_companies_companies_parent_id'),
            ('nutrients', 'FK_nutrients_nutrients_parent_id'),
            ('product_nutrition_facts', 'FK_product_nutrition_facts_nutrients_nutrient_id'),
            ('product_nutrition_facts', 'FK_product_nutrition_facts_products_product_id'),
            ('product_nutrition_facts', 'FK_product_nutrition_facts_units_amount_unit_id'),
            ('product_profiles', 'FK_product_profiles_brands_brand_id'),
            ('product_profiles', 'FK_product_profiles_companies_company_id'),
            ('product_profiles', 'FK_product_profiles_manufacturers_manufacturer_id'),
            ('product_profiles', 'FK_product_profiles_sources_source_id'),
            ('product_upcs', 'FK_product_upcs_products_product_id'),
            ('product_upcs', 'FK_product_upcs_upcs_upc_id'),
            ('products', 'FK_products_brands_brand_id'),
            ('products', 'FK_products_product_profiles_product_profile_id'),
            ('products', 'FK_products_products_parent_id'),
            ('products', 'FK_products_sources_source_id'),
            ('products', 'FK_products_units_serving_size_unit_id'),
            ('products', 'FK_products_units_total_size_unit_id'),
            ('scrape_batches', 'FK_scrape_batches_stores_store_id'),
            ('store_product_allergens_warnings', 'FK_store_product_allergens_warnings_allergens_warnings_allergens_warning_id'),
            ('store_product_allergens_warnings', 'FK_store_product_allergens_warnings_store_products_store_product_id'),
            ('store_product_dietary_infos', 'FK_store_product_dietary_infos_dietary_informations_dietary_information_id'),
            ('store_product_dietary_infos', 'FK_store_product_dietary_infos_store_products_store_product_id'),
            ('store_product_nutrition_facts', 'FK_store_product_nutrition_facts_nutrients_nutrient_id'),
            ('store_product_nutrition_facts', 'FK_store_product_nutrition_facts_store_products_store_product_id'),
            ('store_product_nutrition_facts', 'FK_store_product_nutrition_facts_units_amount_unit_id'),
            ('store_products', 'FK_store_products_bread_crumbs_bread_crumb_id'),
            ('store_products', 'FK_store_products_price_units_price_unit_id'),
            ('store_products', 'FK_store_products_products_product_id'),
            ('store_products', 'FK_store_products_scrape_batches_scrape_batch_id'),
            ('store_products', 'FK_store_products_sources_source_id'),
            ('store_products', 'FK_store_products_storages_storage_id'),
            ('store_products', 'FK_store_products_stores_store_id'),
            ('store_products', 'FK_store_products_units_serving_size_unit_id'),
            ('store_report_data', 'FK_store_report_data_stores_store_id'),
            ('upcs', 'FK_upcs_companies_company_id'),
            ('store_product_images', 'fk_store_product_images_store_products_store_product_id'),
        ]

        for table, constraint in constraints:
            # Get the current foreign key definition
            cursor.execute(f"""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_name = %s
                  AND tc.table_name = %s;
            """, [constraint, table])
            
            result = cursor.fetchone()
            if result:
                column, foreign_table, foreign_column = result
                # Alter the constraint
                cursor.execute(f"""
                    ALTER TABLE {table}
                    DROP CONSTRAINT IF EXISTS {constraint},
                    ADD CONSTRAINT {constraint}
                    FOREIGN KEY ({column})
                    REFERENCES {foreign_table}({foreign_column})
                    ON DELETE CASCADE;
                """)
                print(f"Updated constraint {constraint} on table {table}")
            else:
                print(f"Constraint {constraint} not found on table {table}")

class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0015_modify_bullets_constraints_directly'),
    ]

    operations = [
        migrations.RunPython(update_fk_constraints),
    ]