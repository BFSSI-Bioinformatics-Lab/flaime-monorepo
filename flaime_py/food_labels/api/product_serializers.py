from django.conf import settings
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .serializers import (
    SimpleCompanySerializer,
    SimpleNutrientSerializer,
    SimpleSourceSerializer,
    SimpleStoreSerializer,
    UnitSerializer,
)
from .category_serializers import ProductCategorySerializer
from ..images import blob_image_urls
from ..models import (
    StoreProduct,
    StoreProductNutritionFact,
    SuppFoodLabelFlags,
    UPC,
)

ALLERGEN_FIELDS = ["contains_en", "contains_fr", "may_contain_en", "may_contain_fr"]

# The allergen statements are columns on the store product now (migration 0045). The API
# keeps its old shape, a list of statements, which now holds at most one entry.
ALLERGENS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            field: {"type": "string", "nullable": True} for field in ALLERGEN_FIELDS
        },
    },
}


def allergen_statements(obj):
    statement = {field: getattr(obj, field) for field in ALLERGEN_FIELDS}
    return [statement] if any(statement.values()) else []


CATEGORIES_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "type": "object",
        "properties": {
            "manual": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/CategoryListSerializer"},
            },
            "predicted": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/CategoryListSerializer"},
            },
        },
    },
}


class UPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = UPC
        fields = ["code"]


class SimpleStoreProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProduct
        fields = [
            "id",
            "store_product_code",
            "sku",
            "price",
            "raw_brand",
            "site_name",
            "total_size",
            "external_id",
        ]


class StoreProductSearchResultSerializer(serializers.ModelSerializer):
    """Flat search-result row for POST /api/storeproducts/search/.

    Replaces the Elasticsearch ``hits.hits[]._source`` shape.  Unlike
    ``DetailedStoreProductSerializer`` this serializer keeps ``null`` values so
    the frontend contract (schema.yaml) is honest about optional fields.
    """

    source = SimpleSourceSerializer(read_only=True)
    source_group = serializers.CharField(source="source.group.name", default=None, read_only=True)
    store = SimpleStoreSerializer(read_only=True)
    ingest_run = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    storage_condition = serializers.CharField(source="get_storage_condition_display")
    primary_package_material = serializers.CharField(
        source="get_primary_package_material_display"
    )
    secondary_package_material = serializers.CharField(
        source="get_secondary_package_material_display", allow_null=True
    )
    allergens_warnings = serializers.SerializerMethodField()

    class Meta:
        model = StoreProduct
        fields = [
            "id",
            "site_name",
            "external_id",
            "raw_upc",
            "nielsen_upc",
            "price",
            "source",
            "source_group",
            "store",
            "ingest_run",
            "location",
            "categories",
            "storage_condition",
            "primary_package_material",
            "secondary_package_material",
            "allergens_warnings",
            "verified",
        ]

    @extend_schema_field(
        {
            "type": "object",
            "nullable": True,
            "properties": {
                "id": {"type": "integer"},
                "started": {"type": "string", "format": "date-time"},
            },
        }
    )
    def get_ingest_run(self, obj):
        """The load that added the product; its start dates the product."""
        if not obj.ingest_run_id:
            return None
        return {"id": obj.ingest_run_id, "started": obj.ingest_run.started}

    @extend_schema_field(
        {
            "type": "object",
            "nullable": True,
            "properties": {
                "code": {"type": "string"},
                "name": {"type": "string"},
            },
        }
    )
    def get_location(self, obj):
        if not obj.location_id:
            return None
        return {"code": obj.location.code, "name": obj.location.name}

    @extend_schema_field(
        {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "level": {"type": "integer"},
                },
            },
        }
    )
    def get_categories(self, obj):
        seen = {}
        for link in obj.manual_categories.all():
            cat = link.category
            seen.setdefault(
                cat.id, {"id": cat.id, "name": cat.name, "level": cat.level}
            )
        return sorted(seen.values(), key=lambda c: c["level"])

    @extend_schema_field(ALLERGENS_SCHEMA)
    def get_allergens_warnings(self, obj):
        return allergen_statements(obj)


class StoreProductNutritionFactSerializer(serializers.ModelSerializer):
    nutrient = SimpleNutrientSerializer()
    amount_unit = UnitSerializer()

    class Meta:
        model = StoreProductNutritionFact
        fields = ["nutrient", "amount", "amount_unit", "daily_value", "supplemented"]


class SuppFoodLabelFlagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuppFoodLabelFlags
        exclude = ["id", "store_product"]


class DetailedStoreProductSerializer(serializers.ModelSerializer):
    store = serializers.StringRelatedField()
    source = serializers.StringRelatedField()
    source_group = serializers.CharField(source="source.group.name", default=None, read_only=True)
    brand = serializers.StringRelatedField()
    serving_size_unit = serializers.StringRelatedField()
    company = SimpleCompanySerializer()
    nutrition_facts = StoreProductNutritionFactSerializer(many=True, read_only=True)
    external_id = serializers.StringRelatedField()
    label_flags = SuppFoodLabelFlagsSerializer(read_only=True)
    allergens_warnings = serializers.SerializerMethodField()
    upcs = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    store_product_images = serializers.SerializerMethodField()
    store_product_image_urls = serializers.SerializerMethodField()
    storage_condition = serializers.CharField(source="get_storage_condition_display")
    primary_package_material = serializers.CharField(
        source="get_primary_package_material_display"
    )
    secondary_package_material = serializers.CharField(
        source="get_secondary_package_material_display"
    )

    class Meta:
        model = StoreProduct
        fields = [
            "id",
            "store_product_code",
            "sku",
            "price",
            "brand",
            "raw_brand",
            "site_name",
            "site_description",
            "nutrition_facts_json",
            "total_size",
            "raw_serving_size",
            "raw_upc",
            "nielsen_upc",
            "upcs",
            "categories",
            "private_label",
            "tags",
            "store",
            "serving_size",
            "serving_size_unit",
            "ingredient_en",
            "ingredient_fr",
            "source",
            "source_group",
            "company",
            "created_datetime",
            "modified_datetime",
            "nutrition_facts",
            "external_id",
            "label_flags",
            "allergens_warnings",
            "storage_condition",
            "primary_package_material",
            "secondary_package_material",
            "needs_manual_verification",
            "verified",
            "variety_pack_flag",
            "supplemented_food",
            "product",
            "store_product_images",
            "store_product_image_urls",
        ]

    @extend_schema_field(ALLERGENS_SCHEMA)
    def get_allergens_warnings(self, obj):
        return allergen_statements(obj)

    @extend_schema_field(UPCSerializer(many=True))
    def get_upcs(self, obj):
        return UPCSerializer(
            [link.upc for link in obj.storeproductupc_set.all()], many=True
        ).data

    @extend_schema_field(CATEGORIES_SCHEMA)
    def get_categories(self, obj):
        return ProductCategorySerializer.get_categories_as_list(obj)

    @extend_schema_field({"type": "array", "items": {"type": "string"}})
    def get_store_product_images(self, obj):
        # Replaces the images_v1 Elasticsearch index / REACT_APP_ELASTIC_IMG_URL.
        # Prefetched ordered by `number` in the viewset.
        return [
            img.image_path for img in obj.storeproductimage_set.all() if img.image_path
        ]

    @extend_schema_field(
        {
            "type": "array",
            "nullable": True,
            "items": {
                "type": "object",
                "properties": {"full": {"type": "string"}, "thumb": {"type": "string"}},
            },
        },
    )
    def get_store_product_image_urls(self, obj):
        # Azure Blob Storage URLs, in the same order as store_product_images.
        # Omitted when AZURE_IMAGES_READ_SAS_URL is not set (on-prem image server).
        if not settings.AZURE_IMAGES_READ_SAS_URL:
            return None
        return [blob_image_urls(path) for path in self.get_store_product_images(obj)]

    @extend_schema_field(
        {
            "type": "object",
            "nullable": True,
            "description": (
                "Deprecated compatibility shim. The products table was dropped in the "
                "FSDH migration; these values are synthesised from the store product "
                "itself. Read the top-level fields instead."
            ),
        }
    )
    def get_product(self, obj):
        # The `products` table no longer exists. flaime-2.0 still reads
        # `store_product.product.{brand,upcs,categories,supplemented_food}`, so keep
        # emitting the old shape until the frontend moves to the flattened fields.
        return {
            "id": obj.id,
            "name_of_product": obj.site_name,
            "description_of_product": obj.site_description,
            "brand": obj.brand.name if obj.brand else None,
            "total_size": obj.total_size,
            "total_size_value": None,
            "total_size_unit": None,
            "serving_size": obj.serving_size,
            "serving_size_unit": (
                obj.serving_size_unit.name if obj.serving_size_unit else None
            ),
            "ingredient_en": obj.ingredient_en,
            "ingredient_fr": obj.ingredient_fr,
            "categories": self.get_categories(obj),
            "supplemented_food": obj.supplemented_food,
            "upcs": self.get_upcs(obj),
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {k: v for k, v in representation.items() if v is not None}
