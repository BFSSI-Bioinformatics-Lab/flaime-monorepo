from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from django.db.models import OuterRef, Exists, Subquery, Prefetch
from ..models import (
    StoreProduct,
    Category,
    StoreProductManualCategory,
    StoreProductPredictedCategory,
)
from .category_verification_serializers import (
    ProductPredictionSerializer, 
    ManualCategoryCreateSerializer,
    ManualCategoryUpdateSerializer,
    ManualVerificationSerializer,
    ManualVerificationWithPredictionsSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class CategoryVerificationViewSet(viewsets.GenericViewSet):
    queryset = StoreProductManualCategory.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='scheme',
                description='Scheme ID to filter predictions',
                required=True,
                type=int
            ),
            OpenApiParameter(
                name='source',
                description='Source ID to filter store products',
                required=True,
                type=int
            ),
            OpenApiParameter(
                name='stats_only',
                description='Return only counts instead of full product data',
                required=False,
                type=bool,
                default=False
            ),
            OpenApiParameter(
                name='problematic',
                description='Return only problematic manual verifications',
                required=False,
                type=bool
            ),
            OpenApiParameter(
                name='verified',
                description='Return verified products (requires user parameter)',
                required=False,
                type=bool
            ),
            OpenApiParameter(
                name='user',
                description='User ID for filtering verified products',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='page',
                description='Page number',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='page_size',
                description='Number of items per page (max 200)',
                required=False,
                type=int
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Success",
                examples=[
                    OpenApiExample(
                        "Product Predictions",
                        value={
                            "count": 850,
                            "next": "http://api.example.com/predictions?page=2",
                            "previous": None,
                            "results": [{"id": 123, "product_name": "Sample Product"}]
                        }
                    ),
                    OpenApiExample(
                        "Stats Only",
                        value={"total_count": 850, "verified_count": 234}
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['get'])
    def get_predictions(self, request):
        scheme_id = request.query_params.get('scheme')
        source_id = request.query_params.get('source')
        stats_only = request.query_params.get('stats_only', 'false').lower() == 'true'
        problematic = request.query_params.get('problematic')
        verified = request.query_params.get('verified')
        user_id = request.query_params.get('user')

        if not scheme_id or not source_id:
            return Response(
                {"error": "scheme and source parameters are required"},
                status=400
            )

        if problematic and problematic.lower() == 'true':
            return self._get_problematic_verifications(scheme_id, source_id, stats_only)
        
        if verified and verified.lower() == 'true':
            if not user_id:
                return Response(
                    {"error": "user parameter is required when verified=true"},
                    status=400
                )
            return self._get_user_verifications(scheme_id, source_id, user_id, stats_only)

        return self._get_unverified_predictions(scheme_id, source_id, stats_only)

    def _get_problematic_verifications(self, scheme_id, source_id, stats_only):
        queryset = StoreProductManualCategory.objects.filter(
            problematic_flag=True,
            category__scheme_id=scheme_id,
            store_product__source_id=source_id,
        ).select_related('store_product', 'category', 'user').distinct()

        if stats_only:
            return Response({
                'total_count': queryset.count(),
                'problematic_count': queryset.count()
            })

        queryset = queryset.prefetch_related(
            Prefetch(
                'store_product__predicted_categories',
                queryset=StoreProductPredictedCategory.objects.filter(
                    category__scheme_id=scheme_id
                ).select_related('category')
            )
        ).order_by('-date_added')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ManualVerificationWithPredictionsSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ManualVerificationWithPredictionsSerializer(queryset, many=True)
        return Response(serializer.data)

    def _get_user_verifications(self, scheme_id, source_id, user_id, stats_only):
        queryset = StoreProductManualCategory.objects.filter(
            user_id=user_id,
            category__scheme_id=scheme_id,
            store_product__source_id=source_id,
        ).select_related('store_product', 'category', 'user').distinct()

        if stats_only:
            return Response({
                'total_count': queryset.count(),
                'user_verified_count': queryset.count()
            })

        queryset = queryset.prefetch_related(
            Prefetch(
                'store_product__predicted_categories',
                queryset=StoreProductPredictedCategory.objects.filter(
                    category__scheme_id=scheme_id
                ).select_related('category')
            )
        ).order_by('-date_added')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ManualVerificationWithPredictionsSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ManualVerificationWithPredictionsSerializer(queryset, many=True)
        return Response(serializer.data)

    def _get_unverified_predictions(self, scheme_id, source_id, stats_only):
        has_manual_verification = StoreProductManualCategory.objects.filter(
            store_product=OuterRef('pk'),
            category__scheme_id=scheme_id
        ).values('id')

        leaf_categories = Category.objects.filter(
            scheme_id=scheme_id,
            children__isnull=True
        ).values('id')

        products_with_predictions = (
            StoreProduct.objects
            .filter(
                source_id=source_id,
                predicted_categories__category__in=leaf_categories,
            )
            .distinct()
        )

        if stats_only:
            total_count = products_with_predictions.count()

            verified_count = products_with_predictions.filter(
                manual_categories__category__scheme_id=scheme_id
            ).distinct().count()

            return Response({
                'total_count': total_count,
                'verified_count': verified_count,
                'unverified_count': total_count - verified_count
            })

        store_products = (
            StoreProduct.objects
            .filter(
                source_id=source_id,
                predicted_categories__category__scheme_id=scheme_id,
            )
            .exclude(Exists(has_manual_verification))
            .annotate(
                top_category_code=Subquery(
                    StoreProductPredictedCategory.objects
                    .filter(
                        store_product=OuterRef('pk'),
                        category__scheme_id=scheme_id
                    )
                    .order_by('-confidence')
                    .values('category__code')[:1]
                )
            )
            .prefetch_related(
                'storeproductimage_set',
                Prefetch(
                    'predicted_categories',
                    queryset=StoreProductPredictedCategory.objects.filter(
                        category__scheme_id=scheme_id
                    ).select_related('category')
                )
            )
            .distinct()
            .order_by('top_category_code', 'id')
        )

        page = self.paginate_queryset(store_products)
        if page is not None:
            serializer = ProductPredictionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductPredictionSerializer(store_products, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=ManualCategoryCreateSerializer,
        responses={201: ManualCategoryCreateSerializer},
        description='Create a new category verification'
    )
    @action(detail=False, methods=['post'])
    def create_verification(self, request):
        serializer = ManualCategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    @extend_schema(
        request=ManualCategoryUpdateSerializer,
        responses={200: ManualCategoryUpdateSerializer},
        description='Update an existing category verification'
    )
    @action(detail=True, methods=['patch', 'put'])
    def update_verification(self, request, pk=None):
        try:
            verification = StoreProductManualCategory.objects.get(pk=pk)
        except StoreProductManualCategory.DoesNotExist:
            return Response(
                {"error": "Verification not found"},
                status=404
            )
        
        partial = request.method == 'PATCH'
        serializer = ManualCategoryUpdateSerializer(
            verification,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=200)