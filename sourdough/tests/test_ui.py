import pandas as pd
import pytest

from sourdough import ui
from sourdough.calculations import calculate_recipe


def test_build_recipe_items_basic():
    main_items = (
        ("Strong White flour", 500.0),
        ("Flour 2", 100.0),
        ("Sourdough discard", 200.0),
        ("Pre-ferment", 150.0),
        ("Barley Malt Extract", 5.0),
        ("Water", 0.5),
    )

    items = ui.build_recipe_items(main_items, flour2_pct=15.0, flour3_pct=0.0)

    assert isinstance(items, dict)
    assert items["Strong white bread flour"] == pytest.approx(500.0)
    assert items[f"Alternative flour (15% of total)"] == pytest.approx(100.0)
    assert items["Sourdough discard (100% hydration)"] == pytest.approx(200.0)
    assert items["Pre-ferment (prepare night before)"] == pytest.approx(150.0)
    assert items["Barley malt extract (or honey)"] == pytest.approx(5.0)
    # Water was below the 1g threshold and should not be present
    assert all("Water" not in k for k in items.keys())


def test_build_recipe_items_filters_small_values():
    main_items = (("Salt", 1.0), ("Yeast", 1.1), ("Inclusion 2", 0.9))
    items = ui.build_recipe_items(main_items, flour2_pct=0.0, flour3_pct=0.0)
    # Salt (1.0) and Inclusion 2 (0.9) should be filtered out; Yeast should remain
    assert "Salt" not in items
    assert "Inclusion 2" not in items
    assert "Yeast" in items and items["Yeast"] == pytest.approx(1.1)


def test_ferment_df_from_items_nonempty_and_total():
    items = (("Flour", 100.0), ("Water", 100.0), ("Yeast", 1.0))
    df = ui.ferment_df_from_items(items)
    assert isinstance(df, pd.DataFrame)
    # Indices should include source items and a Total row
    assert "Flour" in df.index
    assert "Water" in df.index
    assert "Yeast" in df.index
    assert "Total" in df.index
    # Total should equal the sum of included weights
    expected_total = 100.0 + 100.0 + 1.0
    assert df.loc["Total", "Weight (g)"] == pytest.approx(expected_total)


def test_ferment_df_from_items_empty_or_all_small():
    # Empty input
    df_empty = ui.ferment_df_from_items(())
    assert isinstance(df_empty, pd.DataFrame)
    assert df_empty.empty

    # All small values should be filtered out
    df_small = ui.ferment_df_from_items((("A", 0.05), ("B", 0.01)))
    assert isinstance(df_small, pd.DataFrame)
    assert df_small.empty


def test_build_total_display_nonempty_and_total():
    items = (("Strong white flour", 70.0, 700.0), ("Water", 72.0, 720.0), ("Salt", 2.0, 20.0))
    df = ui.build_total_display(items)
    assert isinstance(df, pd.DataFrame)

    # Index contains ingredients and Total
    assert "Strong white flour" in df.index
    assert "Water" in df.index
    assert "Salt" in df.index
    assert "Total" in df.index

    # Totals should match
    assert df.loc["Total", "Baker's %"] == pytest.approx(70.0 + 72.0 + 2.0)
    assert df.loc["Total", "Weight (g)"] == pytest.approx(700.0 + 720.0 + 20.0)


def test_build_total_display_filters_small_weights_and_empty():
    # Small weight item should be removed
    items = (("X", 1.0, 0.05), ("Y", 5.0, 50.0))
    df = ui.build_total_display(items)
    assert "X" not in df.index
    assert "Y" in df.index

    # Empty input yields correct columns
    df_empty = ui.build_total_display(())
    assert list(df_empty.columns) == ["Baker's %", "Weight (g)"]


def test_get_recipe_cached_matches_calculate_recipe():
    expected = calculate_recipe(
        dough_weight=900.0,
        sourdough_discard_pct=30.0,
        preferment_pct=30.0,
        scale=1.0,
        flour2_pct=15.0,
        flour3_pct=0.0,
        water_pct=72.0,
        salt_pct=2.0,
        yeast_pct=0.5,
        barley_malt_pct=3.0,
        inclusion2_pct=0.0,
        inclusion3_pct=0.0,
        discard_flour_pct=100.0,
        discard_water_pct=100.0,
        preferment_flour_pct=100.0,
        preferment_water_pct=100.0,
        preferment_yeast_pct=1.0,
    )
    cached = ui.get_recipe_cached(
        dough_weight=900.0,
        sourdough_discard_pct=30.0,
        preferment_pct=30.0,
        scale=1.0,
        flour2_pct=15.0,
        flour3_pct=0.0,
        water_pct=72.0,
        salt_pct=2.0,
        yeast_pct=0.5,
        barley_malt_pct=3.0,
        inclusion2_pct=0.0,
        inclusion3_pct=0.0,
        discard_flour_pct=100.0,
        discard_water_pct=100.0,
        preferment_flour_pct=100.0,
        preferment_water_pct=100.0,
        preferment_yeast_pct=1.0,
    )

    # Compare dataframes by sums and ferments by keys/values
    assert expected[0]["Weight (g)"].sum() == pytest.approx(cached[0]["Weight (g)"].sum())
    assert expected[1]["Weight (g)"].sum() == pytest.approx(cached[1]["Weight (g)"].sum())
    assert expected[2].keys() == cached[2].keys()
    assert expected[3] == pytest.approx(cached[3])
    assert expected[4] == pytest.approx(cached[4])
    assert expected[5] == pytest.approx(cached[5])
