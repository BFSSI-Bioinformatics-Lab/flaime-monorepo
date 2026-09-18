from rest_framework import viewsets, serializers, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, inline_serializer
from drf_spectacular.types import OpenApiTypes

from django.conf import settings
from django.http import StreamingHttpResponse
from django.views.generic import TemplateView
from django.db.models import Prefetch, Count

from ..models import (
    Category,
    CategoryScheme,
    Nutrient,
    Source,
    Store,
    StoreProduct,
    Batch,
    StoreProductImage,
    StoreProductManualCategory,
    StoreProductPredictedCategory,
    StoreProductUPC,
    StorageConditions,
    PackagingChoices,
)

from .serializers import (
    DetailedNutrientSerializer,
    SimpleNutrientSerializer,
    SimpleSourceSerializer,
    DetailedSourceSerializer,
    SimpleStoreSerializer,
    DetailedStoreSerializer,
)

from .product_serializers import (
    SimpleStoreProductSerializer,
    DetailedStoreProductSerializer,
    StoreProductSearchResultSerializer,
)

from .category_serializers import (
    CategoryTreeSerializer,
    CategorySchemeSerializer,
    DetailedCategorySchemeSerializer,
)

from .pagination import StoreProductSearchPagination
from .search import (
    StoreProductSearchRequestSerializer,
    build_search_queryset,
    apply_ordering,
)
from .collection_stats import compute_collection_stats
from ..exports import EXPORT_COLUMN_CHOICES, iter_csv


def _collection_stats_response(name):
    """Typed schema for the collection-stats payload (shared by the source-scoped
    and all-products endpoints). ``name`` keeps the two component names distinct."""
    return inline_serializer(
        name=name,
        fields={
            "source_id": serializers.IntegerField(required=False),
            "total": serializers.IntegerField(),
            "with_fop": serializers.IntegerField(),
            "fop_percentage": serializers.FloatField(),
            "manually_reviewed": serializers.IntegerField(),
            "reviewed_percentage": serializers.FloatField(),
            "nutrients": inline_serializer(
                name=f"{name}Nutrient",
                many=True,
                fields={
                    "label": serializers.CharField(),
                    "nutrient_ids": serializers.ListField(
                        child=serializers.IntegerField()
                    ),
                    "unit": serializers.CharField(),
                    "count": serializers.IntegerField(),
                    "mean": serializers.FloatField(allow_null=True),
                    "median": serializers.FloatField(allow_null=True),
                    "min": serializers.FloatField(allow_null=True),
                    "max": serializers.FloatField(allow_null=True),
                },
            ),
            "additives": inline_serializer(
                name=f"{name}Additive",
                many=True,
                fields={
                    "label": serializers.CharField(),
                    "term": serializers.CharField(),
                    "count": serializers.IntegerField(),
                    "percentage": serializers.FloatField(),
                },
            ),
        },
    )

@extend_schema(
    responses=inline_serializer(
        name='UserInfoResponse',
        fields={
            'id': serializers.IntegerField(),
            'username': serializers.CharField(),
            'email': serializers.EmailField(),
            'groups': serializers.ListField(child=serializers.CharField()),
            'is_staff': serializers.BooleanField(),
            'is_superuser': serializers.BooleanField(),
        }
    )
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    user = request.user
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "groups": list(user.groups.values_list("name", flat=True)),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        }
    )

@extend_schema(
    responses=inline_serializer(
        name='SearchOptionsResponse',
        fields={
            'sources': serializers.ListField(child=serializers.DictField()),
            'stores': serializers.ListField(child=serializers.DictField()),
            'regions': serializers.ListField(child=serializers.DictField()),
            'storage': serializers.ListField(child=serializers.DictField()),
            'packaging': serializers.ListField(child=serializers.DictField()),
        }
    )
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_search_options(request):
    sources = Source.objects.filter(deleted=False).values("id", "name")
    stores = Store.objects.filter(deleted=False).values("id", "name")
    region_list = (
        Batch.objects.exclude(region__isnull=True)
        .exclude(region__exact="")
        .values_list("region", flat=True)
        .distinct()
    )

    return Response(
        {
            "sources": [{"value": s["id"], "label": s["name"]} for s in sources],
            "stores": [{"value": s["id"], "label": s["name"]} for s in stores],
            "regions": [{"value": r, "label": r} for r in region_list],
            "storage": [
                {"value": c[0], "label": c[1]} for c in StorageConditions.choices
            ],
            "packaging": [
                {"value": c[0], "label": c[1]} for c in PackagingChoices.choices
            ],
        }
    )


class CategoryTreeView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="scheme",
                description="Filter categories by scheme ID",
                required=False,
                type=int,
            )
        ],
        responses=CategoryTreeSerializer(many=True),  # Changed this
        description="Get hierarchical category tree with optional scheme filtering",
    )
    def get(self, request):
        scheme_id = request.query_params.get("scheme")
        queryset = Category.objects.filter(deleted=False)
        if scheme_id:
            queryset = queryset.filter(scheme_id=scheme_id)

        child_qs = queryset.select_related("scheme")

        categories = (
            queryset.filter(parent_category__isnull=True)
            .prefetch_related(
                Prefetch(
                    "children",
                    queryset=child_qs.prefetch_related(
                        Prefetch(
                            "children",
                            queryset=child_qs.prefetch_related(
                                Prefetch("children", queryset=child_qs)
                            ),
                        )
                    ),
                )
            )
            .select_related("scheme")
        )

        serializer = CategoryTreeSerializer(categories, many=True)  # Changed this
        return Response(serializer.data)


class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.filter(deleted=False)
    serializer_class = SimpleSourceSerializer

    def get_serializer_class(self):
        if self.action == "retrieve" or self.action == "full":
            return DetailedSourceSerializer
        return SimpleSourceSerializer

    @action(detail=False, methods=["get"], url_path="full")
    def full(self, request):
        sources = self.get_queryset()
        serializer = self.get_serializer(sources, many=True)
        return Response(serializer.data)

    @extend_schema(responses=_collection_stats_response("SourceCollectionStats"))
    @action(detail=True, methods=["get"], url_path="collection-stats")
    def collection_stats(self, request, pk=None):
        # Existing keys unchanged; `nutrients` and `additives` added so the
        # Collection Stats report no longer needs Elasticsearch.
        qs = StoreProduct.objects.filter(source_id=pk, deleted=False)
        return Response({"source_id": int(pk), **compute_collection_stats(qs)})


class CategorySchemeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CategoryScheme.objects.all()
    serializer_class = CategorySchemeSerializer

    def get_serializer_class(self):
        if self.action == "retrieve" or self.action == "full":
            return DetailedCategorySchemeSerializer
        return CategorySchemeSerializer

    @action(detail=False, methods=["get"], url_path="full")
    def full(self, request):
        schemes = self.get_queryset()
        serializer = self.get_serializer(schemes, many=True)
        return Response(serializer.data)


class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.filter(deleted=False)
    serializer_class = SimpleStoreSerializer

    def get_serializer_class(self):
        if self.action == "retrieve" or self.action == "full":
            return DetailedStoreSerializer
        return SimpleStoreSerializer

    @action(detail=False, methods=["get"], url_path="full")
    def full(self, request):
        stores = self.get_queryset()
        serializer = self.get_serializer(stores, many=True)
        return Response(serializer.data)


class NutrientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Nutrient.objects.filter(deleted=False)
    serializer_class = SimpleNutrientSerializer

    def get_serializer_class(self):
        if self.action == "retrieve" or self.action == "full":
            return DetailedNutrientSerializer
        return SimpleNutrientSerializer

    @action(detail=False, methods=["get"], url_path="full")
    def full(self, request):
        nutrients = self.get_queryset()
        serializer = self.get_serializer(nutrients, many=True)
        return Response(serializer.data)


@extend_schema_view(
    retrieve=extend_schema(
        description="Get detailed information for a single store product",
        responses=DetailedStoreProductSerializer,
    ),
    list=extend_schema(
        description="List store products with basic information",
        responses=SimpleStoreProductSerializer,
    ),
)
class StoreProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StoreProduct.objects.filter(deleted=False)

    def get_serializer_class(self):
        if self.action in ["retrieve", "full"]:
            return DetailedStoreProductSerializer
        return SimpleStoreProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["retrieve", "full"]:
            return queryset.select_related(
                "store",
                "source",
                "brand",
                "serving_size_unit",
                "company",
                "label_flags",
            ).prefetch_related(
                "nutrition_facts",
                "nutrition_facts__nutrient",
                "nutrition_facts__amount_unit",
                "allergens_warnings",
                Prefetch(
                    "storeproductupc_set",
                    queryset=StoreProductUPC.objects.select_related("upc"),
                ),
                Prefetch(
                    "manual_categories",
                    queryset=StoreProductManualCategory.objects.select_related(
                        "category", "category__scheme", "category__parent_category", "user"
                    ),
                ),
                Prefetch(
                    "predicted_categories",
                    queryset=StoreProductPredictedCategory.objects.select_related(
                        "category", "category__scheme", "category__parent_category"
                    ),
                ),
                Prefetch(
                    "storeproductimage_set",
                    queryset=StoreProductImage.objects.order_by("number"),
                ),
            )
        return queryset

    @extend_schema(
        description="Get full details for all store products",
        responses=DetailedStoreProductSerializer(many=True),
    )
    @action(detail=False, methods=["get"], url_path="full")
    def full(self, request):
        store_products = self.get_queryset()
        serializer = self.get_serializer(store_products, many=True)
        return Response(serializer.data)

    def _search_queryset(self, request):
        """Validate the shared search body and return the filtered (un-ordered,
        un-prefetched) queryset plus the validated data."""
        payload = StoreProductSearchRequestSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        data = payload.validated_data
        queryset = build_search_queryset(data.get("text"), data.get("filters"))
        return queryset, data

    @extend_schema(
        request=StoreProductSearchRequestSerializer,
        responses=inline_serializer(
            name="PaginatedStoreProductSearch",
            fields={
                "count": serializers.IntegerField(),
                "next": serializers.CharField(allow_null=True),
                "previous": serializers.CharField(allow_null=True),
                "results": StoreProductSearchResultSerializer(many=True),
            },
        ),
        description=(
            "Paginated product search. Replaces the frontend's direct "
            "Elasticsearch `data/_search` queries (Product Finder, Advanced "
            "Search, Product Browser). Returns the standard DRF "
            "`{count, next, previous, results}` envelope. `page` / `page_size` "
            "may be given in the body or as query parameters."
        ),
    )
    @action(detail=False, methods=["post"], url_path="search")
    def search(self, request):
        queryset, data = self._search_queryset(request)
        queryset = apply_ordering(queryset, data.get("sort"))
        queryset = queryset.select_related(
            "source", "store", "scrape_batch"
        ).prefetch_related(
            Prefetch(
                "manual_categories",
                queryset=StoreProductManualCategory.objects.select_related("category"),
            ),
            "allergens_warnings",
        )

        paginator = StoreProductSearchPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = StoreProductSearchResultSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        request=inline_serializer(
            name="StoreProductExportRequest",
            fields={
                "text": serializers.DictField(required=False),
                "filters": serializers.DictField(required=False),
                "columns": serializers.ChoiceField(
                    choices=EXPORT_COLUMN_CHOICES, default="simple"
                ),
            },
        ),
        responses={
            (200, "text/csv"): OpenApiTypes.STR,
            400: inline_serializer(
                name="StoreProductExportError",
                fields={"detail": serializers.CharField()},
            ),
        },
        description=(
            "Server-side CSV export using the same filter body as `/search/` "
            "plus a `columns` layout (`simple`, `full`, `full_supplemented`). "
            "Streams the result; rejects requests over EXPORT_MAX_ROWS."
        ),
    )
    @action(detail=False, methods=["post"], url_path="export")
    def export(self, request):
        columns = request.data.get("columns", "simple")
        if columns not in EXPORT_COLUMN_CHOICES:
            return Response(
                {"detail": f"columns must be one of {EXPORT_COLUMN_CHOICES}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset, _data = self._search_queryset(request)

        total = queryset.count()
        if total > settings.EXPORT_MAX_ROWS:
            return Response(
                {
                    "detail": (
                        f"Export of {total} rows exceeds the limit of "
                        f"{settings.EXPORT_MAX_ROWS}. Narrow your filters."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = StreamingHttpResponse(
            iter_csv(queryset, columns), content_type="text/csv"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="storeproducts_{columns}.csv"'
        )
        return response

    @extend_schema(
        request=StoreProductSearchRequestSerializer,
        responses=inline_serializer(
            name="StoreCount",
            many=True,
            fields={
                "store": serializers.CharField(),
                "count": serializers.IntegerField(),
            },
        ),
        description=(
            "Per-store product counts for the given filter body, as a list "
            "ordered by count desc. Replaces the Product Browser "
            "`store.name.keyword` terms aggregation."
        ),
    )
    @action(detail=False, methods=["post"], url_path="store-counts")
    def store_counts(self, request):
        queryset, _data = self._search_queryset(request)
        rows = (
            queryset.values("store__name")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count", "store__name")
        )
        return Response(
            [{"store": row["store__name"], "count": row["count"]} for row in rows]
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="source",
                description="Restrict the stats to a single source id",
                required=False,
                type=int,
            )
        ],
        responses=_collection_stats_response("CollectionStats"),
        description=(
            "Collection statistics across all products (or one source via "
            "`?source=`): FOP / review counts, nutrient stats (count/mean/"
            "median/min/max) and additive prevalence. Replaces the Collection "
            "Stats report's Elasticsearch aggregations."
        ),
    )
    @action(detail=False, methods=["get"], url_path="collection-stats")
    def collection_stats(self, request):
        queryset = StoreProduct.objects.filter(deleted=False)
        source_id = request.query_params.get("source")
        if source_id:
            queryset = queryset.filter(source_id=source_id)
        return Response(compute_collection_stats(queryset))
