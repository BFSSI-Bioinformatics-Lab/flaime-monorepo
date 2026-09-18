from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from ..models import Category, CategoryScheme


class BaseCategorySerializer(serializers.ModelSerializer):
    scheme = serializers.StringRelatedField()
    verification_info = serializers.SerializerMethodField()
    prediction_info = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'scheme', 'level', 'verification_info', 'prediction_info']

    @extend_schema_field({
        'type': 'object',
        'nullable': True,
        'properties': {
            'verified_by': {'type': 'string', 'format': 'email'},
            'date_added': {'type': 'string', 'format': 'date-time'},
            'problematic': {'type': 'boolean'},
            'notes': {'type': 'string'}
        }
    })
    def get_verification_info(self, obj):
        manual_category = self.context.get('manual_category')
        if not manual_category:
            return None
        return {
            'verified_by': manual_category.user.email,
            'date_added': manual_category.date_added,
            'problematic': manual_category.problematic_flag,
            'notes': manual_category.notes
        }

    @extend_schema_field({
        'type': 'object',
        'nullable': True,
        'properties': {
            'model': {'type': 'string'},
            'confidence': {'type': 'number', 'format': 'float'},
            'date_predicted': {'type': 'string', 'format': 'date-time'}
        }
    })
    def get_prediction_info(self, obj):
        predicted_category = self.context.get('predicted_category')
        if not predicted_category:
            return None
        return {
            'model': predicted_category.model_id,
            'confidence': predicted_category.confidence,
            'date_predicted': predicted_category.date_predicted
        }


class CategoryTreeSerializer(BaseCategorySerializer):
    children = serializers.SerializerMethodField()

    class Meta(BaseCategorySerializer.Meta):
        fields = BaseCategorySerializer.Meta.fields + ['children']
    
    @extend_schema_field('CategoryTreeSerializer')
    def get_children(self, obj):
        children = obj.children.all()
        return CategoryTreeSerializer(children, many=True, context=self.context).data if children else None


class CategoryListSerializer(BaseCategorySerializer):
    parent_category = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta(BaseCategorySerializer.Meta):
        fields = BaseCategorySerializer.Meta.fields + ['parent_category']


class ProductCategorySerializer:
    @staticmethod
    @extend_schema_field({
        'type': 'object',
        'additionalProperties': {
            'type': 'object',
            'properties': {
                'manual': {
                    'type': 'array',
                    'items': {'$ref': '#/components/schemas/CategoryListSerializer'}
                },
                'predicted': {
                    'type': 'array',
                    'items': {'$ref': '#/components/schemas/CategoryListSerializer'}
                }
            }
        }
    })
    def get_categories_as_list(store_product):
        schemes = CategoryScheme.objects.all()
        categories = {}

        for scheme in schemes:
            categories[scheme.name] = {
                'manual': [],
                'predicted': []
            }

        manual = store_product.manual_categories.select_related(
            'category',
            'category__scheme',
            'category__parent_category',
            'user'
        ).all()

        predicted = store_product.predicted_categories.select_related(
            'category',
            'category__scheme',
            'category__parent_category'
        ).all()

        for m in manual:
            if not m.category.scheme:
                continue
            scheme_name = m.category.scheme.name
            categories[scheme_name]['manual'].append(
                CategoryListSerializer(m.category, context={'manual_category': m}).data
            )
            categories[scheme_name]['manual'].sort(key=lambda x: x['level'])

        for p in predicted:
            if not p.category.scheme:
                continue
            scheme_name = p.category.scheme.name
            categories[scheme_name]['predicted'].append(
                CategoryListSerializer(p.category, context={'predicted_category': p}).data
            )
            categories[scheme_name]['predicted'].sort(key=lambda x: x['level'])

        return categories


class CategoryVerificationStatsSerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    verified_count = serializers.IntegerField()
    unverified_count = serializers.IntegerField()


class CategorySchemeSerializer(serializers.ModelSerializer):
    category_count = serializers.SerializerMethodField()

    class Meta:
        model = CategoryScheme
        fields = ['id', 'name', 'description', 'category_count']

    @extend_schema_field({'type': 'integer'})
    def get_category_count(self, obj):
        return obj.category_set.filter(deleted=False).count()


class DetailedCategorySchemeSerializer(CategorySchemeSerializer):
    categories = serializers.SerializerMethodField()

    class Meta(CategorySchemeSerializer.Meta):
        fields = CategorySchemeSerializer.Meta.fields + ['categories']

    @extend_schema_field({
        'type': 'array',
        'items': {'$ref': '#/components/schemas/CategoryTreeSerializer'}
    })
    def get_categories(self, obj):
        root_categories = obj.category_set.filter(
            parent_category__isnull=True,
            deleted=False
        ).order_by('name')
        return CategoryTreeSerializer(root_categories, many=True).data