"""Query construction for POST /api/storeproducts/search/ (and the export /
store-counts endpoints, which take the same request body).

The frontend used to build Elasticsearch bool/DSL queries in the browser and
POST them straight to ES.  These helpers reproduce the equivalent filtering
against Postgres via the ORM.  Everything is a plain function so it can be unit
tested without going through the view.
"""

from django.db.models import Q
from rest_framework import serializers

from ..models import PackagingChoices
from ..models import StorageConditions
from ..models import StoreProduct

# sort.field (API) -> ORM field path.  ``price`` is a FloatField so it sorts
# numerically (ES sorted reading_price.keyword lexically - this is the fix).
SEARCH_ORDERING_FIELDS = {
    "id": "id",
    "external_id": "external_id",
    "site_name": "site_name",
    "price": "price",
    "source": "source__name",
    "store": "store__name",
    "date": "scrape_batch__scrape_datetime",
    "region": "location__name",
    "storage_condition": "storage_condition",
    "primary_package_material": "primary_package_material",
}

# Cap on the number of values accepted in a single *_list (Product Finder
# submits up to 1000 names/IDs at once).
MAX_LIST_ITEMS = 1000


# --------------------------------------------------------------------------- #
# Request body validation
# --------------------------------------------------------------------------- #
class _SearchTextSerializer(serializers.Serializer):
    site_name = serializers.CharField(required=False, allow_blank=True)
    site_name_list = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        max_length=MAX_LIST_ITEMS,
    )
    id_list = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        max_length=MAX_LIST_ITEMS,
    )
    external_id_list = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        max_length=MAX_LIST_ITEMS,
    )
    raw_upc_list = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        max_length=MAX_LIST_ITEMS,
    )
    nielsen_upc_list = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        max_length=MAX_LIST_ITEMS,
    )


class _IngredientsFilterSerializer(serializers.Serializer):
    terms = serializers.ListField(child=serializers.CharField(), allow_empty=False)
    mode = serializers.ChoiceField(choices=["all", "any"], default="all")


class _NutrientFilterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    min = serializers.FloatField(required=False, allow_null=True)
    max = serializers.FloatField(required=False, allow_null=True)


class _SearchFiltersSerializer(serializers.Serializer):
    source = serializers.IntegerField(required=False)
    store = serializers.IntegerField(required=False)
    region = serializers.CharField(required=False)  # a Location code, e.g. "ON"
    category = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    storage_condition = serializers.ChoiceField(
        choices=StorageConditions.values,
        required=False,
    )
    primary_package_material = serializers.ChoiceField(
        choices=PackagingChoices.values,
        required=False,
    )
    secondary_package_material = serializers.ChoiceField(
        choices=PackagingChoices.values,
        required=False,
    )
    ingredients = _IngredientsFilterSerializer(required=False)
    allergens = serializers.CharField(required=False)
    nutrient = _NutrientFilterSerializer(required=False)


class _SearchSortSerializer(serializers.Serializer):
    field = serializers.ChoiceField(choices=sorted(SEARCH_ORDERING_FIELDS))
    order = serializers.ChoiceField(choices=["asc", "desc"], default="asc")


class StoreProductSearchRequestSerializer(serializers.Serializer):
    """Shared request body for /search/, /store-counts/ and /export/."""

    text = _SearchTextSerializer(required=False)
    filters = _SearchFiltersSerializer(required=False)
    sort = _SearchSortSerializer(required=False)
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(required=False, min_value=1)


# --------------------------------------------------------------------------- #
# Queryset construction
# --------------------------------------------------------------------------- #
def build_search_queryset(text=None, filters=None):
    """Return a ``distinct()`` StoreProduct queryset for the given (validated)
    ``text`` and ``filters`` dicts.  No ordering / prefetching is applied - the
    caller adds those."""
    text = text or {}
    filters = filters or {}
    qs = StoreProduct.objects.filter(deleted=False)

    site_name = (text.get("site_name") or "").strip()
    if site_name:
        # case-insensitive substring; accelerated in prod by the pg_trgm GIN
        # index on store_products.site_name.
        qs = qs.filter(site_name__icontains=site_name)

    # Exact-match lists: OR'd within a list, AND'd across the different keys.
    for key, lookup in (
        ("site_name_list", "site_name__in"),
        ("id_list", "id__in"),
        ("external_id_list", "external_id__in"),
        ("raw_upc_list", "raw_upc__in"),
        ("nielsen_upc_list", "nielsen_upc__in"),
    ):
        values = text.get(key)
        if values:
            qs = qs.filter(**{lookup: values})

    if filters.get("source") is not None:
        qs = qs.filter(source_id=filters["source"])
    if filters.get("store") is not None:
        qs = qs.filter(store_id=filters["store"])
    if filters.get("region"):
        qs = qs.filter(location__code=filters["region"])
    if filters.get("category"):
        # Manual categories are the authoritative ones.
        qs = qs.filter(manual_categories__category_id__in=filters["category"])
    if filters.get("date_from"):
        qs = qs.filter(scrape_batch__scrape_datetime__date__gte=filters["date_from"])
    if filters.get("date_to"):
        qs = qs.filter(scrape_batch__scrape_datetime__date__lte=filters["date_to"])
    if filters.get("storage_condition"):
        qs = qs.filter(storage_condition=filters["storage_condition"])
    if filters.get("primary_package_material"):
        qs = qs.filter(primary_package_material=filters["primary_package_material"])
    if filters.get("secondary_package_material"):
        qs = qs.filter(
            secondary_package_material=filters["secondary_package_material"],
        )

    ingredients = filters.get("ingredients") or {}
    terms = [t.strip() for t in ingredients.get("terms", []) if t and t.strip()]
    if terms:
        mode = ingredients.get("mode", "all")
        combined = None
        for term in terms:
            clause = Q(ingredient_en__icontains=term) | Q(
                ingredient_fr__icontains=term,
            )
            if combined is None:
                combined = clause
            elif mode == "any":
                combined |= clause
            else:
                combined &= clause
        qs = qs.filter(combined)

    allergens = (filters.get("allergens") or "").strip()
    if allergens:
        qs = qs.filter(
            Q(allergens_warnings__contains_en__icontains=allergens)
            | Q(allergens_warnings__may_contain_en__icontains=allergens),
        )

    nutrient = filters.get("nutrient") or {}
    if nutrient.get("id") is not None:
        # Both conditions must hold for the *same* nutrition_facts row, so they
        # go in a single filter() call.
        clause = Q(nutrition_facts__nutrient_id=nutrient["id"])
        if nutrient.get("min") is not None:
            clause &= Q(nutrition_facts__amount__gte=nutrient["min"])
        if nutrient.get("max") is not None:
            clause &= Q(nutrition_facts__amount__lte=nutrient["max"])
        qs = qs.filter(clause)

    return qs.distinct()


def apply_ordering(qs, sort=None):
    """Order ``qs`` by a whitelisted sort spec, ``id`` as a stable tiebreaker."""
    if not sort or not sort.get("field"):
        return qs.order_by("id")
    field = SEARCH_ORDERING_FIELDS[sort["field"]]
    prefix = "-" if sort.get("order") == "desc" else ""
    return qs.order_by(f"{prefix}{field}", "id")
