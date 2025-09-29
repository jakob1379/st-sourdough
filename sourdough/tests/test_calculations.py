import pandas as pd
import pytest

from sourdough.calculations import calculate_recipe


def test_calculate_recipe_basic():
    """Basic smoke test for calculate_recipe with typical inputs.

    Verifies return types and arithmetic invariants (total weights sum to target dough weight).
    """
    dough_weight = 900.0
    (
        total_ingredients_df,
        main_dough_df,
        ferments_data,
        pre_fermented_flour,
        sourdough_discard_total_weight,
        preferment_total_weight,
    ) = calculate_recipe(
        dough_weight,
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

    # Basic types and columns
    assert isinstance(total_ingredients_df, pd.DataFrame)
    assert isinstance(main_dough_df, pd.DataFrame)
    assert "Weight (g)" in total_ingredients_df.columns

    # Sum of weights in the formula equals the requested dough weight * scale
    assert total_ingredients_df["Weight (g)"].sum() == pytest.approx(dough_weight * 1.0)
    assert main_dough_df["Weight (g)"].sum() == pytest.approx(dough_weight * 1.0)

    # Ferments data should contain expected keys and the pre_fermented_flour should
    # match the sum of ferment flour components returned in ferments_data
    assert "Sourdough discard" in ferments_data
    assert "Pre-ferment" in ferments_data
    discard_flour = ferments_data["Sourdough discard"]["Flour"]
    preferment_flour = ferments_data["Pre-ferment"]["Flour"]
    assert pre_fermented_flour == pytest.approx(discard_flour + preferment_flour)

    # Totals for the two ferment components should match the per-ferment sums
    assert sourdough_discard_total_weight == pytest.approx(
        ferments_data["Sourdough discard"]["Flour"] + ferments_data["Sourdough discard"]["Water"]
    )
    assert preferment_total_weight == pytest.approx(
        ferments_data["Pre-ferment"]["Flour"]
        + ferments_data["Pre-ferment"]["Water"]
        + ferments_data["Pre-ferment"]["Yeast"]
    )


def test_calculate_recipe_zero_total_bakers_pct_guard():
    """If the computed baker's sum is zero the function should return empty/zero outputs.

    We pass a negative water_pct to force the internal baker's percentage sum to zero
    (this is an abnormal input but exercises the guard in the implementation).
    """
    total_ingredients_df, main_dough_df, ferments_data, pre_fermented_flour, discard_total, preferment_total = (
        calculate_recipe(
            900.0,
            sourdough_discard_pct=0.0,
            preferment_pct=0.0,
            scale=1.0,
            flour2_pct=0.0,
            flour3_pct=0.0,
            water_pct=-100.0,  # force the internal baker's total to 0
            salt_pct=0.0,
            yeast_pct=0.0,
            barley_malt_pct=0.0,
            inclusion2_pct=0.0,
            inclusion3_pct=0.0,
            discard_flour_pct=100.0,
            discard_water_pct=100.0,
            preferment_flour_pct=100.0,
            preferment_water_pct=100.0,
            preferment_yeast_pct=1.0,
        )
    )

    assert total_ingredients_df.empty
    assert main_dough_df.empty
    assert ferments_data == {}
    assert pre_fermented_flour == 0.0
    assert discard_total == 0.0
    assert preferment_total == 0.0
