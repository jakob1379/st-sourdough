# UX review: Streamlit sourdough calculator — layout improvements & tasks

UX Review: Streamlit Sourdough Calculator (inspired by CulinaryExploration)

Summary
-------
I reviewed the Streamlit app layout and UX (sourdough/ui.py + main entry). The app is functional and well-structured, with a clear three-tab layout (Simple recipe, Recipe details, Technical view) and a comprehensive sidebar for inputs. The design follows the CulinaryExploration inspiration in content and flow, but there are several UX improvements that would increase clarity, accessibility, and discoverability — especially for new users and mobile visitors.

Positive points
---------------
- Clear separation between simple and advanced settings; sensible defaults.
- Useful three-tab division (shopping/simple, detailed breakdown, technical analysis).
- Helpful microcopy (tips, scheduling, and baking guidance) which aligns with CulinaryExploration tone.
- Caching used to keep UI responsive.

Key issues & recommendations (prioritized)
----------------------------------------
1) Sidebar overload & discoverability (High)
   - Problem: The sidebar mixes essential inputs, toggles, and a long advanced section that can be hidden; but new users may not discover advanced options or understand impact.
   - Recommendation: Reorganize sidebar into clear sections: "Quick start" (essential inputs), "Flavor & Ferments" (discard, preferment), "Advanced" (collapsible panel). Add short inline descriptions next to each setting and a link/button to "Show example output".
   - Effort: small

2) Advanced toggle UX (Medium)
   - Problem: The toggle is a button that changes label; state is stored in session but not persisted across sessions.
   - Recommendation: Use a checkbox or expander with a persistent configuration (e.g., query param or st.experimental_get/set) and add a short one-line summary when collapsed (e.g., "Yeast: 0.5% | Alt flour: 15%" ) so advanced values aren't hidden entirely.
   - Effort: small

3) Terminology & consistency with CulinaryExploration (Medium)
   - Problem: Ingredient labels differ slightly (e.g., "Strong White flour" vs "Strong white bread flour"); small mismatches can confuse users familiar with the original.
   - Recommendation: Use the same labels and help text as CulinaryExploration where appropriate; offer a "Show original terminology" toggle.
   - Effort: small

4) Mobile layout & responsiveness (High)
   - Problem: Wide layout with multi-column metrics and dataframes may be cramped on mobile.
   - Recommendation: Detect narrow screens and present a single-column stacked layout; collapse dataframes into accordions and provide a concise shopping list view for mobile.
   - Effort: medium

5) Accessibility (High)
   - Problem: No explicit ARIA hints; color/contrast and keyboard focus were not validated.
   - Recommendation: Ensure all interactive elements have accessible labels, verify color contrast for important badges/metrics, and ensure keyboard navigation order is logical. Use semantic titles and alt text for any images.
   - Effort: medium

6) Onboarding & presets (Medium)
   - Problem: New users might be unsure how to choose hydration, discard %, or preferment.
   - Recommendation: Add quick presets ("Beginner", "Moderate", "Open crumb") that set several parameters at once, plus a one-click "Reset to default". Add a short inline example for each preset.
   - Effort: medium

7) Output clarity and print-friendly format (Low)
   - Problem: Printing the shopping list or recipe could be more compact and printer-friendly.
   - Recommendation: Add a "Printable" view that renders the shopping list and step timeline in a single-column, high-contrast format optimized for A4.
   - Effort: small

8) Validation & safety limits (Low)
   - Problem: Some inputs allow extreme values (e.g., flour percentages >30 total alternative flours) without inline validation warnings.
   - Recommendation: Add inline validation and contextual warnings when users exceed recommended ranges.
   - Effort: small

Proposed tasks (issue checklist)
--------------------------------
- [ ] Reorganize sidebar into Quick Start / Flavor & Ferments / Advanced
- [ ] Convert Advanced toggle into persistent expander and show collapsed summary
- [ ] Align ingredient labels & help text with CulinaryExploration
- [ ] Add mobile responsive layout (single-column + collapsed dataframes)
- [ ] Audit and fix accessibility issues (labels, contrast, keyboard nav)
- [ ] Add user presets and Reset to defaults button
- [ ] Implement printable shopping list view
- [ ] Add inline validation & contextual warnings for limits

Files likely to change
---------------------
- sourdough/ui.py (primary)
- README.md (usage / presets documentation)
- Optional: add small CSS or Streamlit theming via .streamlit/config.toml

If you'd like, I can create the GitHub issue now with the report and the checklist as sub-tasks. I can also split the checklist into separate issues if you prefer one issue per major area (sidebar, mobile, accessibility, presets).
