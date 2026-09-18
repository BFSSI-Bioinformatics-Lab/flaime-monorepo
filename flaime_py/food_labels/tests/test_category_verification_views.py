from django.urls import reverse
from rest_framework.test import APITestCase

from flaime_py.food_labels.models import StoreProductManualCategory
from flaime_py.users.tests.factories import UserFactory

from .factories import (
    CategoryFactory,
    CategorySchemeFactory,
    SourceFactory,
    StoreProductFactory,
    StoreProductImageFactory,
    StoreProductManualCategoryFactory,
    StoreProductPredictedCategoryFactory,
)

PREDICTIONS_URL = "api:category-verification-get-predictions"
CREATE_URL = "api:category-verification-create-verification"
UPDATE_URL = "api:category-verification-update-verification"


class CategoryVerificationBase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

        self.scheme = CategorySchemeFactory()
        self.parent = CategoryFactory(scheme=self.scheme, code="PARENT", level=1)
        self.leaf = CategoryFactory(
            scheme=self.scheme, parent_category=self.parent, code="LEAF", level=2
        )
        self.source = SourceFactory()

        self.products = []
        for i in range(3):
            product = StoreProductFactory(
                source=self.source, site_name=f"Product {i}", total_size=f"{i}00g"
            )
            StoreProductPredictedCategoryFactory(
                store_product=product, category=self.leaf, confidence=0.8 + i / 100
            )
            self.products.append(product)
        StoreProductImageFactory(store_product=self.products[0])

    def get_predictions(self, **params):
        return self.client.get(reverse(PREDICTIONS_URL), params)


class GetPredictionsTests(CategoryVerificationBase):
    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.get(reverse(PREDICTIONS_URL)).status_code == 401

    def test_requires_scheme_and_source(self):
        response = self.client.get(reverse(PREDICTIONS_URL))
        assert response.status_code == 400
        assert "scheme and source parameters are required" in str(response.data)

        assert self.get_predictions(scheme=self.scheme.id).status_code == 400
        assert self.get_predictions(source=self.source.id).status_code == 400

    def test_unverified_branch(self):
        response = self.get_predictions(scheme=self.scheme.id, source=self.source.id)
        assert response.status_code == 200
        assert response.data["count"] == 3

        row = response.data["results"][0]
        assert set(row) == {
            "id",
            "product_name",
            "product_size",
            "product_id",
            "store_product_images",
            "predictions",
        }
        assert row["predictions"][0]["category_code"] == "LEAF"

    def test_unverified_branch_excludes_manually_verified(self):
        StoreProductManualCategoryFactory(
            store_product=self.products[0], category=self.leaf, user=self.user
        )
        response = self.get_predictions(scheme=self.scheme.id, source=self.source.id)
        ids = {r["id"] for r in response.data["results"]}
        assert self.products[0].id not in ids
        assert response.data["count"] == 2

    def test_unverified_list_counts_diverge_on_non_leaf_predictions(self):
        # stats_only restricts to leaf-category predictions; the list path only
        # filters by scheme, so a non-leaf prediction is counted in the list but
        # not in the stats total. See NOTE in the handoff.
        other_product = StoreProductFactory(source=self.source)
        StoreProductPredictedCategoryFactory(
            store_product=other_product, category=self.parent
        )
        listed = self.get_predictions(scheme=self.scheme.id, source=self.source.id)
        stats = self.get_predictions(
            scheme=self.scheme.id, source=self.source.id, stats_only="true"
        )
        assert other_product.id in {r["id"] for r in listed.data["results"]}
        assert stats.data["total_count"] == 3

    def test_stats_only(self):
        StoreProductManualCategoryFactory(
            store_product=self.products[0], category=self.leaf, user=self.user
        )
        response = self.get_predictions(
            scheme=self.scheme.id, source=self.source.id, stats_only="true"
        )
        assert response.status_code == 200
        assert response.data == {
            "total_count": 3,
            "verified_count": 1,
            "unverified_count": 2,
        }

    def test_problematic_branch(self):
        StoreProductManualCategoryFactory(
            store_product=self.products[0],
            category=self.leaf,
            user=self.user,
            problematic_flag=True,
        )
        response = self.get_predictions(
            scheme=self.scheme.id, source=self.source.id, problematic="true"
        )
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["problematic_flag"] is True

    def test_problematic_branch_stats_only(self):
        StoreProductManualCategoryFactory(
            store_product=self.products[0],
            category=self.leaf,
            user=self.user,
            problematic_flag=True,
        )
        response = self.get_predictions(
            scheme=self.scheme.id,
            source=self.source.id,
            problematic="true",
            stats_only="true",
        )
        assert response.data == {"total_count": 1, "problematic_count": 1}

    def test_verified_branch_requires_user(self):
        response = self.get_predictions(
            scheme=self.scheme.id, source=self.source.id, verified="true"
        )
        assert response.status_code == 400
        assert "user parameter is required" in str(response.data)

    def test_verified_branch(self):
        StoreProductManualCategoryFactory(
            store_product=self.products[0], category=self.leaf, user=self.user
        )
        other_user = UserFactory()
        StoreProductManualCategoryFactory(
            store_product=self.products[1], category=self.leaf, user=other_user
        )
        response = self.get_predictions(
            scheme=self.scheme.id,
            source=self.source.id,
            verified="true",
            user=self.user.id,
        )
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["product_id"] == self.products[0].id

    def test_verified_branch_stats_only(self):
        StoreProductManualCategoryFactory(
            store_product=self.products[0], category=self.leaf, user=self.user
        )
        response = self.get_predictions(
            scheme=self.scheme.id,
            source=self.source.id,
            verified="true",
            user=self.user.id,
            stats_only="true",
        )
        assert response.data == {"total_count": 1, "user_verified_count": 1}


class CreateVerificationTests(CategoryVerificationBase):
    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(reverse(CREATE_URL), {})
        assert response.status_code == 401

    def test_create_with_store_product_key(self):
        response = self.client.post(
            reverse(CREATE_URL),
            {"store_product": self.products[0].id, "category": self.leaf.id},
        )
        assert response.status_code == 201
        obj = StoreProductManualCategory.objects.get(
            store_product=self.products[0], category=self.leaf
        )
        assert obj.user == self.user

    def test_create_with_legacy_product_key(self):
        response = self.client.post(
            reverse(CREATE_URL),
            {"product": self.products[1].id, "category": self.leaf.id},
        )
        assert response.status_code == 201
        assert StoreProductManualCategory.objects.filter(
            store_product=self.products[1], category=self.leaf
        ).exists()

    def test_missing_fields_rejected(self):
        response = self.client.post(
            reverse(CREATE_URL), {"category": self.leaf.id}
        )
        assert response.status_code == 400

    def test_duplicate_rejected(self):
        StoreProductManualCategoryFactory(
            store_product=self.products[0], category=self.leaf, user=self.user
        )
        response = self.client.post(
            reverse(CREATE_URL),
            {"store_product": self.products[0].id, "category": self.leaf.id},
        )
        assert response.status_code == 400
        assert "already been verified" in str(response.data)


class UpdateVerificationTests(CategoryVerificationBase):
    def setUp(self):
        super().setUp()
        self.verification = StoreProductManualCategoryFactory(
            store_product=self.products[0], category=self.leaf, user=self.user
        )
        self.url = reverse(UPDATE_URL, kwargs={"pk": self.verification.pk})

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        assert self.client.patch(self.url, {"problematic_flag": True}).status_code == 401

    def test_patch_updates_fields(self):
        response = self.client.patch(
            self.url, {"problematic_flag": True, "notes": "needs review"}
        )
        assert response.status_code == 200
        self.verification.refresh_from_db()
        assert self.verification.problematic_flag is True
        assert self.verification.notes == "needs review"

    def test_patch_can_change_category(self):
        new_leaf = CategoryFactory(
            scheme=self.scheme, parent_category=self.parent, code="LEAF2", level=2
        )
        response = self.client.patch(self.url, {"category": new_leaf.id})
        assert response.status_code == 200
        self.verification.refresh_from_db()
        assert self.verification.category == new_leaf

    def test_missing_verification_returns_404(self):
        url = reverse(UPDATE_URL, kwargs={"pk": 999999})
        response = self.client.patch(url, {"problematic_flag": True})
        assert response.status_code == 404
