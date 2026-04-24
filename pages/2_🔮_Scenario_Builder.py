import streamlit as st
import pandas as pd
from src.data_loader import get_asset_classes, ASSET_LABELS, get_categories
from src.similarity_engine import find_similar_events, aggregate_impact_prediction
from src.visualizations import plot_similarity_scores, plot_prediction_with_uncertainty
from src.theory_engine import get_relevant_theories

st.set_page_config(page_title="Scenario Builder", page_icon="🔮", layout="wide")

st.title("🔮 Scenario Builder")
st.markdown("Input current/hypothetical macro conditions and find similar historical precedents.")

st.divider()

# Input panel
st.header("📝 Set Macro Conditions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    inflation = st.number_input("Inflation Rate (%)", 
                                  min_value=-5.0, max_value=25.0, 
                                  value=3.5, step=0.1)
with col2:
    fed_rate = st.number_input("Fed Funds Rate (%)", 
                                min_value=0.0, max_value=20.0, 
                                value=5.25, step=0.25)
with col3:
    unemployment = st.number_input("Unemployment (%)", 
                                    min_value=2.0, max_value=15.0, 
                                    value=4.0, step=0.1)
with col4:
    gdp_growth = st.number_input("GDP Growth (%)", 
                                   min_value=-10.0, max_value=10.0, 
                                   value=2.0, step=0.1)

# Filters
col1, col2 = st.columns(2)
with col1:
    category_filter = st.selectbox(
        "Event Category (optional)",
        options=["All"] + get_categories()
    )
with col2:
    top_n = st.slider("Number of similar events", 3,
