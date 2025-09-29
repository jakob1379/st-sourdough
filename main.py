import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Waste Not Want Not - Sourdough Recipe Calculator")
st.markdown(
    "This app replicates the functionality of the provided [Google Sheet](https://docs.google.com/spreadsheets/d/1m1cki9dIE_zkLR6F6RSErP0Kwx4MRXgiJJBIxCvln1k/edit?usp=sharing) "
    "to calculate sourdough recipe ingredients based on baker's percentages."
)


def calculate_recipe(
    dough_weight: float,
    sourdough_discard_pct: float,
    preferment_pct: float,
    scale: float,
    # Total ingredients baker's percentages
    flour2_pct: float,
    flour3_pct: float,
    water_pct: float,
    salt_pct: float,
    yeast_pct: float,
    barley_malt_pct: float,
    inclusion2_pct: float,
    inclusion3_pct: float,
    # Ferment composition baker's percentages
    discard_flour_pct: float,
    discard_water_pct: float,
    preferment_flour_pct: float,
    preferment_water_pct: float,
    preferment_yeast_pct: float,
) -> tuple:
    """
    Calculates the recipe weights based on user inputs and baker's math.
    """
    # --- 1. Calculate Total Ingredients ---

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
        return pd.DataFrame(), pd.DataFrame(), {}, 0.0

    ingredient_weights = {
        name: (dough_weight / total_bakers_pct) * pct * scale
        for name, pct in bakers_pcts.items()
    }

    total_flour_weight = (
        ingredient_weights.get("Strong white flour", 0)
        + ingredient_weights.get("Flour 2", 0)
        + ingredient_weights.get("Flour 3", 0)
    )

    # --- 2. Calculate Ferment Weights ---

    sourdough_discard_total_weight = total_flour_weight * (
        sourdough_discard_pct / 100.0
    )
    preferment_total_weight = total_flour_weight * (preferment_pct / 100.0)

    discard_bakers_sum = discard_flour_pct + discard_water_pct
    discard_flour_weight = (
        (sourdough_discard_total_weight / discard_bakers_sum)
        * discard_flour_pct
        if discard_bakers_sum > 0
        else 0
    )
    discard_water_weight = (
        (sourdough_discard_total_weight / discard_bakers_sum)
        * discard_water_pct
        if discard_bakers_sum > 0
        else 0
    )

    preferment_bakers_sum = (
        preferment_flour_pct + preferment_water_pct + preferment_yeast_pct
    )
    preferment_flour_weight = (
        (preferment_total_weight / preferment_bakers_sum)
        * preferment_flour_pct
        if preferment_bakers_sum > 0
        else 0
    )
    preferment_water_weight = (
        (preferment_total_weight / preferment_bakers_sum)
        * preferment_water_pct
        if preferment_bakers_sum > 0
        else 0
    )
    preferment_yeast_weight = (
        (preferment_total_weight / preferment_bakers_sum)
        * preferment_yeast_pct
        if preferment_bakers_sum > 0
        else 0
    )

    pre_fermented_flour = discard_flour_weight + preferment_flour_weight

    # --- 3. Calculate Main Dough Ingredients ---

    main_dough = {
        "Strong White flour": ingredient_weights["Strong white flour"]
        - discard_flour_weight
        - preferment_flour_weight,
        "Flour 2": ingredient_weights["Flour 2"],
        "Flour 3": ingredient_weights["Flour 3"],
        "Water": ingredient_weights["Water"]
        - discard_water_weight
        - preferment_water_weight,
        "Salt": ingredient_weights["Salt"],
        "Sourdough discard": sourdough_discard_total_weight,
        "Pre-ferment": preferment_total_weight,
        "Yeast": ingredient_weights["Yeast"] - preferment_yeast_weight,
        "Barley Malt Extract": ingredient_weights["Barley Malt Extract"],
        "Inclusion 2": ingredient_weights["Inclusion 2"],
        "Inclusion 3": ingredient_weights["Inclusion 3"],
    }
    main_dough = {k: v for k, v in main_dough.items() if v > 1e-9}

    # --- 4. Format for Display ---

    total_ingredients_df = pd.DataFrame.from_dict(
        bakers_pcts, orient="index", columns=["Baker's %"]
    )
    total_ingredients_df["Weight (g)"] = total_ingredients_df.index.map(
        ingredient_weights
    )

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

    main_dough_df = pd.DataFrame.from_dict(
        main_dough, orient="index", columns=["Weight (g)"]
    )

    return total_ingredients_df, main_dough_df, ferments_data, pre_fermented_flour


# --- Streamlit UI ---

# Sidebar for inputs
with st.sidebar:
    st.header("Recipe Inputs")
    dough_weight = st.number_input("Dough weight (g)", value=900, min_value=0)
    sourdough_discard_pct = st.number_input(
        "Sourdough discard (%)", value=30.0, min_value=0.0, format="%.2f"
    )
    preferment_pct = st.number_input(
        "Pre-ferment (%)", value=30.0, min_value=0.0, format="%.2f"
    )
    scale = st.number_input("Scale", value=1.0, min_value=0.1, format="%.2f")

    st.header("Total Ingredients (Baker's %)")
    st.info("Percentages are relative to total flour (100%).")
    flour2_pct = st.number_input("Flour 2 (%)", value=15.0, format="%.2f")
    flour3_pct = st.number_input("Flour 3 (%)", value=0.0, format="%.2f")
    water_pct = st.number_input("Water (%)", value=72.0, format="%.2f")
    salt_pct = st.number_input("Salt (%)", value=2.0, format="%.2f")
    yeast_pct = st.number_input("Yeast (%)", value=0.5, format="%.2f")
    barley_malt_pct = st.number_input(
        "Barley Malt Extract (%)", value=3.0, format="%.2f"
    )
    inclusion2_pct = st.number_input("Inclusion 2 (%)", value=0.0, format="%.2f")
    inclusion3_pct = st.number_input("Inclusion 3 (%)", value=0.0, format="%.2f")

    st.header("Ferment Composition (Baker's %)")
    st.info("Percentages are relative to the ferment's own flour.")
    discard_flour_pct = st.number_input(
        "Sourdough Discard Flour (%)", value=100.0, format="%.2f"
    )
    discard_water_pct = st.number_input(
        "Sourdough Discard Water (%)", value=100.0, format="%.2f"
    )
    preferment_flour_pct = st.number_input(
        "Pre-ferment Flour (%)", value=100.0, format="%.2f"
    )
    preferment_water_pct = st.number_input(
        "Pre-ferment Water (%)", value=100.0, format="%.2f"
    )
    preferment_yeast_pct = st.number_input(
        "Pre-ferment Yeast (%)", value=1.0, format="%.2f"
    )

# Perform calculations
(
    total_ingredients_df,
    main_dough_df,
    ferments_data,
    pre_fermented_flour,
) = calculate_recipe(
    dough_weight,
    sourdough_discard_pct,
    preferment_pct,
    scale,
    flour2_pct,
    flour3_pct,
    water_pct,
    salt_pct,
    yeast_pct,
    barley_malt_pct,
    inclusion2_pct,
    inclusion3_pct,
    discard_flour_pct,
    discard_water_pct,
    preferment_flour_pct,
    preferment_water_pct,
    preferment_yeast_pct,
)

# Display results
if not total_ingredients_df.empty:
    st.metric("Pre-fermented Flour", f"{pre_fermented_flour:.2f} g")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Total Ingredients")
        total_ingredients_df.loc["Total"] = [
            total_ingredients_df["Baker's %"].sum(),
            total_ingredients_df["Weight (g)"].sum(),
        ]
        st.dataframe(
            total_ingredients_df.style.format(
                {"Baker's %": "{:.2f}%", "Weight (g)": "{:.2f}"}
            )
        )

    with col2:
        st.subheader("Ferments Breakdown")
        for ferment_name, ingredients in ferments_data.items():
            st.markdown(f"**{ferment_name}**")
            df = pd.DataFrame.from_dict(
                ingredients, orient="index", columns=["Weight (g)"]
            )
            df.loc["Total"] = df["Weight (g)"].sum()
            st.dataframe(df.style.format("{:.2f}"))

    with col3:
        st.subheader("Final Dough Recipe")
        main_dough_df.loc["Total"] = main_dough_df["Weight (g)"].sum()
        st.dataframe(main_dough_df.style.format("{:.2f}"))

else:
    st.warning("Please set valid Baker's percentages in the sidebar.")
