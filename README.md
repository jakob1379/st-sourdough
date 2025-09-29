# Sourdough Recipe Calculator (Streamlit)

A small Streamlit app to compute sourdough bread formulas using baker's percentages. The app was refactored into a small package for better maintainability.

Features
- Simple and advanced modes
- Pre-ferment and discard composition handling
- Shopping list, technical breakdown, and ferment preparation guidance

Quickstart

1. Install dependencies (Python >= 3.13):

   uv sync

   or using pyproject.toml with a modern installer.

2. Run the app:

   streamlit run main.py

Project layout

- main.py — tiny entrypoint that calls sourdough.ui.render_app()
- sourdough/
  - __init__.py
  - calculations.py — core calculation logic (pure functions, typed)
  - ui.py — Streamlit UI, imports calculations

Contributing

Open a pull request with changes. Keep UI and calculation logic separated.

Credits

This calculator is based on the original formula and interface by Culinary Exploration (https://www.culinaryexploration.eu/). Please credit Culinary Exploration as the author of the original calculator when reusing or publishing derivatives.
