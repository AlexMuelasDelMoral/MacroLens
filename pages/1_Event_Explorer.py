import streamlit as st
import pandas as pd
from src.styles import apply_custom_theme
from src.data_loader import (
    load_events, load_impacts, get_asset_classes,
    ASSET_LABELS, ASSET_CATEGORIES
)
from src.visualizations import plot_impact_bar, plot_multi_asset_heatmap
from src.theory_engine import get_relevant_theories, get_asset_narrative

st.set_page_config(page_title="Event Explorer", layout="wide")
apply_custom_theme()

st.markdown('<div class="section-label">HISTORICAL ANALYSIS</div>', unsafe_allow_html=True)
st.markdown("# Event Explorer")
st.caption("Deep dive into historical economic events and their market impacts across 45 asset classes")

st.divider()

events = load_events()
impacts = load_impacts()

# Event selection with category filter
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    categories = sorted(set(e["category"] for e in events))
    category_filter = st.selectbox(
        "Filter by Category",
        options=["All Categories"] + categories
    )

with col2:
    filtered_events = events if category_filter == "All Categories" else [
        e for e in events if e["category"] == category_filter
    ]
    # Sort by severity descending
    filtered_events = sorted(filtered_events, key=lambda x: -x["severity"])
    
    event_names = {f"{e['name']} ({e['year']}) — Severity {e['severity']}/10": e["id"] 
                   for e in filtered_events}
    
    if not event_names:
        st.warning("No events match this filter")
        st.stop()
    
    selected_name = st.selectbox(
        "Select Historical Event",
        options=list(event_names.keys())
    )
    selected_id = event_names[selected_name]

with col3:
    selected_event = next(e for e in events if e["id"] == selected_id)
    st.metric("Severity", f"{selected_event['severity']}/10")

# Event Header Card
st.divider()

st.markdown(f"""
<div class="glass-card" style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(124, 58, 237, 0.08) 100%); border-color: rgba(0, 212, 255, 0.2);">
    <div style="color: #00D4FF; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; margin-bottom: 0.5rem;">
        {selected_event['category'].upper()}
    </div>
    <h2 style="margin: 0 0 0.5rem 0; border: none; padding: 0; color: #E4E8F1;">
        {selected_event['name']}
    </h2>
    <div style="color: #8B92B0; font-size: 1rem; line-height: 1.6;">
        {selected_event['description']}
    </div>
</div>
""", unsafe_allow_html=True)

# Event Metadata
col1, col2, col3, col4 = st.columns(4)
col1.metric("Year", selected_event["year"])
col2.metric("Duration", f"{selected_event['duration_months']} months")
col3.metric("Geography", selected_event["geography"])
col4.metric("Start Date", selected_event["start_date"])

# Triggers
st.markdown("### Key Triggers")
trigger_cols = st.columns(len(selected_event["triggers"]))
for i, trigger in enumerate(selected_event["triggers"]):
    with trigger_cols[i]:
        st.markdown(f"""
        <div style="background: rgba(19, 24, 54, 0.6); border: 1px solid rgba(42, 49, 88, 0.5); 
                    border-radius: 10px; padding: 1rem; text-align: center; height: 100%;">
            <div style="color: #00D4FF; font-size: 1.5rem; margin-bottom: 0.5rem;">▸</div>
            <div style="color: #E4E8F1; font-size: 0.9rem;">{trigger}</div>
        </div>
        """, unsafe_allow_html=True)

# Pre-event conditions
st.markdown("### Pre-Event Macro Conditions")
pre = selected_event["pre_conditions"]

cols = st.columns(5)
cols[0].metric(
    "Inflation",
    f"{pre.get('inflation')}%" if pre.get('inflation') is not None else "N/A"
)
cols[1].metric(
    "Fed Funds Rate",
    f"{pre.get('fed_funds_rate')}%" if pre.get('fed_funds_rate') is not None else "N/A"
)
cols[2].metric(
    "Unemployment",
    f"{pre.get('unemployment')}%" if pre.get('unemployment') is not None else "N/A"
)
cols[3].metric(
    "GDP Growth",
    f"{pre.get('gdp_growth')}%" if pre.get('gdp_growth') is not None else "N/A"
)
cols[4].metric(
    "VIX",
    f"{pre.get('vix')}" if pre.get('vix') is not None else "N/A"
)

st.divider()

# Impact visualization
if selected_id in impacts:
    st.markdown("## Market Impact Analysis")
    
    # Heatmap with category filter
    col1, col2 = st.columns([1, 3])
    with col1:
        heatmap_category = st.selectbox(
            "Filter heatmap",
            options=["All Categories"] + list(ASSET_CATEGORIES.keys()),
            key="heatmap_filter"
        )
    
    # Filter impacts for heatmap
    if heatmap_category == "All Categories":
        filtered_impacts = impacts
    else:
        category_assets = ASSET_CATEGORIES[heatmap_category]
        filtered_event_impacts = {
            asset: data for asset, data in impacts[selected_id].items()
            if asset in category_assets
        }
        filtered_impacts = {selected_id: filtered_event_impacts}
    
    heatmap = plot_multi_asset_heatmap(filtered_impacts, selected_id)
    st.plotly_chart(heatmap, use_container_width=True)
    
    # Individual asset drill-down
    st.markdown("## Asset Class Deep Dive")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        asset_category_filter = st.selectbox(
            "Asset Category",
            options=["All"] + list(ASSET_CATEGORIES.keys()),
            key="asset_cat_filter"
        )
    
    with col2:
        # Build list of available assets based on category filter
        if asset_category_filter == "All":
            available = [
                a for a in get_asset_classes()
                if a in impacts[selected_id]
                and any(v is not None for v in impacts[selected_id][a].values())
            ]
        else:
            available = [
                a for a in ASSET_CATEGORIES[asset_category_filter].keys()
                if a in impacts[selected_id]
                and any(v is not None for v in impacts[selected_id][a].values())
            ]
        
        if not available:
            st.warning("No asset data available for this combination")
            st.stop()
        
        selected_asset = st.selectbox(
            "Select asset",
            options=available,
            format_func=lambda x: ASSET_LABELS.get(x, x)
        )
    
    # Display selected asset impact
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = plot_impact_bar(
            impacts[selected_id][selected_asset],
            selected_asset,
            selected_event["name"]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📖 Narrative")
        narrative = get_asset_narrative(selected_asset, selected_event["category"])
        st.info(narrative)
        
        # Quick stats
        asset_data = impacts[selected_id][selected_asset]
        values = [v for v in asset_data.values() if v is not None]
        if values:
            st.markdown("### Quick Stats")
            st.metric("Max Drawdown", f"{min(values):+.1f}%")
            st.metric("Best Recovery", f"{max(values):+.1f}%")
else:
    st.warning("Impact data for this event is being updated. Run `python scripts/build_impact_data.py` to generate data.")

st.divider()

# Economic theories
st.markdown("## Relevant Economic Theories")
theories = get_relevant_theories(selected_event["category"])

if theories:
    for theory in theories:
        with st.expander(f" {theory['name']}", expanded=False):
            st.markdown(f"**{theory['description']}**")
            st.markdown("**Market Implications:**")
            for asset, implication in theory["implications"].items():
                st.markdown(f"""
                <div style="padding: 0.75rem; background: rgba(19, 24, 54, 0.4); 
                            border-left: 3px solid #00D4FF; border-radius: 6px; margin-bottom: 0.5rem;">
                    <strong style="color: #00D4FF; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.1em;">
                        {asset.replace('_', ' ')}
                    </strong>
                    <div style="color: #E4E8F1; margin-top: 0.25rem;">{implication}</div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("No specific theoretical frameworks mapped for this event category.")