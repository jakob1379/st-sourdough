import pandas as pd


def calculate_recipe(
    dough_weight: float,
    sourdough_discard_pct: float,
    preferment_pct: float,
    scale: float,
    flour2_pct: float,
    flour3_pct: float,
    water_pct: float,
    salt_pct: float,
    yeast_pct: float,
    barley_malt_pct: float,
    inclusion2_pct: float,
    inclusion3_pct: float,
    discard_flour_pct: float,
    discard_water_pct: float,
    preferment_flour_pct: float,
    preferment_water_pct: float,
    preferment_yeast_pct: float,
) -> tuple:
    """Calculate recipe weights based on user inputs and baker's math."""

    strong_white_flour_pct = 100.0 - flour2_pct - flour3_pct
    bakers_pcts = {
        "Strong white flour": strong_white_flour_pct,
        "Flour 2": flour2_pct,
        "Flour 3": flour3_pct,
        "Water": water_pct,
        "Salt": salt_pct,
        "Yeast": yeast_pct,
        "Barley Malt Extract": barley_malt_pct,
        "Inclusion 2": inclusion2_pct,
        "Inclusion 3": inclusion3_pct,
    }
    total_bakers_pct = sum(bakers_pcts.values())

    if total_bakers_pct == 0:
        return pd.DataFrame(), pd.DataFrame(), {}, 0.0, 0.0, 0.0

    ingredient_weights = {
        name: (dough_weight / total_bakers_pct) * pct * scale
        for name, pct in bakers_pcts.items()
    }

    total_flour_weight = (
        ingredient_weights.get("Strong white flour", 0)
        + ingredient_weights.get("Flour 2", 0)
        + ingredient_weights.get("Flour 3", 0)
    )

    sourdough_discard_total_weight = total_flour_weight * (sourdough_discard_pct / 100.0)
    preferment_total_weight = total_flour_weight * (preferment_pct / 100.0)

    discard_bakers_sum = discard_flour_pct + discard_water_pct
    if discard_bakers_sum > 0:
        discard_flour_weight = (sourdough_discard_total_weight / discard_bakers_sum) * discard_flour_pct
        discard_water_weight = (sourdough_discard_total_weight / discard_bakers_sum) * discard_water_pct
    else:
        discard_flour_weight = 0
        discard_water_weight = 0

    preferment_bakers_sum = preferment_flour_pct + preferment_water_pct + preferment_yeast_pct
    if preferment_bakers_sum > 0:
        preferment_flour_weight = (preferment_total_weight / preferment_bakers_sum) * preferment_flour_pct
        preferment_water_weight = (preferment_total_weight / preferment_bakers_sum) * preferment_water_pct
        preferment_yeast_weight = (preferment_total_weight / preferment_bakers_sum) * preferment_yeast_pct
    else:
        preferment_flour_weight = 0
        preferment_water_weight = 0
        preferment_yeast_weight = 0

    pre_fermented_flour = discard_flour_weight + preferment_flour_weight

    main_dough = {
        "Strong White flour": ingredient_weights.get("Strong white flour", 0) - discard_flour_weight - preferment_flour_weight,
        "Flour 2": ingredient_weights.get("Flour 2", 0),
        "Flour 3": ingredient_weights.get("Flour 3", 0),
        "Water": ingredient_weights.get("Water", 0) - discard_water_weight - preferment_water_weight,
        "Salt": ingredient_weights.get("Salt", 0),
        "Sourdough discard": sourdough_discard_total_weight,
        "Pre-ferment": preferment_total_weight,
        "Yeast": ingredient_weights.get("Yeast", 0) - preferment_yeast_weight,
        "Barley Malt Extract": ingredient_weights.get("Barley Malt Extract", 0),
        "Inclusion 2": ingredient_weights.get("Inclusion 2", 0),
        "Inclusion 3": ingredient_weights.get("Inclusion 3", 0),
    }
    main_dough = {k: v for k, v in main_dough.items() if v > 1e-9}

    total_ingredients_df = pd.DataFrame.from_dict(bakers_pcts, orient="index", columns=["Baker's %"])
    total_ingredients_df["Weight (g)"] = total_ingredients_df.index.map(ingredient_weights)

    ferments_data = {
        "Sourdough discard": {
            "Flour": discard_flour_weight,
            "Water": discard_water_weight,
        },
        "Pre-ferment": {
            "Flour": preferment_flour_weight,
            "Water": preferment_water_weight,
            "Yeast": preferment_yeast_weight,
        },
    }

    main_dough_df = pd.DataFrame.from_dict(main_dough, orient="index", columns=["Weight (g)"])

    return total_ingredients_df, main_dough_df, ferments_data, pre_fermented_flour, sourdough_discard_total_weight, preferment_total_weight
