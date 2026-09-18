from django.urls import reverse
from rest_framework.test import APITestCase

from flaime_py.users.tests.factories import UserFactory

from .factories import NutrientFactory
from .factories import SourceFactory
from .factories import StoreFactory
from .factories import StoreProductFactory
from .factories import StoreProductNutritionFactFactory


class AuthMixin:
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)


class StoreCountsTests(AuthMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("api:storeproduct-store-counts")

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.post(self.url, {}, format="json").status_code == 401

    def test_counts_per_store(self):
        a = StoreFactory(name="Loblaws")
        b = StoreFactory(name="Metro")
        StoreProductFactory.create_batch(3, store=a)
        StoreProductFactory.create_batch(1, store=b)
        StoreProductFactory(store=b, deleted=True)

        response = self.client.post(self.url, {}, format="json")
        assert response.status_code == 200
        assert response.data == [
            {"store": "Loblaws", "count": 3},
            {"store": "Metro", "count": 1},
        ]

    def test_respects_filters(self):
        store = StoreFactory(name="Sobeys")
        keep_source = SourceFactory()
        StoreProductFactory.create_batch(2, store=store, source=keep_source)
        StoreProductFactory(store=store, source=SourceFactory())

        response = self.client.post(
            self.url,
            {"filters": {"source": keep_source.id}},
            format="json",
        )
        assert response.data == [{"store": "Sobeys", "count": 2}]


class CollectionStatsAllSourcesTests(AuthMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("api:storeproduct-collection-stats")

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.get(self.url).status_code == 401

    def test_base_counts_and_nutrient_stats(self):
        nutrient = NutrientFactory()
        source = SourceFactory()
        products = StoreProductFactory.create_batch(4, source=source)
        for product, amount in zip(products, [10, 20, 30, 40], strict=False):
            StoreProductNutritionFactFactory(
                store_product=product,
                nutrient=nutrient,
                amount=amount,
            )
        StoreProductFactory(source=source, fop_flag=True)

        # point the first configured nutrient row at our nutrient id
        from flaime_py.food_labels.api import collection_stats as cs

        original = cs.COLLECTION_STATS_NUTRIENTS
        cs.COLLECTION_STATS_NUTRIENTS = [
            {"label": "TestNutrient", "nutrient_ids": [nutrient.id], "unit": "g"},
        ]
        try:
            response = self.client.get(self.url)
        finally:
            cs.COLLECTION_STATS_NUTRIENTS = original

        assert response.status_code == 200
        assert response.data["total"] == 5
        assert response.data["with_fop"] == 1
        stat = response.data["nutrients"][0]
        assert stat["count"] == 4
        assert stat["mean"] == 25.0
        assert stat["median"] == 25.0
        assert stat["min"] == 10.0
        assert stat["max"] == 40.0

    def test_additive_prevalence(self):
        StoreProductFactory(ingredient_en="water, citric acid, salt")
        StoreProductFactory(ingredient_en="water, salt")

        response = self.client.get(self.url)
        citric = next(
            a for a in response.data["additives"] if a["term"] == "Citric Acid"
        )
        assert citric["count"] == 1
        assert citric["percentage"] == 50.0

    def test_source_scoping(self):
        keep = SourceFactory()
        StoreProductFactory.create_batch(2, source=keep)
        StoreProductFactory(source=SourceFactory())

        response = self.client.get(self.url, {"source": keep.id})
        assert response.data["total"] == 2
