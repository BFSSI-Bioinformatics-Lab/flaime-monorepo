import datetime

from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from flaime_py.food_labels.models import (
    Category,
    CategoryScheme,
    IngestRun,
    Location,
    Nutrient,
    Source,
    SourceGroup,
    Store,
    StoreProduct,
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


class SourceGroupFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"Source group {n}")

    class Meta:
        model = SourceGroup
        django_get_or_create = ["name"]


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


class LocationFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"Province {n}")
    code = Sequence(lambda n: f"P{n}")

    class Meta:
        model = Location
        django_get_or_create = ["code"]


class IngestRunFactory(DjangoModelFactory):
    started = Faker("date_time_this_year", tzinfo=datetime.timezone.utc)
    status = IngestRun.Status.SUCCEEDED
    command = "test"

    class Meta:
        model = IngestRun


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


class SuppFoodLabelFlagsFactory(DjangoModelFactory):
    store_product = SubFactory(StoreProductFactory)

    class Meta:
        model = SuppFoodLabelFlags
