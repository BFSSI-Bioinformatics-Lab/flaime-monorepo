from django.db import models
from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver


class VerifiedNftIngredients(models.TextChoices):
    UNKNOWN = 'unknown', ('Unknown')
    MANUALLY_ENTERED = 'manually_entered', ('Manually Entered')
    OCR_VERIFIED = 'ocr_verified', ('OCR (Manually Verified)')
    OCR_UNVERIFIED = 'ocr_unverified', ('OCR (Unverified)')
    EXTERNAL = 'external', ('External')


class StorageConditions(models.TextChoices):
    SHELF_STABLE = "shelf_stable", ("Shelf Stable")
    FRIDGE = "fridge", ("Fridge")
    FREEZER = "freezer", ("Freezer")


class PackagingChoices(models.TextChoices):
    GLASS = "glass", ("Glass")
    METAL = "metal", ("Metal")
    PAPER = "paper", ("Paper/paperboard")
    PLASTIC_PET = "plastic_pet", ("Plastic - PET - 1")
    PLASTIC_HDPE = "plastic_hdpe", ("Plastic - HDPE - 2")
    PLASTIC_PVC = "plastic_pvc", ("Plastic - PVC - 3")
    PLASTIC_LDPE = "plastic_ldpe", ("Plastic - LDPE - 4")
    PLASTIC_PP = "plastic_pp", ("Plastic - PP - 5")
    PLASTIC_PS = "plastic_ps", ("Plastic - PS - 6")
    PLASTIC_OTHER = "plastic_other", ("Plastic - OTHER - 7")
    PLASTIC_UNKNOWN = "plastic_unknown", ("Plastic - Unknown")
    OTHER = "other", ("Other")


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=256, blank=True, null=True)
    modified_datetime = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=256, blank=True, null=True)
    deleted_datetime = models.DateTimeField(blank=True, null=True)
    deleted_by = models.CharField(max_length=256, blank=True, null=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
        app_label = "food_labels"


class AllergensWarning(BaseModel):
    contains_en = models.TextField(blank=True, null=True)
    contains_fr = models.TextField(blank=True, null=True)
    may_contain_en = models.TextField(blank=True, null=True)
    may_contain_fr = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'allergens_warnings'
        verbose_name = 'Allergens Warning'
        verbose_name_plural = 'Allergens Warnings'
        # Removed unique_allergen_combination constraint: NULLs in the four
        # fields aren't treated as equal by Postgres, so it wasn't actually
        # preventing duplicates for rows with any null field. Existing data
        # has duplicates from this. Need to clean up dupes and pick a real
        # dedup strategy (e.g. normalize NULL -> '') before re-adding.
        #constraints = [
        #    models.UniqueConstraint(
        #        fields=['contains_en', 'contains_fr', 'may_contain_en', 'may_contain_fr'],
        #        name='unique_allergen_combination'
        #    )
        # ]

    def __str__(self):
        parts = []
        if self.contains_en:
            parts.append(f"Contains: {self.contains_en}")
        if self.may_contain_en:
            parts.append(f"May contain: {self.may_contain_en}")
        return "; ".join(parts) if parts else "No allergen info"



class Brand(BaseModel):
    name = models.CharField(max_length=512)

    class Meta:
        managed = True
        db_table = 'brands'
        unique_together = (('name', 'deleted'),)
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return self.name


class Bullet(BaseModel):
    description = models.CharField(unique=True, max_length=10240)

    class Meta:
        managed = True
        db_table = 'bullets'
        verbose_name = 'Bullet'
        verbose_name_plural = 'Bullets'

    def __str__(self):
        return self.description


class CategoryScheme(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'category_schemes'
        verbose_name = 'Category Scheme'
        verbose_name_plural = 'Category Schemes'

    def __str__(self):
        return self.name


class Category(BaseModel):
    name = models.CharField(max_length=512)
    code = models.CharField(max_length=256)
    scheme = models.ForeignKey(CategoryScheme, null=True, blank=True, on_delete=models.CASCADE)
    parent_category = models.ForeignKey('self', models.CASCADE, null=True, blank=True, related_name='children')
    level = models.PositiveIntegerField(default=1)
    deleted = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.code} - {self.name}"


class Company(BaseModel):
    name = models.CharField(unique=True, max_length=512)
    parent = models.ForeignKey('self', models.CASCADE, related_name='children', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'companies'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name


class DietaryInformation(BaseModel):
    description = models.CharField(unique=True, max_length=10240)

    class Meta:
        managed = True
        db_table = 'dietary_informations'
        verbose_name = 'Dietary Information'
        verbose_name_plural = 'Dietary Information'

    def __str__(self):
        return self.description


class Nutrient(BaseModel):
    nutrient_code = models.IntegerField(unique=True)
    name = models.CharField(unique=True, max_length=256)
    symbol = models.CharField(max_length=256)
    usda_nutrient_code = models.IntegerField(blank=True, null=True)
    parent = models.ForeignKey('self', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'nutrients'
        verbose_name = 'Nutrient'
        verbose_name_plural = 'Nutrients'

    def __str__(self):
        return self.name


class StoreProductUPC(BaseModel):
    # store_product_upcs replaces product_upcs: UPCs now hang off the store
    # product directly, since products was dropped in the FSDH migration.
    id = models.AutoField(primary_key=True)
    store_product = models.ForeignKey('StoreProduct', models.CASCADE)
    upc = models.ForeignKey('UPC', models.CASCADE)

    class Meta:
        managed = True
        db_table = 'store_product_upcs'
        unique_together = (('store_product', 'upc'),)
        verbose_name = 'SP UPC'
        verbose_name_plural = 'SP UPCs'


class StoreProductManualCategory(models.Model):
    id = models.AutoField(primary_key=True)
    store_product = models.ForeignKey('StoreProduct', models.CASCADE, related_name='manual_categories')
    category = models.ForeignKey('Category', models.CASCADE)
    user = models.ForeignKey('users.User', models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    problematic_flag = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default='')

    class Meta:
        managed = True
        db_table = 'store_product_manual_categories'
        verbose_name = 'Manually Verified Category'
        verbose_name_plural = 'Manually Verified Categories'


class StoreProductPredictedCategory(models.Model):
    id = models.AutoField(primary_key=True)
    store_product = models.ForeignKey('StoreProduct', models.CASCADE, related_name='predicted_categories')
    category = models.ForeignKey('Category', models.CASCADE)
    model_id = models.CharField(max_length=256)
    date_predicted = models.DateTimeField(auto_now_add=True)
    confidence = models.FloatField()

    class Meta:
        managed = True
        db_table = 'store_product_predicted_categories'
        verbose_name = 'Predicted Store Product Category'
        verbose_name_plural = 'Predicted Store Product Categories'


class Batch(BaseModel):
    scrape_datetime = models.DateTimeField()
    total_number_of_products = models.IntegerField()
    total_number_of_new_products = models.IntegerField()
    total_number_of_missing_products = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    store = models.ForeignKey('Store', models.CASCADE, blank=True, null=True)
    region = models.CharField(max_length=512, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'scrape_batches'
        verbose_name = 'Batch'
        verbose_name_plural = 'Batches'

    def __str__(self):
        return f"Scrape id {self.id} date {self.scrape_datetime}"


class Source(BaseModel):
    name = models.CharField(max_length=512)

    class Meta:
        managed = True
        db_table = 'sources'
        unique_together = (('name', 'deleted'),)
        verbose_name = 'Source'
        verbose_name_plural = 'Sources'

    def __str__(self):
        return self.name


class StoreProductAllergensWarning(BaseModel):
    store_product = models.ForeignKey('StoreProduct', models.CASCADE)
    allergens_warning = models.ForeignKey('AllergensWarning', models.CASCADE)

    class Meta:
        managed = True
        db_table = 'store_product_allergens_warnings'
        unique_together = (('store_product', 'allergens_warning'),)
        verbose_name = 'SP Allergens Warning'
        verbose_name_plural = 'SP Allergens Warnings'


class StoreProductBullet(BaseModel):
    store_product = models.ForeignKey('StoreProduct', models.CASCADE)
    bullet = models.ForeignKey('Bullet', models.CASCADE)

    class Meta:
        managed = True
        db_table = 'store_product_bullets'
        unique_together = (('store_product', 'bullet'),)
        verbose_name = 'SP Bullet'
        verbose_name_plural = 'SP Bullets'


class StoreProductDietaryInfo(BaseModel):
    store_product = models.ForeignKey('StoreProduct', models.CASCADE)
    dietary_information = models.ForeignKey('DietaryInformation', models.CASCADE)

    class Meta:
        managed = True
        db_table = 'store_product_dietary_infos'
        unique_together = (('store_product', 'dietary_information'),)
        verbose_name = 'SP Dietary Information'
        verbose_name_plural = 'SP Dietary Information'


class StoreProductImage(BaseModel):
    label = models.CharField(max_length=250, blank=True, null=True)
    number = models.IntegerField()
    image_path = models.CharField(max_length=2048, blank=True, null=True)
    store_product = models.ForeignKey('StoreProduct', models.CASCADE)

    class Meta:
        managed = True
        db_table = 'store_product_images'
        unique_together = (('label', 'number', 'store_product'),)
        verbose_name = 'SP Image'
        verbose_name_plural = 'SP Images'


class StoreProductNutritionFact(BaseModel):
    store_product = models.ForeignKey('StoreProduct', models.CASCADE, related_name='nutrition_facts')
    nutrient = models.ForeignKey('Nutrient', models.CASCADE)
    amount = models.FloatField(blank=True, null=True)
    amount_unit = models.ForeignKey('Unit', models.CASCADE, blank=True, null=True)
    daily_value = models.FloatField(blank=True, null=True)
    supplemented = models.BooleanField(default=False)
    nft_label = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'store_product_nutrition_facts'
        unique_together = (('store_product', 'nutrient'),)
        verbose_name = 'SP Nutrition Fact'
        verbose_name_plural = 'SP Nutrition Facts'


class StoreProduct(BaseModel):
    id = models.BigIntegerField(primary_key=True) # override autoincrement since we're pulling from flaimeshot now
    store = models.ForeignKey('Store', models.CASCADE)
    store_product_code = models.CharField(max_length=512)
    sku = models.CharField(max_length=512, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    company = models.ForeignKey('Company', models.CASCADE, blank=True, null=True)
    brand = models.ForeignKey('Brand', models.CASCADE, blank=True, null=True)
    raw_brand = models.CharField(max_length=256, blank=True, null=True)
    site_name = models.CharField(max_length=512, blank=True, null=True)
    site_description = models.CharField(max_length=10240, blank=True, null=True)
    scrape_batch = models.ForeignKey('Batch', models.CASCADE, blank=True, null=True)
    private_label = models.CharField(max_length=4096, blank=True, null=True)
    variety_pack_flag = models.BooleanField(default=False)
    supplemented_food = models.BooleanField(default=False)
    multiple_nfts_flag = models.BooleanField(blank=True, null=True)
    fop_flag = models.BooleanField(blank=True, null=True)
    individually_packaged_flag = models.BooleanField(blank=True, null=True)
    has_preparation_instructions_flag = models.BooleanField(blank=True, null=True)
    nutrition_available_flag = models.BooleanField()
    nutrition_facts_json = models.JSONField(blank=True, null=True)
    total_size = models.CharField(max_length=500, blank=True, null=True)
    raw_serving_size = models.CharField(max_length=500, blank=True, null=True)
    serving_size = models.IntegerField(blank=True, null=True)
    serving_size_unit = models.ForeignKey('Unit', models.CASCADE, blank=True, null=True)
    ingredient_en = models.TextField(blank=True, null=True)
    ingredient_fr = models.TextField(blank=True, null=True)
    raw_upc = models.CharField(max_length=512, blank=True, null=True)
    verified = models.BooleanField(verbose_name='Entire product manually verified')
    verified_by = models.CharField(max_length=256, blank=True, null=True)
    atwater_result = models.CharField(max_length=64, blank=True, null=True)
    source = models.ForeignKey('Source', models.CASCADE, blank=True, null=True)
    nielsen_upc = models.CharField(max_length=124, blank=True, null=True)
    tags = models.CharField(max_length=2048, blank=True, null=True)
    external_id = models.CharField(max_length=250, blank=True, null=True)
    verified_nft_ingredients = models.CharField(
        max_length=20,
        choices=VerifiedNftIngredients.choices,
        default=VerifiedNftIngredients.UNKNOWN,
        verbose_name='Verified NFT'
    )
    storage_condition = models.CharField(
        max_length=20,
        choices=StorageConditions.choices,
        default=StorageConditions.SHELF_STABLE,
        verbose_name='Storage Condition'
    )
    primary_package_material = models.CharField(
        max_length=20,
        choices=PackagingChoices.choices,
        default=PackagingChoices.OTHER,
        verbose_name='Primary Package Material'
    )
    secondary_package_material = models.CharField(
        max_length=20,
        blank=True, null=True,
        choices=PackagingChoices.choices,
        verbose_name='Secondary Package Material'
    )
    num_units = models.IntegerField(
        blank=True, null=True,
        verbose_name='Number of Units'
    )
    needs_manual_verification = models.BooleanField(default=False)
    manual_verification_reason = models.CharField(max_length=500, blank=True, null=True)
    allergens_warnings = models.ManyToManyField(
        'AllergensWarning',
        through='StoreProductAllergensWarning',
        through_fields=('store_product', 'allergens_warning')
    )
    bullets = models.ManyToManyField(
        'Bullet',
        through='StoreProductBullet',
        through_fields=('store_product', 'bullet')
    )
    dietary_informations = models.ManyToManyField(
        'DietaryInformation',
        through='StoreProductDietaryInfo',
        through_fields=('store_product', 'dietary_information')
    )
    nutrients = models.ManyToManyField(
        'Nutrient',
        through='StoreProductNutritionFact',
        through_fields=('store_product', 'nutrient'),
    )
    upcs = models.ManyToManyField(
        'UPC',
        through='StoreProductUPC',
        through_fields=('store_product', 'upc'),
    )

    class Meta:
        managed = True
        db_table = 'store_products'
        verbose_name = 'Store Product'
        verbose_name_plural = 'Store Products'

    def __str__(self):
        return self.site_name


class SuppFoodLabelFlags(models.Model):
    store_product = models.OneToOneField(StoreProduct, on_delete=models.CASCADE, related_name='label_flags')
    has_supplemental_caution_id = models.BooleanField(default=False)
    has_nutrient_content_claim = models.BooleanField(default=False)
    has_nutrient_function_claim = models.BooleanField(default=False)
    has_disease_risk_reduction_claim = models.BooleanField(default=False)
    has_probiotic_claim = models.BooleanField(default=False)
    has_therapeutic_claim = models.BooleanField(default=False)
    has_function_claim = models.BooleanField(default=False)
    has_general_health_claim = models.BooleanField(default=False)
    has_quantitative_nutrient_declaration = models.BooleanField(default=False)
    has_implied_nonspecific_claim = models.BooleanField(default=False)
    has_logos_icons = models.BooleanField(default=False)
    has_third_party_label = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'supp_food_label_flags'
        verbose_name = 'Label Flags for Supplemented Foods'
        verbose_name_plural = 'Label Flags for Supplemented Foods'

    def __str__(self):
        return f"Label flags for {self.store_product}"


class Store(BaseModel):
    name = models.CharField(max_length=512)

    class Meta:
        managed = True
        db_table = 'stores'
        unique_together = (('name', 'deleted'),)
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'

    def __str__(self):
        return self.name


class Unit(BaseModel):
    name = models.CharField(unique=True, max_length=512)
    description = models.CharField(max_length=512)

    class Meta:
        managed = True
        db_table = 'units'
        verbose_name = 'Unit'
        verbose_name_plural = 'Units'

    def __str__(self):
        return self.name


class UPC(BaseModel):
    code = models.CharField(unique=True, max_length=128)
    company = models.ForeignKey('Company', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'upcs'
        verbose_name = 'UPC'
        verbose_name_plural = 'UPCs'

    def __str__(self):
        return self.code
