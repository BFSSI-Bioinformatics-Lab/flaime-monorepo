import datetime

from django.urls import reverse
from rest_framework.test import APITestCase

from flaime_py.users.tests.factories import UserFactory

from .factories import AllergensWarningFactory
from .factories import BatchFactory
from .factories import CategoryFactory
from .factories import CategorySchemeFactory
from .factories import LocationFactory
from .factories import NutrientFactory
from .factories import SourceFactory
from .factories import StoreFactory
from .factories import StoreProductAllergensWarningFactory
from .factories import StoreProductFactory
from .factories import StoreProductManualCategoryFactory
from .factories import StoreProductNutritionFactFactory
from .factories import StoreProductPredictedCategoryFactory


class AuthMixin:
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)


class StoreProductSearchTests(AuthMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("api:storeproduct-search")

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.post(self.url, {}, format="json").status_code == 401

    def test_empty_body_returns_paginated_envelope(self):
        StoreProductFactory(site_name="Alpha")
        StoreProductFactory(site_name="Beta")
        StoreProductFactory(site_name="Gamma", deleted=True)

        response = self.client.post(self.url, {}, format="json")
        assert response.status_code == 200
        assert set(response.data) == {"count", "next", "previous", "results"}
        assert response.data["count"] == 2
        row = response.data["results"][0]
        # flat, not hits.hits[]._source
        assert "id" in row and "site_name" in row and "_source" not in row

    def test_site_name_is_case_insensitive_substring(self):
        StoreProductFactory(site_name="Organic Granola Clusters")
        StoreProductFactory(site_name="Corn Flakes")

        response = self.client.post(
            self.url,
            {"text": {"site_name": "granola"}},
            format="json",
        )
        assert response.data["count"] == 1
        assert response.data["results"][0]["site_name"] == "Organic Granola Clusters"

    def test_id_list_exact_match(self):
        a = StoreProductFactory()
        StoreProductFactory()
        response = self.client.post(
            self.url,
            {"text": {"id_list": [a.id]}},
            format="json",
        )
        assert [r["id"] for r in response.data["results"]] == [a.id]

    def test_site_name_list_ors_within_and_ands_across(self):
        StoreProductFactory(site_name="Exact A", external_id="X1")
        StoreProductFactory(site_name="Exact B", external_id="X2")
        StoreProductFactory(site_name="Exact A", external_id="ZZ")

        body = {
            "text": {
                "site_name_list": ["Exact A", "Exact B"],
                "external_id_list": ["X1", "X2"],
            },
        }
        response = self.client.post(self.url, body, format="json")
        # "Exact A"/"Exact B" OR'd, then AND'd with the external_id list
        assert response.data["count"] == 2

    def test_source_and_store_filters(self):
        source = SourceFactory()
        store = StoreFactory()
        StoreProductFactory(source=source, store=store)
        StoreProductFactory()

        response = self.client.post(
            self.url,
            {"filters": {"source": source.id, "store": store.id}},
            format="json",
        )
        assert response.data["count"] == 1

    def test_region_filter_uses_location(self):
        ontario = LocationFactory(name="Ontario", code="ON")
        quebec = LocationFactory(name="Quebec", code="QC")
        StoreProductFactory(location=ontario)
        StoreProductFactory(location=quebec)
        StoreProductFactory()

        response = self.client.post(self.url, {"filters": {"region": "ON"}}, format="json")
        assert response.data["count"] == 1

    def test_category_filter_uses_manual_only(self):
        scheme = CategorySchemeFactory()
        category = CategoryFactory(scheme=scheme)
        manual_product = StoreProductFactory()
        StoreProductManualCategoryFactory(
            store_product=manual_product,
            category=category,
            user=self.user,
        )
        predicted_product = StoreProductFactory()
        StoreProductPredictedCategoryFactory(
            store_product=predicted_product,
            category=category,
        )

        response = self.client.post(
            self.url,
            {"filters": {"category": [category.id]}},
            format="json",
        )
        assert [r["id"] for r in response.data["results"]] == [manual_product.id]

    def test_no_duplicate_rows_when_product_has_many_categories(self):
        scheme = CategorySchemeFactory()
        product = StoreProductFactory()
        for _ in range(3):
            StoreProductManualCategoryFactory(
                store_product=product,
                category=CategoryFactory(scheme=scheme),
                user=self.user,
            )
        cat_ids = list(
            product.manual_categories.values_list("category_id", flat=True),
        )
        response = self.client.post(
            self.url,
            {"filters": {"category": cat_ids}},
            format="json",
        )
        assert response.data["count"] == 1

    def test_ingredients_all_vs_any(self):
        StoreProductFactory(ingredient_en="water, sugar, wheat flour, salt")
        StoreProductFactory(ingredient_en="water, sugar, salt")

        all_resp = self.client.post(
            self.url,
            {
                "filters": {
                    "ingredients": {"terms": ["sugar", "wheat flour"], "mode": "all"}
                }
            },
            format="json",
        )
        assert all_resp.data["count"] == 1

        any_resp = self.client.post(
            self.url,
            {
                "filters": {
                    "ingredients": {"terms": ["sugar", "wheat flour"], "mode": "any"}
                }
            },
            format="json",
        )
        assert any_resp.data["count"] == 2

    def test_ingredients_matches_english_or_french(self):
        StoreProductFactory(ingredient_en="", ingredient_fr="eau, sucre, farine")
        response = self.client.post(
            self.url,
            {"filters": {"ingredients": {"terms": ["farine"]}}},
            format="json",
        )
        assert response.data["count"] == 1

    def test_allergens_substring_over_contains_or_may_contain(self):
        hit = StoreProductFactory()
        StoreProductAllergensWarningFactory(
            store_product=hit,
            allergens_warning=AllergensWarningFactory(
                contains_en="",
                may_contain_en="may contain peanuts",
            ),
        )
        miss = StoreProductFactory()
        StoreProductAllergensWarningFactory(
            store_product=miss,
            allergens_warning=AllergensWarningFactory(
                contains_en="milk",
                may_contain_en="",
            ),
        )
        response = self.client.post(
            self.url,
            {"filters": {"allergens": "peanut"}},
            format="json",
        )
        assert [r["id"] for r in response.data["results"]] == [hit.id]

    def test_nutrient_range_filter(self):
        nutrient = NutrientFactory()
        low = StoreProductFactory()
        StoreProductNutritionFactFactory(
            store_product=low,
            nutrient=nutrient,
            amount=50,
        )
        high = StoreProductFactory()
        StoreProductNutritionFactFactory(
            store_product=high,
            nutrient=nutrient,
            amount=500,
        )

        response = self.client.post(
            self.url,
            {"filters": {"nutrient": {"id": nutrient.id, "min": 100, "max": 1000}}},
            format="json",
        )
        assert [r["id"] for r in response.data["results"]] == [high.id]

    def test_date_range_on_scrape_batch(self):
        old = StoreProductFactory(
            scrape_batch=BatchFactory(
                scrape_datetime=datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc),
            ),
        )
        new = StoreProductFactory(
            scrape_batch=BatchFactory(
                scrape_datetime=datetime.datetime(2024, 6, 1, tzinfo=datetime.timezone.utc),
            ),
        )
        no_batch = StoreProductFactory(scrape_batch=None)

        response = self.client.post(
            self.url,
            {"filters": {"date_from": "2023-01-01", "date_to": "2025-01-01"}},
            format="json",
        )
        ids = {r["id"] for r in response.data["results"]}
        assert ids == {new.id}
        assert old.id not in ids and no_batch.id not in ids

    def test_ordering_price_is_numeric(self):
        StoreProductFactory(site_name="p2", price=2.0)
        StoreProductFactory(site_name="p10", price=10.0)
        StoreProductFactory(site_name="p1", price=1.0)

        response = self.client.post(
            self.url,
            {"sort": {"field": "price", "order": "asc"}},
            format="json",
        )
        prices = [r["price"] for r in response.data["results"]]
        assert prices == [1.0, 2.0, 10.0]

    def test_invalid_sort_field_is_rejected(self):
        response = self.client.post(
            self.url,
            {"sort": {"field": "bogus"}},
            format="json",
        )
        assert response.status_code == 400

    def test_page_size_from_body(self):
        for i in range(5):
            StoreProductFactory(site_name=f"prod-{i}")
        response = self.client.post(
            self.url,
            {"page_size": 2, "page": 1},
            format="json",
        )
        assert len(response.data["results"]) == 2
        assert response.data["count"] == 5
        assert response.data["next"] is not None

    def test_scrape_batch_location_and_categories_in_result_shape(self):
        batch = BatchFactory()
        location = LocationFactory(name="Ontario", code="ON")
        product = StoreProductFactory(scrape_batch=batch, location=location, site_name="Shaped")
        scheme = CategorySchemeFactory()
        category = CategoryFactory(scheme=scheme, level=2)
        StoreProductManualCategoryFactory(
            store_product=product,
            category=category,
            user=self.user,
        )

        response = self.client.post(
            self.url,
            {"text": {"site_name": "Shaped"}},
            format="json",
        )
        row = response.data["results"][0]
        assert row["scrape_batch"]["datetime"] is not None
        assert row["location"] == {"code": "ON", "name": "Ontario"}
        assert row["categories"][0]["id"] == category.id
        assert row["categories"][0]["level"] == 2
        assert "verified" in row
