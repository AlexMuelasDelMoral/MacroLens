"""Top navigation bar for MacroLens.

Renders a permanent horizontal nav bar across every page using
st.page_link inside a styled container. Call render_navbar() at
the top of every page file, immediately after apply_custom_theme().
"""
from __future__ import annotations
import streamlit as st


NAV_ITEMS = [
    ("Home",            "app.py",                        "Home"),
    ("Event Explorer",  "pages/1_Event_Explorer.py",     "Explorer"),
    ("Scenario Builder","pages/2_Scenario_Builder.py",   "Scenarios"),
    ("Stress Test",     "pages/3_Portfolio_Stress_Test.py","Stress Test"),
    ("Learn",           "pages/4_Learn.py",              "Learn"),
    ("Backtest",        "pages/5_Backtest.py",           "Backtest"),
    ("Live Dashboard",  "pages/6_Live_Dashboard.py",     "Live"),
    ("Methodology",     "pages/8_Methodology.py",        "Methodology"),
]


def render_navbar() -> None:
    """Render the top navigation bar."""
    st.markdown('<div class="macrolens-nav">', unsafe_allow_html=True)
    cols = st.columns([1.2] + [1] * (len(NAV_ITEMS) - 1))
    for col, (label, page, short) in zip(cols, NAV_ITEMS):
        with col:
            st.page_link(page, label=short)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-spacer"></div>', unsafe_allow_html=True)
