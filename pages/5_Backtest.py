import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date

from src.styles import apply_custom_theme, get_plotly_layout
from src.data_loader import ASSET_CATEGORIES, ASSET_LABELS
from src.historical_macro import get_historical_macro, FAMOUS_MOMENTS
from src.backtest_engine import run_backtest, calculate_asset_accuracy

st.set_page_config(page_title="Backtest", layout="wide")
apply_custom_theme()

# ============ HEADER ============
st.markdown('<div class="section-label">VALIDATION</div>', unsafe_allow_html=True)
st.markdown("# Backtest Mode")
st.markdown('<div class="hero-subtitle">Run MacroLens at any historical date. Compare predictions to what actually happened.</div>', unsafe_allow_html=True)

st.divider()

# ============ DATE SELECTION ============
st.markdown('<div class="section-label">SELECT TIMEPOINT</div>', unsafe_allow_html=True)
st.markdown("## Choose a Historical Moment")

col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.markdown("### Famous Moments")
    moment_options = ["Custom Date"] + [m["label"] for m in FAMOUS_MOMENTS]
    selected_moment = st.selectbox(
        "Select a preset",
        options=moment_options,
        help="Pre-selected moments where we know what happened next"
    )

with col2:
    st.markdown("### Or Pick Any Date")
    if selected_moment == "Custom Date":
        target_date = st.date_input(
            "Date",
            value=date(2020, 2, 19),
            min_value=date(1990, 1, 1),
            max_value=date(2023, 1, 1),
            help="Need at least 2 years after this date for actual return data"
        )
        target_date_str = target_date.strftime("%Y-%m-%d")
        moment_context = None
        moment_outcome = None
    else:
        moment = next(m for m in FAMOUS_MOMENTS if m["label"] == selected_moment)
        target_date_str = moment["date"]
        moment_context = moment["context"]
        moment_outcome = moment["what_happened"]
        st.markdown(f"""
        <div class="glass-card" style="padding: 1rem; margin-top: 0.25rem;">
            <div style="color: #00D4FF; font-family: 'JetBrains Mono'; font-size: 0.85rem;">
                {target_date_str}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Show context if preset selected
if moment_context:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="border-left: 3px solid #00D4FF;">
            <div style="color: #00D4FF; font-family: 'JetBrains Mono'; font-size: 0.7rem; 
                        font-weight: 700; letter-spacing: 0.15em; margin-bottom: 0.5rem;">
                CONTEXT AT TIME
            </div>
            <div style="color: #B8C0DC; line-height: 1.6;">
                {moment_context}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="border-left: 3px solid #FFB547;">
            <div style="color: #FFB547; font-family: 'JetBrains Mono'; font-size: 0.7rem; 
                        font-weight: 700; letter-spacing: 0.15em; margin-bottom: 0.5rem;">
                WHAT ACTUALLY HAPPENED
            </div>
            <div style="color: #B8C0DC; line-height: 1.6;">
                {moment_outcome}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ============ FETCH HISTORICAL MACRO ============
st.markdown('<div class="section-label">MACRO CONDITIONS</div>', unsafe_allow_html=True)
st.markdown(f"## Conditions on {target_date_str}")

with st.spinner("Loading historical macro data..."):
    macro = get_historical_macro(target_date_str)

if not macro:
    st.error("Could not fetch macro data for this date. Try a different date or configure FRED API key.")
    st.stop()

source = macro.pop("_source", "Unknown")
days_off = macro.pop("_days_off", None)

# Display macro conditions
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Inflation", f"{macro.get('inflation', 'N/A')}%" if macro.get('inflation') else "N/A")
with col2:
    st.metric("Fed Funds Rate", f"{macro.get('fed_funds_rate', 'N/A')}%" if macro.get('fed_funds_rate') else "N/A")
with col3:
    st.metric("Unemployment", f"{macro.get('unemployment', 'N/A')}%" if macro.get('unemployment') else "N/A")
with col4:
    st.metric("GDP Growth", f"{macro.get('gdp_growth', 'N/A')}%" if macro.get('gdp_growth') else "N/A")

st.markdown(f"""
<div style="padding: 0.6rem 1rem; background: rgba(10, 22, 40, 0.6); 
            border-left: 3px solid #00D4FF; border-radius: 4px; margin: 1rem 0;
            font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #8B92B0;">
    DATA SOURCE: {source}
    {f' (closest event was {days_off} days away)' if days_off else ''}
</div>
""", unsafe_allow_html=True)

# Allow user to override
with st.expander("Adjust macro conditions manually", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        macro["inflation"] = st.number_input("Inflation %", value=float(macro.get("inflation", 3.0)), step=0.1)
    with col2:
        macro["fed_funds_rate"] = st.number_input("Fed Rate %", value=float(macro.get("fed_funds_rate", 2.0)), step=0.25)
    with col3:
        macro["unemployment"] = st.number_input("Unemployment %", value=float(macro.get("unemployment", 5.0)), step=0.1)
    with col4:
        macro["gdp_growth"] = st.number_input("GDP Growth %", value=float(macro.get("gdp_growth", 2.0)), step=0.1)

st.divider()

# ============ ASSET SELECTION ============
st.markdown('<div class="section-label">ASSETS TO BACKTEST</div>', unsafe_allow_html=True)
st.markdown("## Select Asset Classes")

default_assets = ["sp500", "nasdaq", "us_10y_treasury", "gold", "oil_wti", "tech", "vix"]

selected_assets = st.multiselect(
    "Choose assets (more = slower)",
    options=list(ASSET_LABELS.keys()),
    default=default_assets,
    format_func=lambda x: ASSET_LABELS.get(x, x)
)

if not selected_assets:
    st.warning("Select at least one asset to backtest.")
    st.stop()

st.divider()

# ============ RUN BACKTEST ============
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    run = st.button("RUN BACKTEST", use_container_width=True, type="primary")

if run:
    user_conditions = {
        "inflation": macro.get("inflation"),
        "fed_funds_rate": macro.get("fed_funds_rate"),
        "unemployment": macro.get("unemployment"),
        "gdp_growth": macro.get("gdp_growth"),
    }

    with st.spinner(f"Running backtest for {target_date_str}... fetching actual returns..."):
        results = run_backtest(
            user_conditions,
            target_date_str,
            selected_assets,
            top_n=5,
        )

    if not results:
        st.error("Backtest failed. Try a different date.")
        st.stop()

    st.session_state["backtest_results"] = results

if "backtest_results" not in st.session_state:
    st.info("Click RUN BACKTEST to see how predictions compare to actual outcomes.")
    st.stop()

results = st.session_state["backtest_results"]

# ============ DISPLAY RESULTS ============
st.divider()
st.markdown('<div class="section-label">RESULTS</div>', unsafe_allow_html=True)
st.markdown("## Prediction vs Reality")

# Top-level metrics
metrics = results["metrics"]

col1, col2, col3, col4 = st.columns(4)

with col1:
    acc = metrics.get("direction_accuracy") or 0
    color = "#00F5A0" if acc >= 60 else ("#FFB547" if acc >= 45 else "#FF3B6B")
    st.markdown(f"""
    <div class="glass-card" style="text-align: center; border-left: 3px solid {color};">
        <div class="stat-label">DIRECTION ACCURACY</div>
        <div style="font-family: 'JetBrains Mono'; font-size: 2.5rem; font-weight: 700; 
                    color: {color}; margin: 0.5rem 0;">
            {acc}%
        </div>
        <div style="color: #8B92B0; font-size: 0.75rem; font-family: 'JetBrains Mono';">
            {metrics.get('n_direction_correct', 0)} / {metrics.get('n_direction_total', 0)} correct
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    mae = metrics.get("mean_absolute_error") or 0
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <div class="stat-label">MEAN ABS ERROR</div>
        <div style="font-family: 'JetBrains Mono'; font-size: 2.5rem; font-weight: 700; 
                    color: #00D4FF; margin: 0.5rem 0;">
            {mae}%
        </div>
        <div style="color: #8B92B0; font-size: 0.75rem; font-family: 'JetBrains Mono';">
            avg miss size
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    median_e = metrics.get("median_absolute_error") or 0
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <div class="stat-label">MEDIAN ABS ERROR</div>
        <div style="font-family: 'JetBrains Mono'; font-size: 2.5rem; font-weight: 700; 
                    color: #00D4FF; margin: 0.5rem 0;">
            {median_e}%
        </div>
        <div style="color: #8B92B0; font-size: 0.75rem; font-family: 'JetBrains Mono';">
            typical miss size
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    n_pred = metrics.get("n_predictions") or 0
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <div class="stat-label">PREDICTIONS</div>
        <div style="font-family: 'JetBrains Mono'; font-size: 2.5rem; font-weight: 700; 
                    color: #E4E8F1; margin: 0.5rem 0;">
            {n_pred}
        </div>
        <div style="color: #8B92B0; font-size: 0.75rem; font-family: 'JetBrains Mono';">
            comparable points
        </div>
    </div>
    """, unsafe_allow_html=True)

# Historical analogs used
st.markdown("### Events Used for Prediction")
st.caption(f"Using only events from before {target_date_str}")

analog_data = []
for item in results["similar_events"]:
    analog_data.append({
        "Event": f"{item['event']['name']} ({item['event']['year']})",
        "Category": item["event"]["category"],
        "Similarity": f"{item['similarity']}%"
    })

st.dataframe(pd.DataFrame(analog_data), use_container_width=True, hide_index=True)

st.divider()

# ============ ASSET-LEVEL RESULTS ============
st.markdown("## Asset-Level Comparison")

# Asset selector
selected_asset = st.selectbox(
    "Drill down into specific asset",
    options=selected_assets,
    format_func=lambda x: ASSET_LABELS.get(x, x)
)

asset_data = results["assets"][selected_asset]
acc = calculate_asset_accuracy(asset_data)

# Asset metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Direction Accuracy", 
              f"{acc['direction_pct']}%" if acc['direction_pct'] is not None else "N/A")
with col2:
    st.metric("Mean Absolute Error",
              f"{acc['mae']}%" if acc['mae'] is not None else "N/A")
with col3:
    st.metric("Comparable Horizons", f"{acc['n_horizons']}/5")

# Side by side bar chart
horizons = ["1m", "3m", "6m", "1y", "2y"]
horizon_labels = ["1M", "3M", "6M", "1Y", "2Y"]

predicted = [asset_data["predicted"].get(h) for h in horizons]
actual = [asset_data["actual"].get(h) for h in horizons]

fig = go.Figure()
fig.add_trace(go.Bar(
    name="Predicted",
    x=horizon_labels,
    y=predicted,
    marker_color="#00D4FF",
    text=[f"{v:+.1f}%" if v is not None else "N/A" for v in predicted],
    textposition="outside",
    textfont=dict(family="JetBrains Mono", size=11),
))
fig.add_trace(go.Bar(
    name="Actual",
    x=horizon_labels,
    y=actual,
    marker_color="#FFB547",
    text=[f"{v:+.1f}%" if v is not None else "N/A" for v in actual],
    textposition="outside",
    textfont=dict(family="JetBrains Mono", size=11),
))

fig.add_hline(y=0, line_dash="dash", line_color="rgba(139, 146, 176, 0.5)")

layout = get_plotly_layout(
    title=dict(
        text=f"<b>{ASSET_LABELS[selected_asset].upper()} — PREDICTED vs ACTUAL</b>",
        font=dict(size=14, color="#E4E8F1", family="JetBrains Mono"),
    ),
    barmode="group",
    height=450,
    yaxis_title="Return (%)",
    xaxis_title="Time Horizon",
)
fig.update_layout(layout)
st.plotly_chart(fig, use_container_width=True)

# Detailed breakdown table
st.markdown("### Detailed Breakdown")

breakdown = []
for h, label in zip(horizons, horizon_labels):
    pred = asset_data["predicted"].get(h)
    act = asset_data["actual"].get(h)
    err = asset_data["error"].get(h)
    direction = asset_data["direction_correct"].get(h)

    breakdown.append({
        "Horizon": label,
        "Predicted": f"{pred:+.2f}%" if pred is not None else "—",
        "Actual": f"{act:+.2f}%" if act is not None else "—",
        "Error": f"{err:+.2f}%" if err is not None else "—",
        "Direction": "Correct" if direction else ("Wrong" if direction is False else "—"),
    })

df = pd.DataFrame(breakdown)
st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()

# ============ FULL ASSET HEATMAP ============
st.markdown("## All Assets — Error Heatmap")
st.caption("Negative error = prediction was too pessimistic. Positive error = prediction was too optimistic.")

errors_data = []
asset_names = []
for asset_id in selected_assets:
    asset = results["assets"][asset_id]
    row = []
    for h in horizons:
        e = asset["error"].get(h)
        row.append(e)
    errors_data.append(row)
    asset_names.append(ASSET_LABELS[asset_id])

fig = go.Figure(data=go.Heatmap(
    z=errors_data,
    x=horizon_labels,
    y=asset_names,
    colorscale=[
        [0, "#FF3B6B"],
        [0.5, "#0A1628"],
        [1, "#00F5A0"],
    ],
    zmid=0,
    text=[[f"{v:+.1f}" if v is not None else "—" for v in row] for row in errors_data],
    texttemplate="%{text}",
    textfont={"size": 10, "family": "JetBrains Mono", "color": "#E4E8F1"},
    colorbar=dict(
        title=dict(text="Error %", font=dict(color="#E4E8F1")),
        tickfont=dict(color="#8B92B0"),
    ),
))

layout = get_plotly_layout(
    title=dict(
        text="<b>PREDICTION ERRORS BY ASSET AND HORIZON</b>",
        font=dict(size=14, color="#E4E8F1", family="JetBrains Mono"),
    ),
    height=max(400, len(asset_names) * 40),
    margin=dict(l=160, r=40, t=80, b=40),
)
fig.update_layout(layout)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============ INTERPRETATION ============
st.markdown('<div class="section-label">INTERPRETATION</div>', unsafe_allow_html=True)
st.markdown("## What This Tells Us")

acc_pct = metrics.get("direction_accuracy", 0) or 0

if acc_pct >= 70:
    interpretation_color = "#00F5A0"
    interpretation_label = "STRONG PERFORMANCE"
    interpretation_text = (
        "The model correctly identified market direction in most cases. "
        "Historical pattern matching captured the dominant macro forces driving prices."
    )
elif acc_pct >= 55:
    interpretation_color = "#FFB547"
    interpretation_label = "MODERATE PERFORMANCE"
    interpretation_text = (
        "The model performed better than coin flip but missed important nuances. "
        "Likely explanations: regime change, unprecedented policy response, or unique event characteristics."
    )
else:
    interpretation_color = "#FF3B6B"
    interpretation_label = "WEAK PERFORMANCE"
    interpretation_text = (
        "The model struggled at this date. This often happens at major regime transitions, "
        "true black swan events, or when policy responses dramatically changed the typical playbook. "
        "This is honest signal — pattern matching has limits."
    )

st.markdown(f"""
<div class="glass-card" style="border-left: 3px solid {interpretation_color};">
    <div style="color: {interpretation_color}; font-family: 'JetBrains Mono'; font-size: 0.75rem; 
                font-weight: 700; letter-spacing: 0.15em; margin-bottom: 0.75rem;">
        {interpretation_label}
    </div>
    <div style="color: #B8C0DC; line-height: 1.7; font-size: 0.95rem;">
        {interpretation_text}
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="glass-card" style="margin-top: 1rem;">
    <div style="color: #8B92B0; font-size: 0.85rem; line-height: 1.7;">
        <strong style="color: #E4E8F1;">Why backtests matter.</strong> Any predictive system should 
        be tested against history. Strong forward-looking claims without backtest evidence are 
        marketing, not analysis. By exposing the model's track record, MacroLens lets you decide 
        for yourself how much weight to give its predictions.
    </div>
</div>
""", unsafe_allow_html=True)