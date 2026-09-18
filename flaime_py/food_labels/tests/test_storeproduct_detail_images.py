from django.urls import reverse
from rest_framework.test import APITestCase

from flaime_py.users.tests.factories import UserFactory

from .factories import StoreProductFactory
from .factories import StoreProductImageFactory


class AuthMixin:
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)


class DetailedStoreProductImageTests(AuthMixin, APITestCase):
    def test_store_product_images_ordered_by_number(self):
        product = StoreProductFactory()
        StoreProductImageFactory(
            store_product=product,
            number=2,
            image_path="b.jpg",
            label="back",
        )
        StoreProductImageFactory(
            store_product=product,
            number=1,
            image_path="a.jpg",
            label="front",
        )
        StoreProductImageFactory(
            store_product=product,
            number=3,
            image_path="",
            label="empty",
        )

        url = reverse("api:storeproduct-detail", kwargs={"pk": product.id})
        response = self.client.get(url)

        assert response.status_code == 200
        # replaces the images_v1 _doc/{id} _source.store_product_images array
        assert response.data["store_product_images"] == ["a.jpg", "b.jpg"]
        assert response.data["verified"] is False

    def test_no_images_yields_empty_list(self):
        product = StoreProductFactory()
        url = reverse("api:storeproduct-detail", kwargs={"pk": product.id})
        response = self.client.get(url)
        assert response.data["store_product_images"] == []
