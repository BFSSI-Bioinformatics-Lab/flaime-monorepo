from django.urls import reverse
from rest_framework.test import APITestCase

from flaime_py.users.tests.factories import UserFactory

from .factories import StoreProductFactory


class DetailedStoreProductAllergenTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=UserFactory())

    def get(self, product):
        url = reverse("api:storeproduct-detail", kwargs={"pk": product.id})
        return self.client.get(url).data

    def test_allergen_columns_are_one_statement(self):
        product = StoreProductFactory(
            contains_en="Milk", contains_fr="Lait", may_contain_en="Peanuts", may_contain_fr=None,
        )
        assert self.get(product)["allergens_warnings"] == [
            {"contains_en": "Milk", "contains_fr": "Lait",
             "may_contain_en": "Peanuts", "may_contain_fr": None},
        ]

    def test_no_allergen_text_yields_empty_list(self):
        product = StoreProductFactory(contains_en="", may_contain_en=None)
        assert self.get(product)["allergens_warnings"] == []
