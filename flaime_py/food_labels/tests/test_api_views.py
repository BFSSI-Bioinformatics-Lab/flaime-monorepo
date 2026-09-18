from django.urls import reverse
from rest_framework.test import APITestCase

from flaime_py.food_labels.models import StorageConditions
from flaime_py.users.tests.factories import UserFactory

from .factories import (
    BatchFactory,
    CategoryFactory,
    CategorySchemeFactory,
    NutrientFactory,
    SourceFactory,
    StoreFactory,
    StoreProductFactory,
    StoreProductManualCategoryFactory,
    StoreProductPredictedCategoryFactory,
)


class AuthMixin:
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)


class UserInfoTests(AuthMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("api:user_info")

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.get(self.url).status_code == 401

    def test_returns_current_user(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert response.data["id"] == self.user.id
        assert response.data["email"] == self.user.email
        assert set(response.data) >= {
            "id",
            "username",
            "email",
            "groups",
            "is_staff",
            "is_superuser",
        }
        assert response.data["groups"] == []


class SearchOptionsTests(AuthMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("search_options")

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.get(self.url).status_code == 401

    def test_payload_shape(self):
        source = SourceFactory()
        store = StoreFactory()
        BatchFactory(region="Ontario")
        BatchFactory(region="")
        BatchFactory(region=None)

        response = self.client.get(self.url)
        assert response.status_code == 200

        assert {"value": source.id, "label": source.name} in response.data["sources"]
        assert {"value": store.id, "label": store.name} in response.data["stores"]
        assert response.data["regions"] == [{"value": "Ontario", "label": "Ontario"}]
        assert StorageConditions.SHELF_STABLE.value in {
            o["value"] for o in response.data["storage"]
        }
        assert len(response.data["packaging"]) > 0

    def test_excludes_soft_deleted(self):
        SourceFactory(name="Gone", deleted=True)
        response = self.client.get(self.url)
        assert "Gone" not in [s["label"] for s in response.data["sources"]]


class CategoryTreeViewTests(AuthMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("api:category-tree")
        self.scheme = CategorySchemeFactory()
        self.root = CategoryFactory(scheme=self.scheme, code="ROOT", level=1)
        self.child = CategoryFactory(
            scheme=self.scheme, parent_category=self.root, code="CHILD", level=2
        )
        other_scheme = CategorySchemeFactory()
        self.other_root = CategoryFactory(scheme=other_scheme, code="OTHER", level=1)

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.get(self.url).status_code == 401

    def test_returns_nested_tree(self):
        response = self.client.get(self.url, {"scheme": self.scheme.id})
        assert response.status_code == 200
        assert len(response.data) == 1

        root = response.data[0]
        assert root["code"] == "ROOT"
        assert len(root["children"]) == 1
        assert root["children"][0]["code"] == "CHILD"
        assert root["children"][0]["children"] is None

    def test_scheme_filter(self):
        response = self.client.get(self.url, {"scheme": self.scheme.id})
        codes = {c["code"] for c in response.data}
        assert "OTHER" not in codes

    def test_excludes_soft_deleted(self):
        CategoryFactory(scheme=self.scheme, parent_category=None, code="DEL", deleted=True)
        response = self.client.get(self.url, {"scheme": self.scheme.id})
        assert "DEL" not in {c["code"] for c in response.data}


class SourceViewSetTests(AuthMixin, APITestCase):
    def test_list_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.get(reverse("api:source-list")).status_code == 401

    def test_list_and_retrieve(self):
        source = SourceFactory()
        SourceFactory(name="Deleted", deleted=True)

        list_response = self.client.get(reverse("api:source-list"))
        assert list_response.status_code == 200
        names = {s["name"] for s in list_response.data}
        assert source.name in names
        assert "Deleted" not in names

        detail = self.client.get(reverse("api:source-detail", kwargs={"pk": source.id}))
        assert detail.status_code == 200
        assert detail.data["id"] == source.id
        assert "created_datetime" in detail.data

    def test_full_action(self):
        SourceFactory()
        response = self.client.get(reverse("api:source-full"))
        assert response.status_code == 200
        assert "created_datetime" in response.data[0]

    def test_collection_stats(self):
        source = SourceFactory()
        StoreProductFactory(source=source, fop_flag=True, verified=True)
        StoreProductFactory(source=source, fop_flag=False, verified=False)
        StoreProductFactory(source=source, fop_flag=False, verified=False, deleted=True)

        url = reverse("api:source-collection-stats", kwargs={"pk": source.id})
        response = self.client.get(url)
        assert response.status_code == 200
        # Existing keys are unchanged...
        assert {
            "source_id": response.data["source_id"],
            "total": response.data["total"],
            "with_fop": response.data["with_fop"],
            "fop_percentage": response.data["fop_percentage"],
            "manually_reviewed": response.data["manually_reviewed"],
            "reviewed_percentage": response.data["reviewed_percentage"],
        } == {
            "source_id": source.id,
            "total": 2,
            "with_fop": 1,
            "fop_percentage": 50.0,
            "manually_reviewed": 1,
            "reviewed_percentage": 50.0,
        }
        # ...plus the new nutrient / additive blocks.
        assert isinstance(response.data["nutrients"], list)
        assert isinstance(response.data["additives"], list)

    def test_collection_stats_no_products(self):
        source = SourceFactory()
        url = reverse("api:source-collection-stats", kwargs={"pk": source.id})
        response = self.client.get(url)
        assert response.data["total"] == 0
        assert response.data["fop_percentage"] == 0


class CategorySchemeViewSetTests(AuthMixin, APITestCase):
    def test_list_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.get(reverse("api:categoryscheme-list")).status_code == 401

    def test_list_includes_category_count(self):
        scheme = CategorySchemeFactory()
        CategoryFactory(scheme=scheme)
        CategoryFactory(scheme=scheme, deleted=True)

        response = self.client.get(reverse("api:categoryscheme-list"))
        assert response.status_code == 200
        row = next(s for s in response.data if s["id"] == scheme.id)
        assert row["category_count"] == 1

    def test_retrieve_is_detailed(self):
        scheme = CategorySchemeFactory()
        CategoryFactory(scheme=scheme, parent_category=None)
        response = self.client.get(
            reverse("api:categoryscheme-detail", kwargs={"pk": scheme.id})
        )
        assert response.status_code == 200
        assert "categories" in response.data

    def test_full_action(self):
        CategorySchemeFactory()
        response = self.client.get(reverse("api:categoryscheme-full"))
        assert response.status_code == 200
        assert "categories" in response.data[0]


class StoreViewSetTests(AuthMixin, APITestCase):
    def test_list_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.get(reverse("api:store-list")).status_code == 401

    def test_list_retrieve_full(self):
        store = StoreFactory()
        StoreFactory(name="Closed", deleted=True)

        listed = self.client.get(reverse("api:store-list"))
        assert listed.status_code == 200
        names = {s["name"] for s in listed.data}
        assert store.name in names
        assert "Closed" not in names

        detail = self.client.get(reverse("api:store-detail", kwargs={"pk": store.id}))
        assert detail.status_code == 200
        assert "created_datetime" in detail.data

        full = self.client.get(reverse("api:store-full"))
        assert full.status_code == 200
        assert "created_datetime" in full.data[0]


class NutrientViewSetTests(AuthMixin, APITestCase):
    def test_list_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.get(reverse("api:nutrient-list")).status_code == 401

    def test_list_retrieve_full(self):
        nutrient = NutrientFactory()
        NutrientFactory(deleted=True)

        listed = self.client.get(reverse("api:nutrient-list"))
        assert listed.status_code == 200
        ids = {n["id"] for n in listed.data}
        assert nutrient.id in ids
        assert len(listed.data) == 1

        detail = self.client.get(
            reverse("api:nutrient-detail", kwargs={"pk": nutrient.id})
        )
        assert detail.status_code == 200
        assert detail.data["nutrient_code"] == nutrient.nutrient_code

        full = self.client.get(reverse("api:nutrient-full"))
        assert full.status_code == 200
        assert "created_datetime" in full.data[0]


class StoreProductViewSetTests(AuthMixin, APITestCase):
    def test_list_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.get(reverse("api:storeproduct-list")).status_code == 401

    def test_list_is_simple_serializer(self):
        product = StoreProductFactory(site_name="Cookies", sku="SKU1")
        StoreProductFactory(deleted=True)

        response = self.client.get(reverse("api:storeproduct-list"))
        assert response.status_code == 200
        assert len(response.data) == 1
        row = response.data[0]
        assert row["id"] == product.id
        assert row["site_name"] == "Cookies"
        assert "site_description" not in row

    def test_retrieve_is_detailed_serializer(self):
        scheme = CategorySchemeFactory()
        category = CategoryFactory(scheme=scheme)
        product = StoreProductFactory(site_name="Detailed Product")
        StoreProductManualCategoryFactory(
            store_product=product, category=category, user=self.user
        )
        StoreProductPredictedCategoryFactory(store_product=product, category=category)

        response = self.client.get(
            reverse("api:storeproduct-detail", kwargs={"pk": product.id})
        )
        assert response.status_code == 200
        assert response.data["id"] == product.id
        assert response.data["site_name"] == "Detailed Product"
        assert "categories" in response.data
        assert scheme.name in response.data["categories"]

    def test_full_action(self):
        StoreProductFactory()
        response = self.client.get(reverse("api:storeproduct-full"))
        assert response.status_code == 200
        assert len(response.data) == 1
        assert "categories" in response.data[0]
