from django.test import override_settings
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

    @override_settings(AZURE_IMAGES_READ_SAS_URL="")
    def test_no_blob_urls_without_blob_storage(self):
        product = StoreProductFactory()
        StoreProductImageFactory(store_product=product, number=1, image_path="a.jpg")
        url = reverse("api:storeproduct-detail", kwargs={"pk": product.id})
        response = self.client.get(url)
        # None values are dropped from the payload (to_representation)
        assert "store_product_image_urls" not in response.data

    @override_settings(
        AZURE_IMAGES_READ_SAS_URL="https://acct.blob.core.windows.net/datahub/flaime/?sp=r&sig=abc%3D",
    )
    def test_blob_urls(self):
        product = StoreProductFactory()
        StoreProductImageFactory(
            store_product=product, number=2, image_path="2025/1/front_IMG_1[1].JPG",
        )
        StoreProductImageFactory(
            store_product=product, number=1, image_path="FLIP/pic/prod1_photo2_nft",
        )
        StoreProductImageFactory(store_product=product, number=3, image_path="")
        url = reverse("api:storeproduct-detail", kwargs={"pk": product.id})
        response = self.client.get(url)

        base = "https://acct.blob.core.windows.net/datahub/flaime"
        sas = "?sp=r&sig=abc%3D"
        assert response.data["store_product_image_urls"] == [
            {
                "full": f"{base}/images/FLIP/pic/prod1_photo2_nft{sas}",
                "thumb": f"{base}/thumb/FLIP/pic/prod1_photo2_nft{sas}",
            },
            {
                "full": f"{base}/images/2025/1/front_IMG_1%5B1%5D.JPG{sas}",
                "thumb": f"{base}/thumb/2025/1/front_IMG_1%5B1%5D.JPG{sas}",
            },
        ]
