import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from src.styles import apply_custom_theme, get_plotly_layout, render_page_header
from src.live_data import (
    fetch_latest_indicator, fetch_historical_series,
    get_current_macro_snapshot, get_recession_probability,
    get_fred_client
)
from src.visualizations import plot_macro_gauge
from src.portfolio_state import (
    has_portfolio, get_active_positions, portfolio_summary_string,
    portfolio_as_fractions,
)
from src.similarity_engine import find_similar_events, aggregate_impact_prediction

st.set_page_config(page_title="Live Dashboard", layout="wide")
apply_custom_theme()

render_page_header(
    label="REAL-TIME DATA",
    title="Live Macro Dashboard",
    subtitle="Current macroeconomic indicators and regime analysis from FRED",
)
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
        delta="Target: 2.0%" if val else None,
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
        st.plotly_chart(fig, width='stretch')
        
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

        if curve_data is not None and not curve_data.empty:
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
            st.plotly_chart(fig, width='stretch')

            if yc < 0:
                st.error(f"Curve inverted ({yc}%) — Historical recession signal")
            else:
                st.success(f"Curve normal ({yc}%)")
        else:
            st.info("Yield curve historical data unavailable. Check FRED API connection.")

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
st.plotly_chart(fig, width='stretch')

st.info(" **Interpretation**: Today's position on this map helps identify which historical crises had similar macro conditions. Events in your quadrant are the most relevant precedents.")

# ============ PORTFOLIO REGIME ANALYSIS ============
if has_portfolio():
    st.divider()
    st.markdown("## Portfolio Regime Analysis")
    st.caption(
        f"Active portfolio: {portfolio_summary_string()}. "
        "Based on current macro conditions, these are the most relevant "
        "historical precedents for your portfolio."
    )

    current_conditions = {
        k: v for k, v in {
            "inflation": snapshot.get("inflation"),
            "fed_funds_rate": snapshot.get("fed_funds_rate"),
            "unemployment": snapshot.get("unemployment"),
            "gdp_growth": snapshot.get("gdp_growth"),
        }.items() if v is not None
    }

    if len(current_conditions) >= 2:
        with st.spinner("Matching current conditions to historical events..."):
            similar = find_similar_events(current_conditions, top_n=5)

        if similar:
            st.markdown("### Closest historical analogs to today")
            analog_cols = st.columns(min(len(similar), 5))
            for i, item in enumerate(similar[:5]):
                event = item["event"]
                sim = item["similarity"]
                with analog_cols[i]:
                    color = "#00F5A0" if sim >= 60 else (
                        "#FFB547" if sim >= 40 else "#FF3B6B"
                    )
                    st.markdown(f"""
                    <div class="glass-card" style="text-align: center; padding: 1rem;">
                        <div style="color: {color}; font-family: JetBrains Mono;
                                    font-size: 1.4rem; font-weight: 700;">
                            {sim}%
                        </div>
                        <div style="color: #E4E8F1; font-size: 0.8rem;
                                    margin: 0.4rem 0; font-weight: 600;">
                            {event['name']}
                        </div>
                        <div style="color: #8B92B0; font-size: 0.7rem;">
                            {event['year']} — Severity {event['severity']}/10
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("### Projected portfolio returns under current regime")
            st.caption(
                "Similarity-weighted average of your portfolio across the "
                "five closest historical analogs to today."
            )

            fractions = portfolio_as_fractions()
            horizon_labels = [
                ("1m", "1M"), ("3m", "3M"),
                ("6m", "6M"), ("1y", "1Y"), ("2y", "2Y"),
            ]
            portfolio_returns: dict[str, float | None] = {h: None for h, _ in horizon_labels}

            for asset_id, fraction in fractions.items():
                pred = aggregate_impact_prediction(similar, asset_id)
                if not pred:
                    continue
                for horizon, _ in horizon_labels:
                    h_pred = pred.get(horizon)
                    if h_pred is None:
                        continue
                    current_val = portfolio_returns[horizon] or 0.0
                    portfolio_returns[horizon] = current_val + fraction * h_pred["expected"]

            metric_cols = st.columns(5)
            for i, (horizon, label) in enumerate(horizon_labels):
                value = portfolio_returns[horizon]
                with metric_cols[i]:
                    if value is not None:
                        delta_color = "normal" if value >= 0 else "inverse"
                        st.metric(
                            label=label,
                            value=f"{value:+.1f}%",
                            delta="Projected return",
                            delta_color=delta_color,
                        )
                    else:
                        st.metric(label=label, value="N/A")
    else:
        st.info(
            "Live FRED data is needed for regime analysis. "
            "Ensure your API key is configured and at least two macro "
            "indicators are available."
        )