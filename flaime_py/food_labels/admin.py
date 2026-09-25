from django.contrib import admin
from django import forms
from .models import (
    StoreProduct, StoreProductNutritionFact, StoreProductUPC,
    StoreProductManualCategory,
    Category, Nutrient, Unit, UPC, Source, Store, Location,
    StoreProductAllergensWarning, AllergensWarning
)


# only superusers have delete privileges

class ProtectedModelAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(UPC)
class UPCAdmin(ProtectedModelAdmin):
    search_fields = ['code']
    list_display = ['id', 'code', 'company']
    list_filter = ['company']
    
    def get_model_perms(self, request):
        return {}

@admin.register(Source)
class SourceAdmin(ProtectedModelAdmin):
    search_fields = ['name']
    
    def get_model_perms(self, request):
        return {}

@admin.register(Store)
class StoreAdmin(ProtectedModelAdmin):
    search_fields = ['name']
    
    def get_model_perms(self, request):
        return {}

@admin.register(Location)
class LocationAdmin(ProtectedModelAdmin):
    search_fields = ['name', 'code']
    list_display = ['id', 'name', 'code']
    
    def get_model_perms(self, request):
        return {}


@admin.register(AllergensWarning)
class AllergensWarningAdmin(ProtectedModelAdmin):
    search_fields = ['contains_en', 'contains_fr', 'may_contain_en', 'may_contain_fr']
    list_display = ['id', 'allergen_summary', 'contains_en', 'may_contain_en']
    fields = ['contains_en', 'contains_fr', 'may_contain_en', 'may_contain_fr']
    
    def allergen_summary(self, obj):
        parts = []
        if obj.contains_en:
            parts.append(f"Contains: {obj.contains_en[:50]}")
        if obj.may_contain_en:
            parts.append(f"May contain: {obj.may_contain_en[:50]}")
        return "; ".join(parts) if parts else "No allergen info"
    allergen_summary.short_description = 'Summary'
    
    def get_model_perms(self, request):
        return {}


@admin.register(Category)
class CategoryAdmin(ProtectedModelAdmin):
    search_fields = ['name', 'code']
    list_display = ['id', 'name', 'code', 'scheme', 'level']
    list_filter = ['scheme', 'level']
    
    def get_model_perms(self, request):
        return {}


@admin.register(Nutrient)
class NutrientAdmin(ProtectedModelAdmin):
    search_fields = ['name', 'symbol']
    list_display = ['nutrient_code', 'name', 'symbol']
    
    def get_model_perms(self, request):
        return {}


@admin.register(Unit)
class UnitAdmin(ProtectedModelAdmin):
    search_fields = ['name', 'description']
    list_display = ['id', 'name', 'description']
    
    def get_model_perms(self, request):
        return {}


# custom form, looks up UPC model where it exists and adds the link

class StoreProductUPCInlineForm(forms.ModelForm):
    upc_code = forms.CharField(max_length=128, required=True, label='UPC Code')

    class Meta:
        model = StoreProductUPC
        fields = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.upc:
            self.fields['upc_code'].initial = self.instance.upc.code
    
    def clean_upc_code(self):
        upc_code = self.cleaned_data.get('upc_code')
        if not upc_code:
            raise forms.ValidationError('UPC code is required')
        return upc_code
    
    def save(self, commit=True):
        upc_code = self.cleaned_data.get('upc_code')
        if upc_code:
            upc, created = UPC.objects.get_or_create(code=upc_code)
            self.instance.upc = upc
        return super().save(commit=commit)



# inlines so that nutrients, categories, etc are editable from the product/sp page

class StoreProductUPCInline(admin.TabularInline):
    model = StoreProductUPC
    form = StoreProductUPCInlineForm
    extra = 1
    fields = ['upc_code']

class StoreProductManualCategoryInline(admin.TabularInline):
    model = StoreProductManualCategory
    extra = 1
    autocomplete_fields = ['category', 'user']
    readonly_fields = ['date_added']

class StoreProductNutritionFactInline(admin.TabularInline):
    model = StoreProductNutritionFact
    extra = 1
    autocomplete_fields = ['nutrient', 'amount_unit']
    fields = ['nutrient', 'amount', 'amount_unit', 'daily_value', 'supplemented']
    ordering = ['nutrient__sort_order', 'nutrient__name']

class StoreProductAllergensWarningInline(admin.TabularInline):
    model = StoreProductAllergensWarning
    extra = 1
    autocomplete_fields = ['allergens_warning']


# these ones will be directly editable

@admin.register(StoreProduct)
class StoreProductAdmin(ProtectedModelAdmin):
    list_display = ['id', 'site_name', 'store', 'location', 'brand', 'serving_size', 'serving_size_unit', 'source',
                    'verified', 'supplemented_food']
    list_filter = ['store', 'location', 'source', 'verified', 'nutrition_available_flag', 'supplemented_food',
                   'variety_pack_flag', 'needs_manual_verification', 'verified_nft_ingredients',
                   'storage_condition', 'primary_package_material']
    search_fields = ['site_name', 'store_product_code']
    raw_id_fields = ['brand']
    autocomplete_fields = ['source', 'store', 'location', 'serving_size_unit',
                           'total_size_unit', 'reference_amount_unit']
    fields = [
        'site_name', ('store', 'location'), 'source',
        'brand',
        ('serving_size', 'serving_size_unit'),
        ('total_size_value', 'total_size_unit'),
        ('reference_amount', 'reference_amount_unit'),
        'storage_condition',
        ('primary_package_material', 'secondary_package_material'),
        'num_units',
        'variety_pack_flag',
        'individually_packaged_flag',
        'supplemented_food',
        'verified',
        'verified_nft_ingredients',
        'needs_manual_verification',
        'manual_verification_reason',
        'ingredient_en',
        'ingredient_fr',
    ]
    inlines = [
        StoreProductUPCInline,
        StoreProductManualCategoryInline,
        StoreProductAllergensWarningInline,
        StoreProductNutritionFactInline,
    ]

    def has_add_permission(self, request):
        return request.user.is_superuser


@admin.register(StoreProductManualCategory)
class StoreProductManualCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'store_product_id', 'product_name', 'category', 'user', 'date_added',
                    'problematic_flag']
    list_filter = ['problematic_flag', 'date_added', 'category']
    search_fields = ['store_product__site_name', 'category__name', 'notes']
    autocomplete_fields = ['category', 'user']
    raw_id_fields = ['store_product']
    readonly_fields = ['date_added']

    def product_name(self, obj):
        return obj.store_product.site_name
    product_name.short_description = 'Product'


