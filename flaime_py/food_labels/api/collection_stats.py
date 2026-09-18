"""Collection-statistics computation shared by
``GET /api/sources/{id}/collection-stats/`` and
``GET /api/storeproducts/collection-stats/``.

Replaces the Elasticsearch ``size:0`` aggregation queries the Collection Stats
report used to run from the browser (nested nutrition_details stats +
percentiles, and the additive ``match_phrase`` filters aggregation).

The nutrient set and additive list mirror ``NUTRIENT_CONFIG`` / ``ADDITIVES`` in
the frontend's ``src/pages/reports/Collection_stats/index.jsx``.
"""

from django.db.models import Aggregate
from django.db.models import Avg
from django.db.models import Count
from django.db.models import FloatField
from django.db.models import Max
from django.db.models import Min

from ..models import StoreProduct
from ..models import StoreProductNutritionFact


class PercentileCont(Aggregate):
    """Postgres ``PERCENTILE_CONT(p) WITHIN GROUP (ORDER BY expr)`` - exact
    continuous percentile.  Used for the median."""

    function = "PERCENTILE_CONT"
    name = "PercentileCont"
    output_field = FloatField()
    template = "%(function)s(%(percentile)s) WITHIN GROUP (ORDER BY %(expressions)s)"

    def __init__(self, expression, percentile=0.5, **extra):
        super().__init__(expression, percentile=percentile, **extra)


# nutrient_ids are StoreProduct nutrition-fact Nutrient PKs (Nutrient.id).
COLLECTION_STATS_NUTRIENTS = [
    {"label": "Sodium", "nutrient_ids": [307], "unit": "mg"},
    {"label": "Total Sugars", "nutrient_ids": [269, 917], "unit": "g"},
    {"label": "Saturated Fat", "nutrient_ids": [606], "unit": "g"},
]

# (label, ingredient substring) - label == term for now; E-number labels can be
# added here if the frontend config carries them.
COLLECTION_STATS_ADDITIVES = [
    ("Potassium Sorbate", "Potassium Sorbate"),
    ("Potassium Metabisulphite", "Potassium Metabisulphite"),
    ("Sodium Nitrite", "Sodium Nitrite"),
    ("Ascorbic Acid", "Ascorbic Acid"),
    ("Sodium Ascorbate", "Sodium Ascorbate"),
    ("Sodium Erythorbate", "Sodium Erythorbate"),
    ("Citric Acid", "Citric Acid"),
    ("Rosemary Extract", "Rosemary Extract"),
]


def _pct(part, whole):
    return round(part / whole * 100, 2) if whole else 0


def _nutrient_stats(product_qs, spec):
    facts = StoreProductNutritionFact.objects.filter(
        store_product__in=product_qs,
        nutrient_id__in=spec["nutrient_ids"],
        amount__isnull=False,
    )
    agg = facts.aggregate(
        count=Count("amount"),
        mean=Avg("amount"),
        median=PercentileCont("amount"),
        min=Min("amount"),
        max=Max("amount"),
    )
    return {
        "label": spec["label"],
        "nutrient_ids": spec["nutrient_ids"],
        "unit": spec["unit"],
        "count": agg["count"] or 0,
        "mean": agg["mean"],
        "median": agg["median"],
        "min": agg["min"],
        "max": agg["max"],
    }


def compute_collection_stats(product_qs=None):
    """Return the collection-stats payload for a ``StoreProduct`` queryset
    (already scoped to a source, or all non-deleted products)."""
    if product_qs is None:
        product_qs = StoreProduct.objects.filter(deleted=False)

    total = product_qs.count()
    with_fop = product_qs.filter(fop_flag=True).count()
    manually_reviewed = product_qs.filter(verified=True).count()

    nutrients = [
        _nutrient_stats(product_qs, spec) for spec in COLLECTION_STATS_NUTRIENTS
    ]

    additives = []
    for label, term in COLLECTION_STATS_ADDITIVES:
        count = product_qs.filter(ingredient_en__icontains=term).count()
        additives.append(
            {
                "label": label,
                "term": term,
                "count": count,
                "percentage": _pct(count, total),
            },
        )

    return {
        "total": total,
        "with_fop": with_fop,
        "fop_percentage": _pct(with_fop, total),
        "manually_reviewed": manually_reviewed,
        "reviewed_percentage": _pct(manually_reviewed, total),
        "nutrients": nutrients,
        "additives": additives,
    }
