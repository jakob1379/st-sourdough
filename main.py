import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Sourdough Recipe Calculator")

# Initialize session state for advanced mode
if 'show_advanced' not in st.session_state:
    st.session_state.show_advanced = False

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
    discard_flour_weight = (
        (sourdough_discard_total_weight / discard_bakers_sum) * discard_flour_pct
        if discard_bakers_sum > 0 else 0
    )
    discard_water_weight = (
        (sourdough_discard_total_weight / discard_bakers_sum) * discard_water_pct
        if discard_bakers_sum > 0 else 0
    )

    preferment_bakers_sum = preferment_flour_pct + preferment_water_pct + preferment_yeast_pct
    preferment_flour_weight = (
        (preferment_total_weight / preferment_bakers_sum) * preferment_flour_pct
        if preferment_bakers_sum > 0 else 0
    )
    preferment_water_weight = (
        (preferment_total_weight / preferment_bakers_sum) * preferment_water_pct
        if preferment_bakers_sum > 0 else 0
    )
    preferment_yeast_weight = (
        (preferment_total_weight / preferment_bakers_sum) * preferment_yeast_pct
        if preferment_bakers_sum > 0 else 0
    )

    pre_fermented_flour = discard_flour_weight + preferment_flour_weight

    main_dough = {
        "Strong White flour": ingredient_weights["Strong white flour"] - discard_flour_weight - preferment_flour_weight,
        "Flour 2": ingredient_weights["Flour 2"],
        "Flour 3": ingredient_weights["Flour 3"],
        "Water": ingredient_weights["Water"] - discard_water_weight - preferment_water_weight,
        "Salt": ingredient_weights["Salt"],
        "Sourdough discard": sourdough_discard_total_weight,
        "Pre-ferment": preferment_total_weight,
        "Yeast": ingredient_weights["Yeast"] - preferment_yeast_weight,
        "Barley Malt Extract": ingredient_weights["Barley Malt Extract"],
        "Inclusion 2": ingredient_weights["Inclusion 2"],
        "Inclusion 3": ingredient_weights["Inclusion 3"],
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

# Header with better branding
st.title("🍞 Sourdough Recipe Calculator")
st.markdown("**Waste Not Want Not** - Turn your sourdough discard into delicious bread")

# Toggle for advanced mode
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("⚙️ Advanced Settings" if not st.session_state.show_advanced else "📝 Simple Mode"):
        st.session_state.show_advanced = not st.session_state.show_advanced

# Main interface with tabs
tab1, tab2, tab3 = st.tabs(["🥖 Your Recipe", "📊 Recipe Details", "🔬 Technical View"])

# Essential inputs in sidebar - always visible
with st.sidebar:
    st.header("🎯 Recipe Basics")

    dough_weight = st.number_input(
        "🍞 Target dough weight (g)",
        value=900,
        min_value=100,
        help="Total weight of your finished dough"
    )

    col_a, col_b = st.columns(2)
    with col_a:
        water_pct = st.number_input("💧 Hydration (%)", value=72.0, min_value=50.0, max_value=100.0)
    with col_b:
        salt_pct = st.number_input("🧂 Salt (%)", value=2.0, min_value=1.0, max_value=5.0)

    sourdough_discard_pct = st.slider(
        "♻️ Sourdough discard",
        min_value=0.0,
        max_value=50.0,
        value=30.0,
        step=5.0,
        format="%.0f%%",
        help="Percentage of total flour weight from sourdough discard"
    )

    preferment_pct = st.slider(
        "⏰ Pre-ferment",
        min_value=0.0,
        max_value=50.0,
        value=30.0,
        step=5.0,
        format="%.0f%%",
        help="Percentage of total flour weight as pre-ferment"
    )

    # Advanced settings - collapsible
    if st.session_state.show_advanced:
        st.header("⚙️ Advanced Options")

        with st.expander("📐 Scaling & Additional Ingredients"):
            scale = st.number_input("Recipe scale multiplier", value=1.0, min_value=0.1, format="%.2f")
            yeast_pct = st.number_input("🦠 Commercial yeast (%)", value=0.5, min_value=0.0, format="%.2f")
            barley_malt_pct = st.number_input("🌾 Barley malt extract (%)", value=3.0, min_value=0.0, format="%.2f")

        with st.expander("🌾 Alternative Flours"):
            flour2_pct = st.number_input("Flour type 2 (%)", value=15.0, min_value=0.0, format="%.2f")
            flour3_pct = st.number_input("Flour type 3 (%)", value=0.0, min_value=0.0, format="%.2f")

        with st.expander("➕ Mix-ins"):
            inclusion2_pct = st.number_input("Inclusion 2 (%)", value=0.0, min_value=0.0, format="%.2f")
            inclusion3_pct = st.number_input("Inclusion 3 (%)", value=0.0, min_value=0.0, format="%.2f")

        with st.expander("🧪 Ferment Composition"):
            st.info("Baker's percentages for individual ferments")
            discard_flour_pct = st.number_input("Discard flour ratio", value=100.0, format="%.1f")
            discard_water_pct = st.number_input("Discard water ratio", value=100.0, format="%.1f")
            preferment_flour_pct = st.number_input("Pre-ferment flour ratio", value=100.0, format="%.1f")
            preferment_water_pct = st.number_input("Pre-ferment water ratio", value=100.0, format="%.1f")
            preferment_yeast_pct = st.number_input("Pre-ferment yeast ratio", value=1.0, format="%.2f")
    else:
        # Default values when advanced mode is off
        scale = 1.0
        flour2_pct = 15.0
        flour3_pct = 0.0
        yeast_pct = 0.5
        barley_malt_pct = 3.0
        inclusion2_pct = 0.0
        inclusion3_pct = 0.0
        discard_flour_pct = 100.0
        discard_water_pct = 100.0
        preferment_flour_pct = 100.0
        preferment_water_pct = 100.0
        preferment_yeast_pct = 1.0

# Calculate recipe
(total_ingredients_df, main_dough_df, ferments_data, pre_fermented_flour,
 sourdough_discard_total_weight, preferment_total_weight) = calculate_recipe(
    dough_weight, sourdough_discard_pct, preferment_pct, scale,
    flour2_pct, flour3_pct, water_pct, salt_pct, yeast_pct, barley_malt_pct,
    inclusion2_pct, inclusion3_pct, discard_flour_pct, discard_water_pct,
    preferment_flour_pct, preferment_water_pct, preferment_yeast_pct
)

# Tab 1: Simple Recipe View
with tab1:
    if not main_dough_df.empty:
        st.success(f"Recipe ready! Total dough weight: **{main_dough_df['Weight (g)'].sum():.0f}g**")

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💧 Hydration", f"{water_pct}%")
        with col2:
            st.metric("🧂 Salt", f"{salt_pct}%")
        with col3:
            st.metric("♻️ Discard Used", f"{sourdough_discard_pct:.0f}%")
        with col4:
            st.metric("⏰ Pre-ferment", f"{preferment_pct:.0f}%")

        st.markdown("---")

        # Simple shopping list view
        st.subheader("🛒 Your Recipe")

        # Filter and rename for user-friendly display
        recipe_items = {}
        for ingredient, weight in main_dough_df['Weight (g)'].items():
            if weight > 1:  # Only show meaningful amounts
                if ingredient == "Strong White flour":
                    recipe_items["Strong white bread flour"] = weight
                elif ingredient == "Flour 2" and weight > 0:
                    recipe_items["Alternative flour"] = weight
                elif ingredient == "Sourdough discard":
                    recipe_items["Sourdough discard"] = weight
                elif ingredient == "Pre-ferment":
                    recipe_items["Pre-ferment (prepared)"] = weight
                else:
                    recipe_items[ingredient] = weight

        # Display in a clean, printable format
        for ingredient, weight in recipe_items.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{ingredient}**")
            with col2:
                st.write(f"**{weight:.0f}g**")

        # Quick preparation notes
        st.markdown("---")
        st.subheader("📝 Quick Notes")
        st.info(f"""
        **Before you start:**
        - Prepare your pre-ferment ({preferment_total_weight:.0f}g total) 8-12 hours ahead
        - Have your sourdough discard ready ({sourdough_discard_total_weight:.0f}g needed)
        - Room temperature water works best for mixing
        """)

    else:
        st.error("Unable to calculate recipe. Please check your inputs.")

# Tab 2: Recipe Details
with tab2:
    if not main_dough_df.empty:
        st.subheader("📊 Detailed Breakdown")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🏠 Main Dough Ingredients**")
            display_df = main_dough_df.copy()
            display_df['Weight (g)'] = display_df['Weight (g)'].round(1)
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=False
            )

            total_weight = display_df['Weight (g)'].sum()
            st.metric("Total dough weight", f"{total_weight:.0f}g")

        with col2:
            st.markdown("**🧪 Ferment Preparation**")

            for ferment_name, ingredients in ferments_data.items():
                if any(v > 1 for v in ingredients.values()):  # Only show if meaningful amounts
                    with st.container():
                        st.markdown(f"*{ferment_name}:*")
                        for ing_name, weight in ingredients.items():
                            if weight > 1:
                                st.write(f"• {ing_name}: **{weight:.0f}g**")
                        st.write(f"*Total: {sum(ingredients.values()):.0f}g*")
                        st.write("")

# Tab 3: Technical View
with tab3:
    if not total_ingredients_df.empty:
        st.subheader("🔬 Baker's Percentages & Technical Details")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Total Formula**")
            display_total = total_ingredients_df.copy()
            display_total = display_total[display_total['Weight (g)'] > 0.1]
            display_total.loc["Total"] = [
                display_total["Baker's %"].sum(),
                display_total["Weight (g)"].sum(),
            ]
            st.dataframe(
                display_total.style.format({
                    "Baker's %": "{:.1f}%",
                    "Weight (g)": "{:.1f}g"
                }),
                use_container_width=True
            )

        with col2:
            st.markdown("**Ferment Details**")
            for ferment_name, ingredients in ferments_data.items():
                st.markdown(f"*{ferment_name}:*")
                df = pd.DataFrame.from_dict(
                    ingredients, orient="index", columns=["Weight (g)"]
                )
                df = df[df['Weight (g)'] > 0.1]
                if not df.empty:
                    df.loc["Total"] = df["Weight (g)"].sum()
                    st.dataframe(
                        df.style.format("{:.1f}g"),
                        use_container_width=True
                    )
                st.write("")

        with col3:
            st.markdown("**Key Calculations**")
            st.metric("Pre-fermented flour", f"{pre_fermented_flour:.1f}g")
            st.metric("Scale factor", f"{scale}")

            # Show flour breakdown
            strong_flour_pct = 100.0 - flour2_pct - flour3_pct
            st.write("**Flour composition:**")
            st.write(f"• Strong white: {strong_flour_pct:.1f}%")
            if flour2_pct > 0:
                st.write(f"• Flour 2: {flour2_pct:.1f}%")
            if flour3_pct > 0:
                st.write(f"• Flour 3: {flour3_pct:.1f}%")

# Footer
st.markdown("---")
st.markdown(
    "*Based on the [original spreadsheet](https://docs.google.com/spreadsheets/d/1m1cki9dIE_zkLR6F6RSErP0Kwx4MRXgiJJBIxCvln1k/edit?usp=sharing). "
    "Happy baking! 🥖*"
)
