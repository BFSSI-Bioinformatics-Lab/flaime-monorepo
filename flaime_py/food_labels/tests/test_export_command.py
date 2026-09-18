"""Locks the `manage.py export --mode full` output so the refactor onto the
shared `flaime_py.food_labels.exports` module can't silently change it."""

import csv

import pytest
from django.core.management import call_command

from flaime_py.food_labels.exports import build_headers
from flaime_py.food_labels.exports import resolve_nutrients

from .factories import NutrientFactory
from .factories import SourceFactory
from .factories import StoreProductFactory
from .factories import StoreProductNutritionFactFactory


@pytest.mark.django_db()
def test_full_export_command_writes_expected_header_and_rows(tmp_path):
    nutrient = NutrientFactory(name="SODIUM")
    source = SourceFactory(name="Acme")
    product = StoreProductFactory(source=source, site_name="Test Product")
    StoreProductNutritionFactFactory(
        store_product=product,
        nutrient=nutrient,
        amount=42.0,
    )

    out = tmp_path / "export.csv"
    call_command("export", "--mode", "full", "--output", str(out))

    with out.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))

    assert rows[0] == build_headers("full", resolve_nutrients())
    assert rows[1][0] == str(product.id)
    assert rows[1][1] == "Acme"
    assert "42.0" in rows[1]
    assert len(rows) == 2


@pytest.mark.django_db()
def test_full_export_command_source_filter(tmp_path):
    keep = SourceFactory()
    StoreProductFactory(source=keep)
    StoreProductFactory(source=SourceFactory())

    out = tmp_path / "export.csv"
    call_command(
        "export", "--mode", "full", "--source", str(keep.id), "--output", str(out)
    )

    with out.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))

    assert len(rows) == 2  # header + single matching product
