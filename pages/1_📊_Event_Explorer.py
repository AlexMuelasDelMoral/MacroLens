import streamlit as st
import pandas as pd
from src.data_loader import load_events, load_impacts, get_asset_classes, ASSET_LABELS
from src.visualizations import plot_impact_bar, plot_multi_asset_heatmap
from src.theory_engine import get_relevant_theories, get_asset_narrative

st.set_page_config(page_title="Event Explorer", page_icon="📊", layout="wide")

st.title("📊 Event Explorer")
st.markdown("Deep dive into historical economic events and their market impacts.")

events = load_events()
impacts = load_impacts()

# Event selection
col1, col2 = st.columns([2, 1])

with col1:
    event_names = {e["name"] + f" ({e['year']})": e["id"] for e in events}
    selected_name = st.selectbox(
        "Select Historical Event",
        options=list(event_names.keys())
    )
    selected_id = event_names[selected_name]

selected_event = next(e for e in events if e["id"] == selected_id)

with col2:
    st.metric("Severity", f"{selected_event['severity']}/10")

# Event details
st.divider()
st.header(f"📌 {selected_event['name']}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Category", selected_event["category"])
col2.metric("Duration", f"{selected_event['duration_months']} months")
col3.metric("Geography", selected_event["geography"])
col4.metric("Year", selected_event["year"])

st.info(f"**Description:** {selected_event['description']}")

# Triggers
st.markdown("**Key Triggers:**")
for trigger in selected_event["triggers"]:
    st.markdown(f"- {trigger}")

# Pre-event conditions
st.subheader("📈 Pre-Event Macro Conditions")
pre = selected_event["pre_conditions"]
cols = st.columns(5)
cols[0].metric("Inflation", f"{pre.get('inflation', 'N/A')}%" if pre.get('inflation') else "N/A")
cols[1].metric("Fed Funds Rate", f"{pre.get('fed_funds_rate', 'N/A')}%" if pre.get('fed_funds_rate') else "N/A")
cols[2].metric("Unemployment", f"{pre.get('unemployment', 'N/A')}%" if pre.get('unemployment') else "N/A")
cols[3].metric("GDP Growth", f"{pre.get('gdp_growth', 'N/A')}%" if pre.get('gdp_growth') else "N/A")
cols[4].metric("VIX", f"{pre.get('vix', 'N/A')}" if pre.get('vix') else "N/A")

st.divider()

# Impact visualization
if selected_id in impacts:
    st.header("💹 Market Impact Analysis")
    
    # Heatmap
    st.subheader("Full Asset Class Heatmap")
    heatmap = plot_multi_asset_heatmap(impacts, selected_id)
    st.plotly_chart(heatmap, use_container_width=True)
    
    # Individual asset drill-down
    st.subheader("🔍 Asset Class Deep Dive")
    
    available_assets = [a for a in get_asset_classes() 
                        if a in impacts[selected_id] and 
                        any(v is not None for v in impacts[selected_id][a].values())]
    
    selected_asset = st.selectbox(
        "Select asset class",
        options=available_assets,
        format_func=lambda x: ASSET_LABELS.get(x, x)
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = plot_impact_bar(impacts[selected_id][selected_asset], 
                              selected_asset, selected_event["name"])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📖 Narrative")
        narrative = get_asset_narrative(selected_asset, selected_event["category"])
        st.info(narrative)
else:
    st.warning("Impact data for this event is being updated. Check back soon!")

st.divider()

# Economic theories
st.header("📚 Relevant Economic Theories")
theories = get_relevant_theories(selected_event["category"])

for theory in theories:
    with st.expander(f"📖 {theory['name']}"):
        st.markdown(f"**Description:** {theory['description']}")
        st.markdown("**Implications:**")
        for asset, implication in theory["implications"].items():
            st.markdown(f"- **{asset.replace('_', ' ').title()}**: {implication}")
