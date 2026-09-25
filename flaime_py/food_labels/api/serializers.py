from rest_framework import serializers

from ..models import Nutrient, Source, Store, Company, Unit


class SimpleSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'name']


class DetailedSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'


class SimpleStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name']


class DetailedStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class SimpleNutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrient
        fields = ['id', 'nutrient_code', 'name', 'symbol', 'usda_nutrient_code', 'parent', 'sort_order']


class DetailedNutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrient
        fields = '__all__'


class SimpleCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name']


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'description']
