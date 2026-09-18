from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from ..models import (
    StoreProductManualCategory,
    StoreProductImage,
    StoreProduct,
    StoreProductPredictedCategory
)


class StoreProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProductImage
        fields = ['image_path', 'label']


class PredictionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    category_code = serializers.CharField(source='category.code')
    category_id = serializers.IntegerField(source='category.id')
    
    class Meta:
        model = StoreProductPredictedCategory
        fields = [
            'category_id',
            'category_name',
            'category_code',
            'model_id',
            'confidence',
            'date_predicted'
        ]


class ProductPredictionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='site_name')
    product_size = serializers.CharField(source='total_size')
    # `product_id` is kept as an alias of the store product id: products was dropped
    # in the FSDH migration, and flaime-2.0 posts this value back on create.
    product_id = serializers.IntegerField(source='id')
    store_product_images = serializers.SerializerMethodField()
    predictions = PredictionSerializer(source='predicted_categories', many=True)

    class Meta:
        model = StoreProduct
        fields = [
            'id',
            'product_name',
            'product_size',
            'product_id',
            'store_product_images',
            'predictions'
        ]

    @extend_schema_field({
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'label': {'type': 'string'},
                'image_path': {'type': 'string'}
            }
        }
    })
    def get_store_product_images(self, obj):
        images = StoreProductImage.objects.filter(store_product=obj)
        return StoreProductImageSerializer(images, many=True).data


class ManualCategoryCreateSerializer(serializers.ModelSerializer):
    # `product` is accepted as a legacy alias for `store_product` so flaime-2.0 can
    # keep posting the id it reads back as `product_id`.
    product = serializers.PrimaryKeyRelatedField(
        source='store_product',
        queryset=StoreProduct.objects.all(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = StoreProductManualCategory
        fields = ['store_product', 'product', 'category', 'problematic_flag', 'notes']
        extra_kwargs = {
            'store_product': {'required': False},
            'notes': {'required': False, 'allow_blank': True}
        }

    def validate(self, data):
        if 'store_product' not in data or 'category' not in data:
            raise serializers.ValidationError(
                "Both product and category are required when creating a new verification"
            )

        existing = StoreProductManualCategory.objects.filter(
            store_product=data['store_product'],
            category=data['category']
        ).exists()

        if existing:
            raise serializers.ValidationError(
                "This product-category combination has already been verified"
            )

        return data


class ManualVerificationSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='store_product.id')
    product_name = serializers.CharField(source='store_product.site_name')
    product_size = serializers.CharField(source='store_product.total_size')
    category_id = serializers.IntegerField(source='category.id')
    category_name = serializers.CharField(source='category.name')
    category_code = serializers.CharField(source='category.code')
    user_email = serializers.EmailField(source='user.email')
    store_product_images = serializers.SerializerMethodField()

    class Meta:
        model = StoreProductManualCategory
        fields = [
            'id',
            'product_id',
            'product_name',
            'product_size',
            'category_id',
            'category_name',
            'category_code',
            'user_email',
            'date_added',
            'problematic_flag',
            'notes',
            'store_product_images'
        ]

    @extend_schema_field({
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'label': {'type': 'string'},
                'image_path': {'type': 'string'}
            }
        }
    })
    def get_store_product_images(self, obj):
        images = StoreProductImage.objects.filter(store_product_id=obj.store_product_id)
        return StoreProductImageSerializer(images, many=True).data


class ManualVerificationWithPredictionsSerializer(ManualVerificationSerializer):
    predictions = PredictionSerializer(source='store_product.predicted_categories', many=True, read_only=True)
    store_product_id = serializers.IntegerField(read_only=True)

    class Meta(ManualVerificationSerializer.Meta):
        fields = ManualVerificationSerializer.Meta.fields + ['predictions', 'store_product_id']
        read_only_fields = ['predictions']


class ManualCategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProductManualCategory
        fields = ['category', 'problematic_flag', 'notes']
        extra_kwargs = {
            'notes': {'required': False, 'allow_blank': True},
            'category': {'required': False},
            'problematic_flag': {'required': False}
        }