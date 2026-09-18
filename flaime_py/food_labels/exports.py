"""Shared CSV-export logic for FLAIMEshot store-product data.

Both the offline ``manage.py export`` command and the HTTP
``POST /api/storeproducts/export/`` endpoint build their rows here so the two
stay in lock-step.  The management command owns file writing / CLI options; the
endpoint streams :func:`iter_csv`.
"""

import csv

from django.db.models import Prefetch

from .models import Nutrient
from .models import StoreProductManualCategory
from .models import StoreProductNutritionFact
from .models import StoreProductUPC
from .models import SuppFoodLabelFlags

# Physiological ordering + DB name for every nutrient column in a "full" export.
NUTRIENT_ORDER = [
    ("Calories", "ENERGY (KILOCALORIES)"),
    ("Total Fat", "FAT (TOTAL LIPIDS)"),
    ("Saturated", "FATTY ACIDS, SATURATED, TOTAL"),
    ("Trans", "FATTY ACIDS, TRANS, TOTAL"),
    ("Saturated + Trans", "FATTY ACIDS, SATURATED + TRANS, TOTAL"),
    ("Omega-6 Polyunsaturated", "FATTY ACIDS, POLYUNSATURATED, TOTAL OMEGA N-6"),
    ("Omega-3 Polyunsaturated", "FATTY ACIDS, POLYUNSATURATED, TOTAL OMEGA N-3"),
    ("Monounsaturated", "FATTY ACIDS, MONOUNSATURATED, TOTAL"),
    ("Total Carbohydrate", "CARBOHYDRATE, TOTAL (BY DIFFERENCE)"),
    ("Dietary Fibre", "FIBRE, TOTAL DIETARY"),
    ("Soluble Fibre", "FIBRE, SOLUBLE DIETARY FIBRE"),
    ("Insoluble Fibre", "FIBRE, INSOLUBLE DIETARY FIBRE"),
    ("Sugars", "SUGARS, TOTAL"),
    ("Sugar Alcohols", "SUGAR_ALCOHOLS"),
    ("Starch", "STARCH"),
    ("Protein", "PROTEIN"),
    ("Cholesterol", "CHOLESTEROL"),
    ("Sodium", "SODIUM"),
    ("Potassium", "POTASSIUM"),
    ("Calcium", "CALCIUM"),
    ("Iron", "IRON"),
    ("Vitamin A", "VITAMIN A (MICROGRAMS)"),
    ("Vitamin C", "VITAMIN C"),
    ("Vitamin D", "VITAMIN D (MICROGRAMS)"),
    ("Vitamin E", "VITAMIN E, TOTAL TOCOPHEROLS"),
    ("Vitamin K", "VITAMIN K"),
    ("Thiamine", "THIAMINE"),
    ("Riboflavin", "RIBOFLAVIN"),
    ("Niacin", "NIACIN (NICOTINIC ACID) PREFORMED"),
    ("Vitamin B₆", "VITAMIN B-6"),
    ("Folate", "TOTAL FOLACIN"),
    ("Vitamin B₁₂", "VITAMIN B-12"),
    ("Biotin", "BIOTIN"),
    ("Pantothenate", "PANTOTHENIC ACID"),
    ("Choline", "CHOLINE, TOTAL"),
    ("Phosphorous", "PHOSPHORUS"),
    ("Iodide", "IODIDE"),
    ("Magnesium", "MAGNESIUM"),
    ("Zinc", "ZINC"),
    ("Selenium", "SELENIUM"),
    ("Copper", "COPPER"),
    ("Manganese", "MANGANESE"),
    ("Chromium", "CHROMIUM"),
    ("Molybdenum", "MOLYBDENUM"),
    ("Chloride", "CHLORIDE"),
]

# (model attribute, CSV header) for the 12 supplemented-food label flags.
SUPP_FLAG_FIELDS = [
    ("has_supplemental_caution_id", "SUPP_has_supplemental_caution_id"),
    ("has_nutrient_content_claim", "SUPP_has_nutrient_content_claim"),
    ("has_nutrient_function_claim", "SUPP_has_nutrient_function_claim"),
    ("has_disease_risk_reduction_claim", "SUPP_has_disease_risk_reduction_claim"),
    ("has_probiotic_claim", "SUPP_has_probiotic_claim"),
    ("has_therapeutic_claim", "SUPP_has_therapeutic_claim"),
    ("has_function_claim", "SUPP_has_function_claim"),
    ("has_general_health_claim", "SUPP_has_general_health_claim"),
    (
        "has_quantitative_nutrient_declaration",
        "SUPP_has_quantitative_nutrient_declaration",
    ),
    ("has_implied_nonspecific_claim", "SUPP_has_implied_nonspecific_claim"),
    ("has_logos_icons", "SUPP_has_logos_icons"),
    ("has_third_party_label", "SUPP_has_third_party_label"),
]

EXPORT_COLUMN_CHOICES = ["simple", "full", "full_supplemented"]

SIMPLE_HEADERS = [
    "Assigned Flaime ID",
    "External ID",
    "Store Name",
    "Data Source",
    "Product Name",
    "Category Name",
]

_FULL_BASE_HEADERS = [
    "flaime_id",
    "source",
    "storage_condition",
    "variety_pack_flag",
    "multiple_nfts",
    "multiple_lois",
    "fop_symbol",
    "preparation_instructions",
    "individually_packaged_flag",
    "product_name",
    "company",
    "brand",
    "upc",
    "reference_amount_category",
    "net_quantity",
    "serving_size_household_measure",
    "serving_size_metric_value",
    "serving_size_metric_unit",
]

_FULL_TRAILER_HEADERS = ["ingredients_en", "nft_verified", "product_verified"]


def _display_name(nutrient):
    return next(
        (dn for dn, db in NUTRIENT_ORDER if db == nutrient.name),
        nutrient.name,
    )


def resolve_nutrients():
    """Nutrients that back the "full" nutrient columns, in NUTRIENT_ORDER order."""
    by_name = {n.name: n for n in Nutrient.objects.all()}
    return [by_name[db] for _dn, db in NUTRIENT_ORDER if db in by_name]


def resolve_supp_nutrients(nutrients):
    """Nutrients that appear on any supplemented NFT row (ordered like the
    management command: NUTRIENT_ORDER ones first, then the rest by id)."""
    all_supp = list(
        Nutrient.objects.filter(storeproductnutritionfact__supplemented=True)
        .distinct()
        .order_by("id"),
    )
    ordered = [n for n in nutrients if n in all_supp]
    additional = [n for n in all_supp if n not in nutrients]
    return ordered + additional


def build_headers(
    columns,
    nutrients,
    supp_nutrients=(),
    *,
    include_description=False,
):
    if columns == "simple":
        return list(SIMPLE_HEADERS)

    headers = list(_FULL_BASE_HEADERS)
    if include_description:
        headers.insert(headers.index("product_name") + 1, "site_description")

    for nutrient in nutrients:
        dn = _display_name(nutrient)
        headers += [f"{dn}_amount", f"{dn}_amount_unit", f"{dn}_daily_value"]

    if columns == "full_supplemented":
        for nutrient in supp_nutrients:
            dn = _display_name(nutrient)
            headers += [
                f"SUPP_{dn}_amount",
                f"SUPP_{dn}_amount_unit",
                f"SUPP_{dn}_daily_value",
            ]
        headers += [header for _attr, header in SUPP_FLAG_FIELDS]

    headers += _FULL_TRAILER_HEADERS
    return headers


def _full_queryset(queryset, *, supplemented):
    qs = queryset.select_related(
        "serving_size_unit",
        "source",
        "company",
        "brand",
    ).prefetch_related(
        Prefetch(
            "storeproductupc_set",
            queryset=StoreProductUPC.objects.select_related("upc"),
        ),
        Prefetch(
            "manual_categories",
            queryset=StoreProductManualCategory.objects.filter(
                category__scheme__name="reference amount",
                category__level=2,
            ).select_related("category"),
        ),
    )
    if supplemented:
        qs = qs.select_related("label_flags")
    return qs.order_by("id")


def _label_flags(store_product):
    try:
        return store_product.label_flags
    except SuppFoodLabelFlags.DoesNotExist:
        return None


def _full_row(
    sp,
    nutrients,
    supp_nutrients,
    facts,
    supp_facts,
    *,
    supplemented,
    all_barcodes,
    include_description,
):
    upc_codes = [link.upc.code for link in sp.storeproductupc_set.all()]
    if all_barcodes:
        upc = "|".join(upc_codes)
    else:
        upc = upc_codes[0] if upc_codes else ""

    ref_cats = list(sp.manual_categories.all())
    ref_amount_cat = ref_cats[0].category.code if ref_cats else ""

    row = [
        sp.id,
        sp.source.name if sp.source else "",
        sp.get_storage_condition_display(),
        sp.variety_pack_flag,
        sp.multiple_nfts_flag,
        "",  # multiple_lois - not tracked
        sp.fop_flag,
        sp.has_preparation_instructions_flag,
        sp.individually_packaged_flag,
        sp.site_name,
    ]
    if include_description:
        row.append(sp.site_description)
    row += [
        sp.company.name if sp.company else "",
        sp.brand.name if sp.brand else sp.raw_brand or "",
        upc,
        ref_amount_cat,
        sp.total_size or "",
        sp.raw_serving_size or "",
        sp.serving_size or "",
        sp.serving_size_unit.name if sp.serving_size_unit else "",
    ]

    for nutrient in nutrients:
        fact = facts.get(nutrient.id)
        row += [
            fact.amount if fact else "",
            fact.amount_unit.name if fact and fact.amount_unit else "",
            fact.daily_value if fact else "",
        ]

    if supplemented:
        for nutrient in supp_nutrients:
            fact = supp_facts.get(nutrient.id)
            row += [
                fact.amount if fact else "",
                fact.amount_unit.name if fact and fact.amount_unit else "",
                fact.daily_value if fact else "",
            ]
        flags = _label_flags(sp)
        if flags is not None:
            row += [
                "Yes" if getattr(flags, attr) else "No"
                for attr, _header in SUPP_FLAG_FIELDS
            ]
        else:
            row += [""] * len(SUPP_FLAG_FIELDS)

    row += [
        sp.ingredient_en or "",
        "Yes" if sp.verified_nft_ingredients != "unknown" else "No",
        "Yes" if sp.verified else "No",
    ]
    return row


def iter_full_rows(
    queryset,
    *,
    supplemented=False,
    all_barcodes=False,
    include_description=False,
    batch_size=1000,
    progress=None,
):
    """Yield the header row then one list per product for a full export.

    ``progress`` - optional ``callable(start, end, total)`` invoked once per
    batch (the management command uses it for stdout progress).
    """
    nutrients = resolve_nutrients()
    supp_nutrients = resolve_supp_nutrients(nutrients) if supplemented else []

    qs = _full_queryset(queryset, supplemented=supplemented)

    yield build_headers(
        "full_supplemented" if supplemented else "full",
        nutrients,
        supp_nutrients,
        include_description=include_description,
    )

    total = qs.count()
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        if progress is not None:
            progress(start, end, total)

        batch = list(qs[start:end])
        ids = [sp.id for sp in batch]

        facts_by_product = {}
        for fact in StoreProductNutritionFact.objects.filter(
            store_product_id__in=ids,
        ).select_related("nutrient", "amount_unit"):
            facts_by_product.setdefault(fact.store_product_id, {})[fact.nutrient_id] = (
                fact
            )

        supp_by_product = {}
        if supplemented:
            for fact in StoreProductNutritionFact.objects.filter(
                store_product_id__in=ids,
                supplemented=True,
            ).select_related("nutrient", "amount_unit"):
                supp_by_product.setdefault(fact.store_product_id, {})[
                    fact.nutrient_id
                ] = fact

        for sp in batch:
            yield _full_row(
                sp,
                nutrients,
                supp_nutrients,
                facts_by_product.get(sp.id, {}),
                supp_by_product.get(sp.id, {}),
                supplemented=supplemented,
                all_barcodes=all_barcodes,
                include_description=include_description,
            )


def iter_simple_rows(queryset):
    qs = (
        queryset.select_related("store", "source")
        .prefetch_related(
            Prefetch(
                "manual_categories",
                queryset=StoreProductManualCategory.objects.select_related(
                    "category",
                ).order_by("category__level"),
            ),
        )
        .order_by("id")
    )
    yield list(SIMPLE_HEADERS)
    for sp in qs.iterator(chunk_size=2000):
        categories = " > ".join(
            link.category.name for link in sp.manual_categories.all()
        )
        yield [
            sp.id,
            sp.external_id or "",
            sp.store.name if sp.store_id else "",
            sp.source.name if sp.source_id else "",
            sp.site_name or "",
            categories,
        ]


def iter_rows(queryset, columns, *, batch_size=1000):
    """Header row + data rows for the given ``columns`` layout."""
    if columns == "simple":
        yield from iter_simple_rows(queryset)
    else:
        yield from iter_full_rows(
            queryset,
            supplemented=(columns == "full_supplemented"),
            batch_size=batch_size,
        )


class _Echo:
    """A file-like object whose ``write`` just returns the value, for
    ``csv.writer`` + ``StreamingHttpResponse``."""

    def write(self, value):
        return value


def iter_csv(queryset, columns, *, batch_size=1000):
    """Yield CSV-encoded lines (strings) for a streaming HTTP response."""
    writer = csv.writer(_Echo())
    for row in iter_rows(queryset, columns, batch_size=batch_size):
        yield writer.writerow(row)
