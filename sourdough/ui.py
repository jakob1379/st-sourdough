from __future__ import annotations

import streamlit as st
import pandas as pd
from sourdough.calculations import calculate_recipe, FermentsData

# Cached wrappers for expensive or repeatable computations
@st.cache_data
def get_recipe_cached(
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
) -> tuple[pd.DataFrame, pd.DataFrame, FermentsData, float, float, float]:
    """Cached wrapper around the pure calculate_recipe function.

    Keeping caching in the UI module keeps calculations.py importable without Streamlit.
    """
    return calculate_recipe(
        dough_weight, sourdough_discard_pct, preferment_pct, scale,
        flour2_pct, flour3_pct, water_pct, salt_pct, yeast_pct, barley_malt_pct,
        inclusion2_pct, inclusion3_pct, discard_flour_pct, discard_water_pct,
        preferment_flour_pct, preferment_water_pct, preferment_yeast_pct
    )


@st.cache_data
def build_recipe_items(
    main_items: tuple[tuple[str, float], ...],
    flour2_pct: float,
    flour3_pct: float,
) -> dict[str, float]:
    """Build user-friendly recipe items for the shopping list from stable, hashable input.

    main_items must be a tuple of (ingredient_name, weight) pairs so it's hashable for caching.
    """
    recipe_items: dict[str, float] = {}
    for ingredient, weight in main_items:
        if weight > 1:  # Only show meaningful amounts
            if ingredient == "Strong White flour":
                recipe_items["Strong white bread flour"] = weight
            elif ingredient == "Flour 2" and weight > 0:
                recipe_items[f"Alternative flour ({flour2_pct:.0f}% of total)"] = weight
            elif ingredient == "Sourdough discard":
                recipe_items["Sourdough discard (100% hydration)"] = weight
            elif ingredient == "Pre-ferment":
                recipe_items["Pre-ferment (prepare night before)"] = weight
            elif ingredient == "Barley Malt Extract" and weight > 0:
                recipe_items["Barley malt extract (or honey)"] = weight
            else:
                recipe_items[ingredient] = weight
    return recipe_items


@st.cache_data
def ferment_df_from_items(items: tuple[tuple[str, float], ...]) -> pd.DataFrame:
    """Convert ferment items (tuple of pairs) into a small DataFrame suitable for display.

    items: tuple of (ingredient_name, weight)
    """
    df = pd.DataFrame.from_dict(dict(items), orient="index", columns=["Weight (g)"])
    df = df[df["Weight (g)"] > 0.1]
    if not df.empty:
        df.loc["Total"] = df["Weight (g)"].sum()
    return df


@st.cache_data
def build_total_display(items: tuple[tuple[str, float, float], ...]) -> pd.DataFrame:
    """Build the display DataFrame for total ingredients.

    items: tuple of (ingredient_name, baker_pct, weight)
    """
    if not items:
        return pd.DataFrame(columns=["Baker's %", "Weight (g)"])

    df = pd.DataFrame(items, columns=["Ingredient", "Baker's %", "Weight (g)"]).set_index("Ingredient")
    df = df[df["Weight (g)"] > 0.1]
    if not df.empty:
        df.loc["Total"] = [df["Baker's %"].sum(), df["Weight (g)"].sum()]
    return df


def _render_tab1(
    main_dough_df: pd.DataFrame,
    flour2_pct: float,
    flour3_pct: float,
    water_pct: float,
    salt_pct: float,
    sourdough_discard_pct: float,
    preferment_pct: float,
    preferment_total_weight: float,
) -> None:
    """Render the simplified, user-facing recipe (Tab 1)."""
    if not main_dough_df.empty:
        st.success(f"🎉 **Your recipe is ready!** Total dough weight: **{main_dough_df['Weight (g)'].sum():.0f}g**")

        # Key metrics with helpful context
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💧 Hydration", f"{water_pct}%", help="Perfect for sandwich bread texture")
        with col2:
            st.metric("🧂 Salt", f"{salt_pct}%", help="Balanced flavor enhancement")
        with col3:
            st.metric("♻️ Discard Used", f"{sourdough_discard_pct:.0f}%", help="Waste nothing, gain flavor!")
        with col4:
            st.metric("⏰ Pre-ferment", f"{preferment_pct:.0f}%", help="Complex artisan flavors")

        st.markdown("---")

        # Preparation timeline
        st.subheader("📅 Your Baking Schedule")
        st.info(f"""
        **Tonight (5 minutes):** Make your pre-ferment ({preferment_total_weight:.0f}g total)

        **Tomorrow morning:** Start mixing your dough - total process is about 5-6 hours

        **Fresh bread by afternoon!** Perfect timing for dinner or next day's sandwiches
        """)

        st.markdown("---")

        # Simple shopping list view
        st.subheader("🛒 Shopping List & Recipe")
        st.markdown("*Everything you need, nothing you don't*")

        # Filter and rename for user-friendly display (cached)
        main_items = tuple(main_dough_df['Weight (g)'].items())
        recipe_items = build_recipe_items(main_items, flour2_pct, flour3_pct)

        # Display in a clean, printable format
        for ingredient, weight in recipe_items.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{ingredient}**")
            with col2:
                st.write(f"**{weight:.0f}g**")

        # Pro tips section
        st.markdown("---")
        st.subheader("🏆 Pro Tips for Success")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **🎯 For Best Results**:
             - Use bread flour with 12%+ protein
             - Room temperature water mixes easier
             - Don't rush the bulk fermentation
             - Score your loaf for even baking
            """)

        with col2:
            st.markdown("""
            **🔧 Troubleshooting:**
             - Dough too sticky? Use wet hands, not more flour
             - Slow rise? Find a warmer spot (22-25°C ideal)
             - Want more sourness? Use older discard
             - Dense bread? Check your starter is active
            """)
    else:
        st.error("⚠️ Unable to calculate recipe. Please check your input values in the sidebar.")


def _render_tab2(main_dough_df: pd.DataFrame, ferments_data: FermentsData) -> None:
    """Render the Recipe Details tab (Tab 2)."""
    if not main_dough_df.empty:
        st.subheader("📊 Complete Recipe Breakdown")
        st.markdown("*Perfect for experienced bakers who want to understand the full process*")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🏠 Final Dough Assembly**")
            st.markdown("*Mix these together on baking day*")
            display_df = main_dough_df.copy()
            display_df['Weight (g)'] = display_df['Weight (g)'].round(1)
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=False
            )

            total_weight = display_df['Weight (g)'].sum()
            st.metric("Total dough weight", f"{total_weight:.0f}g")

            st.markdown("**⏱️ Timeline Estimate**")
            st.markdown("""
            - **Mixing:** 10 minutes
            - **Bulk fermentation:** 4-5 hours
            - **Shaping & final proof:** 1-2 hours
            - **Baking:** 35-45 minutes
            """)

        with col2:
            st.markdown("**🧪 Ferment Preparation Guide**")
            st.markdown("*Prepare these components separately*")

            for ferment_name, ingredients in ferments_data.items():
                # Use cached helper to turn ferment dict into a small DataFrame for display
                items_tuple = tuple(ingredients.items())
                df = ferment_df_from_items(items_tuple)
                if not df.empty:
                    with st.container():
                        if ferment_name == "Sourdough discard":
                            st.markdown(f"**{ferment_name}** *(use directly from fridge)*")
                            st.caption("Your regular sourdough discard at 100% hydration")
                        else:
                            st.markdown(f"**{ferment_name}** *(make night before)*")
                            st.caption("Mix and ferment 8-12 hours at room temperature")

                        # Display the ferment components and total from the cached DataFrame
                        st.dataframe(df.style.format("{:.0f}g"), use_container_width=True)
                        st.write("")

            st.markdown("**🌡️ Temperature Guide**")
            st.info("""
            **Kitchen 18-20°C:** Add 1-2 hours to all times
            **Kitchen 20-23°C:** Perfect - follow timing exactly
            **Kitchen 24-27°C:** Subtract 1 hour, watch carefully
            **Kitchen 28°C+:** Consider cooler location or less yeast
            """)


def _render_tab3(
    total_ingredients_df: pd.DataFrame,
    ferments_data: FermentsData,
    pre_fermented_flour: float,
    scale: float,
    total_flour_weight: float,
    water_pct: float,
    flour2_pct: float,
    flour3_pct: float,
) -> None:
    """Render the Technical View tab (Tab 3)."""
    if not total_ingredients_df.empty:
        st.subheader("🔬 Baker's Percentages & Technical Analysis")
        st.markdown("*For bakers who want to understand and modify the formula*")

        with st.expander("📚 Understanding Baker's Percentages", expanded=False):
            st.markdown("""
            Baker's percentages express each ingredient as a percentage of the total flour weight (always 100%).
            This system lets you:
            - **Scale recipes easily** - double the percentages, double the recipe
            - **Compare formulas** - see how different breads relate
            - **Adjust confidently** - know the impact of changes

            **Example:** 72% hydration means 72g water per 100g flour
            """)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**📋 Master Formula**")
            st.caption("*Total ingredient breakdown*")

            # Prepare hashable items and use cached builder for consistent display
            items = tuple(
                (idx, row["Baker's %"], row["Weight (g)"])
                for idx, row in total_ingredients_df.iterrows()
            )
            display_total = build_total_display(items)

            st.dataframe(
                display_total.style.format({
                    "Baker's %": "{:.1f}%",
                    "Weight (g)": "{:.1f}g"
                }),
                use_container_width=True
            )

        with col2:
            st.markdown("**🔬 Ferment Analysis**")
            st.caption("*Component breakdown*")
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
            st.markdown("**📊 Key Metrics**")
            st.caption("*Formula characteristics*")
            st.metric("Pre-fermented flour", f"{pre_fermented_flour:.1f}g")
            st.metric("Scale factor", f"{scale}")
            st.metric("Total flour", f"{total_flour_weight:.0f}g")
            st.metric("Effective hydration", f"{water_pct:.1f}%")

            # Show flour breakdown
            st.markdown("**🌾 Flour composition:**")
            strong_flour_pct = 100.0 - flour2_pct - flour3_pct
            st.write(f"• Strong white: {strong_flour_pct:.1f}%")
            if flour2_pct > 0:
                st.write(f"• Alternative: {flour2_pct:.1f}%")
            if flour3_pct > 0:
                st.write(f"• Third flour: {flour3_pct:.1f}%")

        st.markdown("---")

        # Formula modification guide
        st.markdown("**🎛️ Formula Modification Guide**")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **Common Adjustments:**
            - **More open crumb:** +5% hydration
            - **Tighter crumb:** -5% hydration
            - **More sour:** +10% discard, -10% pre-ferment
            - **Faster rise:** +0.2% commercial yeast
            - **Slower rise:** -0.2% commercial yeast
            """)

        with col2:
            st.markdown("""
            **Safety Limits:**
            - **Hydration:** 60-85% for this style
            - **Salt:** 1.5-2.5% (never less than 1.5%)
            - **Yeast:** 0.2-1.0% (more = commercial flavor)
            - **Alternative flours:** Max 30% total
            - **Inclusions:** Max 15% total weight
            """)



def render_app() -> None:
    """Render the Streamlit UI for the sourdough calculator.

    This function is intended to be the entry point called by Streamlit (``streamlit run main.py``).
    It builds the sidebar inputs, handles the advanced/simple mode toggle and renders three main tabs:
    - "Your Recipe" (simple view)
    - "Recipe Details" (detailed breakdown)
    - "Technical View" (baker's percentages and analysis)
    """
    st.set_page_config(layout="wide", page_title="Sourdough Recipe Calculator")

    # Initialize session state for advanced mode
    if 'show_advanced' not in st.session_state:
        st.session_state.show_advanced = False

    # Header with better branding
    st.title("🍞 Sourdough Recipe Calculator")
    st.markdown("**Waste Not Want Not** - Turn your sourdough discard into delicious bread")

    # Add introductory guidance
    st.info(
        """
    👋 **Welcome to the Culinary Exploration sourdough calculator!** This tool helps you create perfectly balanced
    farmhouse-style sandwich loaves using your sourdough discard. The recipe produces a beautiful, soft crumb with complex
    flavors from extended fermentation. **New to sourdough?** Start with the default settings and adjust as you learn!
    """
    )

    # Toggle for advanced mode
    col1, col2 = st.columns([3, 1])
    with col2:
        def _toggle_advanced():
            st.session_state.show_advanced = not st.session_state.show_advanced

        st.button(
            "⚙️ Advanced Settings" if not st.session_state.show_advanced else "📝 Simple Mode",
            key="toggle_advanced",
            on_click=_toggle_advanced,
        )

    # Main interface with tabs
    tab1, tab2, tab3 = st.tabs(["🥖 Your Recipe", "📊 Recipe Details", "🔬 Technical View"])

    # Essential inputs in sidebar - always visible
    with st.sidebar:
        st.header("🎯 Recipe Basics")
        st.markdown("*Adjust these core settings to customize your bread*")

        dough_weight = st.number_input(
            "🍞 Target dough weight (g)",
            value=900,
            min_value=100,
            help="This determines the final size of your loaf. 900g makes a perfect sandwich loaf that fits most bread tins. Smaller amounts work great for rolls!"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            water_pct = st.number_input(
                "💧 Hydration (%)",
                value=72.0,
                min_value=50.0,
                max_value=100.0,
                help="Higher hydration = more open crumb and chewier texture. 72% gives a balanced, sandwich-friendly crumb. Beginners should start here!"
            )
        with col_b:
            salt_pct = st.number_input(
                "🧂 Salt (%)",
                value=2.0,
                min_value=1.0,
                max_value=5.0,
                help="Salt enhances flavor and controls fermentation. 2% is the sweet spot for most breads. Never go below 1.5% or above 2.5% for table bread."
            )

        st.markdown("#### ♻️ The Magic of Discard")
        st.markdown("*This is what makes your bread special!*")

        sourdough_discard_pct = st.slider(
            "Sourdough discard usage",
            min_value=0.0,
            max_value=50.0,
            value=30.0,
            step=5.0,
            format="%.0f%%",
            help="Higher percentage = more sourdough flavor and better use of discard. 30% gives beautiful flavor without overpowering. This is the 'Waste Not Want Not' philosophy in action!"
        )

        preferment_pct = st.slider(
            "Pre-ferment (poolish)",
            min_value=0.0,
            max_value=50.0,
            value=30.0,
            step=5.0,
            format="%.0f%%",
            help="Pre-fermentation develops complex flavors and improves texture. 30% creates the perfect balance - your bread will taste like it came from an artisan bakery!"
        )

        # Advanced settings - collapsible
        if st.session_state.show_advanced:
            st.markdown("---")
            st.header("⚙️ Advanced Options")
            st.markdown("*For experienced bakers who want full control*")

            with st.expander("📐 Scaling & Yeast Control", expanded=False):
                st.markdown("*Perfect for adapting recipes or controlling fermentation speed*")
                scale = st.number_input(
                    "Recipe scale multiplier",
                    value=1.0,
                    min_value=0.1,
                    format="%.2f",
                    help="Scale the entire recipe up or down. 2.0 doubles everything, 0.5 halves it. Useful for different tin sizes!"
                )
                yeast_pct = st.number_input(
                    "🦠 Commercial yeast (%)",
                    value=0.5,
                    min_value=0.0,
                    format="%.2f",
                    help="Think of yeast as 'speed control' - less yeast = slower, more flavorful fermentation. 0.5% gives you control without commercial yeast flavor."
                )
                barley_malt_pct = st.number_input(
                    "🌾 Barley malt extract (%)",
                    value=3.0,
                    min_value=0.0,
                    format="%.2f",
                    help="Adds deep, malty sweetness and improves crust color. You can substitute with honey (use half the amount) or molasses for different flavors."
                )
                flour2_pct = st.number_input(
                    "Alternative flour (%)",
                    value=15.0,
                    min_value=0.0,
                    format="%.2f",
                    help="Try wholewheat (15% is perfect), rye for earthiness, or spelt for nuttiness. Don't exceed 25% or the bread might not rise properly."
                )
                flour3_pct = st.number_input(
                    "Third flour type (%)",
                    value=0.0,
                    min_value=0.0,
                    format="%.2f",
                    help="For complex blends - maybe add some rye if you're already using wholewheat. Keep total alternative flours under 30%."
                )

            with st.expander("➕ Mix-ins & Inclusions", expanded=False):
                st.markdown("*Add seeds, nuts, or dried fruit to make it your own*")
                inclusion2_pct = st.number_input(
                    "Seeds/nuts (%)",
                    value=0.0,
                    min_value=0.0,
                    format="%.2f",
                    help="Sunflower seeds, pumpkin seeds, or chopped walnuts work beautifully. 5-8% is usually perfect."
                )
                inclusion3_pct = st.number_input(
                    "Dried fruit (%)",
                    value=0.0,
                    min_value=0.0,
                    format="%.2f",
                    help="Raisins, dried cranberries, or chopped dates. Soak them briefly in warm water first to prevent them from stealing moisture from your dough."
                )

            with st.expander("🧪 Ferment Composition (Expert Level)", expanded=False):
                st.markdown("*Fine-tune the hydration and composition of your ferments*")
                st.info("⚠️ **Advanced users only** - These ratios control the internal composition of your sourdough discard and pre-ferment. The defaults work perfectly for most situations.")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Sourdough Discard Ratios**")
                    discard_flour_pct = st.number_input("Discard flour ratio", value=100.0, format="%.1f")
                    discard_water_pct = st.number_input("Discard water ratio", value=100.0, format="%.1f")

                with col2:
                    st.markdown("**Pre-ferment Ratios**")
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

        # Helpful tips section
        st.markdown("---")
        st.markdown("### 💡 Quick Tips")
        with st.expander("🕐 Timing your bake", expanded=False):
            st.markdown("""
            **Make your pre-ferment the night before** (takes 2 minutes)
            **Next morning:** Mix dough → wait 4-5 hours → shape → proof 1 hour → bake
            **Total hands-on time:** About 30 minutes spread across the day
            """)

        with st.expander("🌡️ Temperature matters", expanded=False):
            st.markdown("""
            **Warm kitchen (25°C+):** Everything goes faster - reduce yeast or use cooler water
            **Cool kitchen (18°C-):** Things slow down - find a warmer spot or be patient
            **Sweet spot:** 20-23°C for predictable timing
            """)

    # Calculate recipe (cached)
    (total_ingredients_df, main_dough_df, ferments_data, pre_fermented_flour,
     sourdough_discard_total_weight, preferment_total_weight) = get_recipe_cached(
        dough_weight, sourdough_discard_pct, preferment_pct, scale,
        flour2_pct, flour3_pct, water_pct, salt_pct, yeast_pct, barley_malt_pct,
        inclusion2_pct, inclusion3_pct, discard_flour_pct, discard_water_pct,
        preferment_flour_pct, preferment_water_pct, preferment_yeast_pct
    )

    # Calculate total flour weight from the returned data
    total_flour_weight = 0
    if not total_ingredients_df.empty:
        flour_ingredients = ["Strong white flour", "Flour 2", "Flour 3"]
        for ingredient in flour_ingredients:
            if ingredient in total_ingredients_df.index:
                total_flour_weight += total_ingredients_df.loc[ingredient, "Weight (g)"]

    # Tab 1: Simple Recipe View
    with tab1:
        _render_tab1(
            main_dough_df=
            main_dough_df,
            flour2_pct=flour2_pct,
            flour3_pct=flour3_pct,
            water_pct=water_pct,
            salt_pct=salt_pct,
            sourdough_discard_pct=sourdough_discard_pct,
            preferment_pct=preferment_pct,
            preferment_total_weight=preferment_total_weight,
        )

    # Tab 2: Recipe Details
    with tab2:
        _render_tab2(main_dough_df=main_dough_df, ferments_data=ferments_data)

    # Tab 3: Technical View
    with tab3:
        _render_tab3(
            total_ingredients_df=total_ingredients_df,
            ferments_data=ferments_data,
            pre_fermented_flour=pre_fermented_flour,
            scale=scale,
            total_flour_weight=total_flour_weight,
            water_pct=water_pct,
            flour2_pct=flour2_pct,
            flour3_pct=flour3_pct,
        )

    # Footer with attribution and helpful links
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **🔗 Learn More:**
        [Original Spreadsheet](https://docs.google.com/spreadsheets/d/1m1cki9dIE_zkLR6F6RSErP0Kwx4MRXgiJJBIxCvln1k/edit?usp=sharing)
        [Culinary Exploration](https://www.culinaryexploration.eu/)
        """)

    with col2:
        st.markdown("""
        **📺 Watch & Learn:**
        [Recipe Video Tutorial](https://www.youtube.com/watch?v=r0HQbQQDDe8)
        [Sourdough Starter Guide](https://www.culinaryexploration.eu/blog/sourdough-starter)
        """)

    with col3:
        st.markdown("""
        **🍞 Happy Baking!**
        *Remember: Great bread takes time,
        but the results are worth it.*
        """)
