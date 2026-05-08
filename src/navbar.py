"""Top navigation bar for MacroLens."""
from __future__ import annotations
import streamlit as st

NAV_ITEMS = [
    ("Event Explorer",   "pages/1_Event_Explorer.py",       "Explorer"),
    ("Scenario Builder", "pages/2_Scenario_Builder.py",     "Scenarios"),
    ("Stress Test",      "pages/3_Portfolio_Stress_Test.py","Stress Test"),
    ("Learn",            "pages/4_Learn.py",                "Learn"),
    ("Backtest",         "pages/5_Backtest.py",             "Backtest"),
    ("Live Dashboard",   "pages/6_Live_Dashboard.py",       "Live"),
    ("About",            "pages/7_About.py",                "About"),
    ("Methodology",      "pages/8_Methodology.py",          "Methodology"),
]

def render_navbar() -> None:
    brand_col, *nav_cols = st.columns([2] + [1] * len(NAV_ITEMS))
    with brand_col:
        st.page_link("app.py", label="MacroLens")
    for col, (label, page, short) in zip(nav_cols, NAV_ITEMS):
        with col:
            st.page_link(page, label=short)
    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
