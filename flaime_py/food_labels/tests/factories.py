import datetime

from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from flaime_py.food_labels.models import (
    AllergensWarning,
    Batch,
    Category,
    CategoryScheme,
    Nutrient,
    Source,
    Store,
    StoreProduct,
    StoreProductAllergensWarning,
    StoreProductImage,
    StoreProductManualCategory,
    StoreProductNutritionFact,
    StoreProductPredictedCategory,
    SuppFoodLabelFlags,
    Unit,
)
from flaime_py.users.tests.factories import UserFactory


class CategorySchemeFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"Scheme {n}")
    description = Faker("sentence")

    class Meta:
        model = CategoryScheme


class CategoryFactory(DjangoModelFactory):
    name = Faker("word")
    code = Sequence(lambda n: f"CODE-{n}")
    scheme = SubFactory(CategorySchemeFactory)
    parent_category = None
    level = 1

    class Meta:
        model = Category


class SourceFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"Source {n}")

    class Meta:
        model = Source
        django_get_or_create = ["name"]


class StoreFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"Store {n}")

    class Meta:
        model = Store
        django_get_or_create = ["name"]


class NutrientFactory(DjangoModelFactory):
    nutrient_code = Sequence(lambda n: n + 1)
    name = Sequence(lambda n: f"Nutrient {n}")
    symbol = Sequence(lambda n: f"N{n}")

    class Meta:
        model = Nutrient
        django_get_or_create = ["nutrient_code"]


class BatchFactory(DjangoModelFactory):
    scrape_datetime = Faker("date_time_this_year", tzinfo=datetime.timezone.utc)
    total_number_of_products = 0
    total_number_of_new_products = 0
    total_number_of_missing_products = 0
    store = SubFactory(StoreFactory)

    class Meta:
        model = Batch


class StoreProductFactory(DjangoModelFactory):
    id = Sequence(lambda n: n + 1_000_000)
    store = SubFactory(StoreFactory)
    source = SubFactory(SourceFactory)
    store_product_code = Sequence(lambda n: f"SP-{n}")
    site_name = Faker("word")
    nutrition_available_flag = False
    verified = False

    class Meta:
        model = StoreProduct


class StoreProductImageFactory(DjangoModelFactory):
    store_product = SubFactory(StoreProductFactory)
    number = Sequence(lambda n: n + 1)
    image_path = Sequence(lambda n: f"/path/to/image_{n}.jpg")
    label = "Main"

    class Meta:
        model = StoreProductImage


class StoreProductManualCategoryFactory(DjangoModelFactory):
    store_product = SubFactory(StoreProductFactory)
    category = SubFactory(CategoryFactory)
    user = SubFactory(UserFactory)
    problematic_flag = False
    notes = ""

    class Meta:
        model = StoreProductManualCategory


class StoreProductPredictedCategoryFactory(DjangoModelFactory):
    store_product = SubFactory(StoreProductFactory)
    category = SubFactory(CategoryFactory)
    model_id = "test-model-v1"
    confidence = 0.9

    class Meta:
        model = StoreProductPredictedCategory


class UnitFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"unit-{n}")
    description = "test unit"

    class Meta:
        model = Unit
        django_get_or_create = ["name"]


class StoreProductNutritionFactFactory(DjangoModelFactory):
    store_product = SubFactory(StoreProductFactory)
    nutrient = SubFactory(NutrientFactory)
    amount = 10.0
    amount_unit = SubFactory(UnitFactory)
    daily_value = None
    supplemented = False

    class Meta:
        model = StoreProductNutritionFact


class AllergensWarningFactory(DjangoModelFactory):
    contains_en = "milk"
    contains_fr = "lait"
    may_contain_en = "peanut"
    may_contain_fr = "arachide"

    class Meta:
        model = AllergensWarning


class StoreProductAllergensWarningFactory(DjangoModelFactory):
    store_product = SubFactory(StoreProductFactory)
    allergens_warning = SubFactory(AllergensWarningFactory)

    class Meta:
        model = StoreProductAllergensWarning


class SuppFoodLabelFlagsFactory(DjangoModelFactory):
    store_product = SubFactory(StoreProductFactory)

    class Meta:
        model = SuppFoodLabelFlags
