import csv
import io

from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from flaime_py.food_labels.exports import build_headers
from flaime_py.food_labels.exports import resolve_nutrients
from flaime_py.users.tests.factories import UserFactory

from .factories import CategoryFactory
from .factories import CategorySchemeFactory
from .factories import NutrientFactory
from .factories import SourceFactory
from .factories import StoreFactory
from .factories import StoreProductFactory
from .factories import StoreProductManualCategoryFactory
from .factories import StoreProductNutritionFactFactory
from .factories import SuppFoodLabelFlagsFactory


class AuthMixin:
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)


def _read_csv(response):
    body = b"".join(response.streaming_content).decode("utf-8")
    return list(csv.reader(io.StringIO(body)))


class StoreProductExportTests(AuthMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("api:storeproduct-export")

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.post(self.url, {}, format="json").status_code == 401

    def test_simple_layout(self):
        source = SourceFactory(name="MySource")
        store = StoreFactory(name="MyStore")
        scheme = CategorySchemeFactory()
        product = StoreProductFactory(
            source=source,
            store=store,
            site_name="Widget",
            external_id="E1",
        )
        StoreProductManualCategoryFactory(
            store_product=product,
            category=CategoryFactory(scheme=scheme, name="Snacks", level=1),
            user=self.user,
        )

        response = self.client.post(
            self.url,
            {"columns": "simple"},
            format="json",
        )
        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"
        rows = _read_csv(response)
        assert rows[0] == [
            "Assigned Flaime ID",
            "External ID",
            "Store Name",
            "Data Source",
            "Product Name",
            "Category Name",
        ]
        assert rows[1] == [
            str(product.id),
            "E1",
            "MyStore",
            "MySource",
            "Widget",
            "Snacks",
        ]

    def test_full_layout_header_matches_export_module(self):
        StoreProductFactory()
        response = self.client.post(self.url, {"columns": "full"}, format="json")
        rows = _read_csv(response)
        expected = build_headers("full", resolve_nutrients())
        assert rows[0] == expected
        assert rows[0][:3] == ["flaime_id", "source", "storage_condition"]
        assert rows[0][-3:] == ["ingredients_en", "nft_verified", "product_verified"]

    def test_full_supplemented_adds_flag_columns(self):
        product = StoreProductFactory()
        SuppFoodLabelFlagsFactory(
            store_product=product,
            has_probiotic_claim=True,
        )
        response = self.client.post(
            self.url,
            {"columns": "full_supplemented"},
            format="json",
        )
        rows = _read_csv(response)
        assert "SUPP_has_probiotic_claim" in rows[0]
        assert "SUPP_has_third_party_label" in rows[0]

    def test_nutrient_amount_lands_in_full_export(self):
        nutrient = NutrientFactory(name="SODIUM")
        product = StoreProductFactory()
        StoreProductNutritionFactFactory(
            store_product=product,
            nutrient=nutrient,
            amount=123.0,
        )
        response = self.client.post(self.url, {"columns": "full"}, format="json")
        rows = _read_csv(response)
        header, data = rows[0], rows[1]
        assert "123.0" in data
        assert "Sodium_amount" in header

    def test_filters_apply_to_export(self):
        keep = SourceFactory()
        StoreProductFactory(source=keep)
        StoreProductFactory(source=SourceFactory())

        response = self.client.post(
            self.url,
            {"columns": "simple", "filters": {"source": keep.id}},
            format="json",
        )
        rows = _read_csv(response)
        assert len(rows) == 2  # header + 1 product

    @override_settings(EXPORT_MAX_ROWS=1)
    def test_row_cap_returns_400(self):
        StoreProductFactory()
        StoreProductFactory()
        response = self.client.post(
            self.url,
            {"columns": "simple"},
            format="json",
        )
        assert response.status_code == 400
        assert "exceeds the limit" in response.data["detail"]

    def test_invalid_columns_returns_400(self):
        response = self.client.post(
            self.url,
            {"columns": "nonsense"},
            format="json",
        )
        assert response.status_code == 400
