import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from src.styles import apply_custom_theme, get_plotly_layout
from src.live_data import (
    fetch_latest_indicator, fetch_historical_series,
    get_current_macro_snapshot, get_recession_probability,
    get_fred_client
)
from src.visualizations import plot_macro_gauge

st.set_page_config(page_title="Live Dashboard", layout="wide")
apply_custom_theme()

st.markdown('<div class="section-label">REAL-TIME DATA</div>', unsafe_allow_html=True)
st.markdown("# Live Macro Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")

# Check FRED connection
fred = get_fred_client()
if not fred:
    st.error("FRED API not configured. Add your API key to `.streamlit/secrets.toml`")
    st.code('FRED_API_KEY = "your_key_here"', language="toml")
    st.info("Get your free API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
    st.stop()

# Fetch snapshot
with st.spinner("Fetching latest data..."):
    snapshot = get_current_macro_snapshot()
    recession_prob = get_recession_probability()

st.divider()

# Key Indicators Row
st.markdown("## Key Economic Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    val = snapshot.get("inflation")
    st.metric(
        "Inflation (YoY)",
        f"{val}%" if val else "N/A",
        delta=f"Target: 2.0%" if val else None,
        delta_color="inverse"
    )

with col2:
    val = snapshot.get("fed_funds_rate")
    st.metric(
        "Fed Funds Rate",
        f"{val}%" if val else "N/A"
    )

with col3:
    val = snapshot.get("unemployment")
    st.metric(
        "Unemployment",
        f"{val}%" if val else "N/A"
    )

with col4:
    val = snapshot.get("us_10y_yield")
    st.metric(
        "10Y Treasury",
        f"{val}%" if val else "N/A"
    )

st.write("")

# Recession Probability Gauge
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Recession Signal")
    if recession_prob is not None:
        fig = plot_macro_gauge(
            recession_prob,
            "Recession Probability (18mo)",
            min_val=0, max_val=100,
            threshold_low=30, threshold_high=60
        )
        st.plotly_chart(fig, use_container_width=True)
        
        if recession_prob >= 70:
            st.error(f"HIGH RISK: {recession_prob}% probability based on yield curve")
        elif recession_prob >= 40:
            st.warning(f"MODERATE RISK: {recession_prob}%")
        else:
            st.success(f"LOW RISK: {recession_prob}%")

with col2:
    st.markdown("### Yield Curve Status")
    yc = snapshot.get("yield_curve")
    if yc is not None:
        curve_data = fetch_historical_series("T10Y2Y", years=5)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=curve_data.index,
            y=curve_data.values,
            mode='lines',
            line=dict(color='#00D4FF', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 255, 0.1)',
            name='10Y-2Y Spread'
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="#FF3B6B", line_width=2,
                      annotation_text="Inversion Line", annotation_position="right")
        
        layout = get_plotly_layout(
            title="<b>10Y-2Y Treasury Spread</b>",
            height=350,
            yaxis_title="Spread (%)",
            showlegend=False
        )
        fig.update_layout(layout)
        st.plotly_chart(fig, use_container_width=True)
        
        if yc < 0:
            st.error(f"🔴 Curve INVERTED ({yc}%) — Historical recession signal")
        else:
            st.success(f"🟢 Curve NORMAL ({yc}%)")

st.divider()

# Historical Comparison
st.markdown("## Current vs Historical Crisis Conditions")
st.caption("How today's macro environment compares to pre-crisis conditions")

from src.data_loader import load_events
events = load_events()

comparison_data = []
for event in events:
    pre = event["pre_conditions"]
    if pre.get("inflation") and pre.get("fed_funds_rate"):
        comparison_data.append({
            "Event": f"{event['name']} ({event['year']})",
            "Inflation": pre.get("inflation"),
            "Fed Rate": pre.get("fed_funds_rate"),
            "Unemployment": pre.get("unemployment"),
            "GDP Growth": pre.get("gdp_growth")
        })

# Add current
comparison_data.append({
    "Event": "TODAY",
    "Inflation": snapshot.get("inflation"),
    "Fed Rate": snapshot.get("fed_funds_rate"),
    "Unemployment": snapshot.get("unemployment"),
    "GDP Growth": None
})

df_comp = pd.DataFrame(comparison_data)

# Scatter plot
fig = go.Figure()

for i, row in df_comp.iterrows():
    is_today = "TODAY" in row["Event"]
    fig.add_trace(go.Scatter(
        x=[row["Inflation"]],
        y=[row["Fed Rate"]],
        mode='markers+text',
        marker=dict(
            size=25 if is_today else 15,
            color='#FF3B6B' if is_today else '#00D4FF',
            symbol='star' if is_today else 'circle',
            line=dict(color='#FFFFFF', width=2 if is_today else 1)
        ),
        text=[row["Event"]],
        textposition="top center",
        textfont=dict(size=9, color='#E4E8F1'),
        name=row["Event"],
        showlegend=False
    ))

layout = get_plotly_layout(
    title="<b>Inflation vs Fed Funds Rate — Historical Crisis Mapping</b>",
    xaxis_title="Inflation Rate (%)",
    yaxis_title="Fed Funds Rate (%)",
    height=600
)
fig.update_layout(layout)
st.plotly_chart(fig, use_container_width=True)

st.info(" **Interpretation**: Today's position on this map helps identify which historical crises had similar macro conditions. Events in your quadrant are the most relevant precedents.")