from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.conf import settings

from flaime_py.users.api.views import UserViewSet
from flaime_py.food_labels.api.views import SourceViewSet, StoreViewSet, NutrientViewSet, StoreProductViewSet, CategorySchemeViewSet
from flaime_py.food_labels.api.category_verification_views import CategoryVerificationViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register("users", UserViewSet)
router.register("sources", SourceViewSet)
router.register("stores", StoreViewSet)
router.register("nutrients", NutrientViewSet)
router.register("storeproducts", StoreProductViewSet)
router.register("categoryschemes", CategorySchemeViewSet)
router.register("category-verifications", CategoryVerificationViewSet, basename='category-verification')

app_name = "api"
urlpatterns = router.urls

urlpatterns += [
    path('', include('flaime_py.food_labels.urls')),
]