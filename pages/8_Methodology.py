import streamlit as st
from src.styles import apply_custom_theme, render_page_header
from src.navbar import render_navbar
from src.data_loader import load_events, get_asset_classes, calculate_quality_score, get_data_last_updated

st.set_page_config(page_title="Methodology", layout="wide")
apply_custom_theme()
render_navbar()

# ============ HEADER ============
render_page_header(
    label="DOCUMENTATION",
    title="Methodology",
    subtitle="How MacroLens generates predictions, and the limitations you should know",
)
st.markdown('<div class="hero-subtitle">How MacroLens generates predictions, and the limitations you should know.</div>', unsafe_allow_html=True)

st.divider()

# ============ EXECUTIVE OVERVIEW ============
st.markdown('<div class="section-label">OVERVIEW</div>', unsafe_allow_html=True)
st.markdown("## System Architecture")

st.markdown("""
<div class="glass-card">
MacroLens is built on three layers that work together to produce defensible market 
forecasts under economic stress scenarios. Unlike a pure machine learning system, 
it deliberately combines hard data, statistical inference, and economic theory — 
each layer compensates for the limitations of the others.
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown("""
    <div class="feature-card">
        <div style="color: #00D4FF; font-family: 'JetBrains Mono'; font-size: 0.75rem; 
                    font-weight: 700; letter-spacing: 0.15em;">LAYER 01</div>
        <div class="feature-title" style="margin-top: 0.5rem;">DATA FOUNDATION</div>
        <div class="feature-description">
            Historical price data fetched directly from Yahoo Finance for every 
            event-asset combination. Calculated returns at 1M, 3M, 6M, 1Y, and 2Y 
            horizons from event start. Coverage decreases for older events as 
            many instruments did not exist.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div style="color: #00D4FF; font-family: 'JetBrains Mono'; font-size: 0.75rem; 
                    font-weight: 700; letter-spacing: 0.15em;">LAYER 02</div>
        <div class="feature-title" style="margin-top: 0.5rem;">PATTERN MATCHING</div>
        <div class="feature-description">
            Weighted Euclidean distance algorithm identifies historical analogs 
            based on macroeconomic state vectors. Similarity scores drive 
            probability-weighted aggregation of historical outcomes into 
            forward-looking forecasts.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div style="color: #00D4FF; font-family: 'JetBrains Mono'; font-size: 0.75rem; 
                    font-weight: 700; letter-spacing: 0.15em;">LAYER 03</div>
        <div class="feature-title" style="margin-top: 0.5rem;">THEORY OVERLAY</div>
        <div class="feature-description">
            Economic frameworks contextualize quantitative output. Flight-to-quality, 
            monetary policy transmission, stagflation dynamics, and risk-on/risk-off 
            regimes provide qualitative interpretation alongside numerical forecasts.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============ DATA SOURCES ============
st.markdown('<div class="section-label">DATA SOURCES</div>', unsafe_allow_html=True)
st.markdown("## Where the Numbers Come From")

events = load_events()
assets = get_asset_classes()

# Calculate global quality
total_real = total_curated = total_estimated = total_missing = 0
for e in events:
    q = calculate_quality_score(e["id"])
    total_real += q.get("real", 0)
    total_curated += q.get("curated", 0)
    total_estimated += q.get("estimated", 0)
    total_missing += q.get("missing", 0)

total_cells = total_real + total_curated + total_estimated + total_missing

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Data Points", f"{total_cells:,}")
col2.metric("From Yahoo Finance", f"{total_real:,}",
            f"{total_real/total_cells*100:.1f}%")
col3.metric("Manually Curated", f"{total_curated:,}",
            f"{total_curated/total_cells*100:.1f}%")
col4.metric("Rule-Based Estimate", f"{total_estimated:,}",
            f"{total_estimated/total_cells*100:.1f}%")

timestamps = get_data_last_updated()
if timestamps:
    st.markdown("### Data freshness")
    ts_cols = st.columns(len(timestamps))
    for i, (label, timestamp) in enumerate(timestamps.items()):
        with ts_cols[i]:
            st.markdown(f"""
            <div style="background: rgba(0, 212, 255, 0.05); border: 0.5px solid rgba(0, 212, 255, 0.2);
                        border-radius: 8px; padding: 0.75rem 1rem;">
                <div style="color: #8B92B0; font-size: 0.7rem; letter-spacing: 0.08em;
                            font-family: JetBrains Mono; margin-bottom: 0.3rem;">
                    {label.upper()}
                </div>
                <div style="color: #00D4FF; font-size: 0.8rem; font-family: JetBrains Mono;">
                    {timestamp}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.write("")

with st.expander("Yahoo Finance Historical Data — How It's Fetched", expanded=False):
    st.markdown("""
    For each event, the system fetches daily closing prices for the corresponding 
    Yahoo Finance ticker spanning from the event start date through 800 days forward.
    Returns are calculated as percentage changes between the close on the first 
    available trading day at or after the event start, and the close at the target 
    horizon date.
    
    **Yield indices** (10Y Treasury, 2Y Treasury, VIX) report absolute changes in 
    points rather than percentage changes, since the underlying values are already 
    quoted in percentage terms.
    
    **Fallback tickers** are used when the primary ETF did not exist for older events. 
    For example, US 10Y Treasury exposure uses the IEF ETF (inception 2002) but 
    falls back to the ^TNX yield index (data from 1962) for events like the 1973 
    Oil Crisis or 1987 Black Monday.
    """)

with st.expander("Manual Curated Data — When and Why", expanded=False):
    st.markdown("""
    Certain data points are manually curated from authoritative historical sources 
    when Yahoo Finance data is incomplete or known to be inaccurate. These overrides 
    take precedence over both fetched and generated data.
    
    Curated data is sourced from:
    - Federal Reserve Economic Data (FRED)
    - Academic research papers on financial crises
    - Official central bank publications
    - Bloomberg historical archives where accessible
    """)

with st.expander("Rule-Based Estimation — The Fallback Layer", expanded=False):
    st.markdown("""
    When neither fetched nor curated data exists (typically because the asset 
    did not exist during the event period), a rule-based estimator generates 
    a plausible value using:
    
    - **Event archetype**: Each event category has a baseline impact pattern
    - **Asset characteristics**: Beta, rate sensitivity, inflation sensitivity, crisis beta
    - **Severity scaling**: Linear scaling based on the event's severity rating (1-10)
    - **Time decay**: Asset-type-specific recovery patterns over the time horizon
    
    Estimates are clearly marked in the UI with quality indicators. They should 
    be treated as illustrative rather than predictive.
    """)

st.divider()

# ============ SIMILARITY ALGORITHM ============
st.markdown('<div class="section-label">ALGORITHM</div>', unsafe_allow_html=True)
st.markdown("## Pattern Matching")

st.markdown("""
<div class="glass-card">
The core forecasting engine uses weighted Euclidean distance across normalized 
macroeconomic indicators to identify the historical events most similar to a 
user's input scenario. Similar events contribute to the forecast in proportion 
to their similarity score.
</div>
""", unsafe_allow_html=True)

st.markdown("### Distance Calculation")
st.code("""
distance = sqrt(
    sum(
        weight[i] * ((user_value[i] - event_value[i]) / range[i])^2
        for i in [inflation, fed_rate, unemployment, gdp_growth]
    ) / sum(weights)
)

similarity = max(0, 100 * (1 - distance))
""", language="python")

st.markdown("### Aggregation")
st.code("""
predicted_return = (
    sum(similarity[i] * historical_return[i] for i in similar_events)
    / sum(similarity[i] for i in similar_events)
)

uncertainty_band = (min(historical_returns), max(historical_returns))
""", language="python")

st.markdown("""
The aggregation is **similarity-weighted** rather than averaged equally. An event 
with 90% similarity contributes nine times more to the forecast than one with 10% 
similarity. The reported uncertainty band reflects the actual range of historical 
outcomes among matched events.
""")

st.divider()

# ============ ASSUMPTIONS ============
st.markdown('<div class="section-label">ASSUMPTIONS</div>', unsafe_allow_html=True)
st.markdown("## What This System Assumes")

st.markdown("""
<div class="glass-card">

**1. Historical Patterns Have Predictive Value**

The fundamental assumption is that markets respond to similar macroeconomic 
configurations in similar ways. This is empirically supported but has clear 
limits — see "Limitations" below.

**2. Macro State Captures Sufficient Context**

The four macro variables used (inflation, Fed funds rate, unemployment, GDP growth) 
are assumed to capture the most relevant context. In reality, factors like 
sentiment, positioning, valuations, and policy credibility also matter.

**3. Asset Behavior is Approximately Stable**

The risk-off behavior of US Treasuries, gold's role as a safe haven, and 
similar relationships are assumed to persist. Regime changes (e.g., Bitcoin 
becoming more correlated with risk assets) can break these assumptions.

**4. Severity Scales Linearly**

Event severity (1-10) is assumed to scale impact magnitude linearly. This is a 
simplification — real crises often exhibit non-linear behavior, where mild 
stress is absorbed but extreme stress triggers cascading failures.

</div>
""", unsafe_allow_html=True)

st.divider()

# ============ LIMITATIONS ============
st.markdown('<div class="section-label">LIMITATIONS</div>', unsafe_allow_html=True)
st.markdown("## Known Limitations")

limitations = [
    {
        "title": "Survivorship Bias",
        "body": "The historical event database focuses on major events that left clear footprints. "
                "Smaller crises that resolved quickly may be underrepresented, biasing the dataset "
                "toward severe outcomes."
    },
    {
        "title": "Black Swan Blindness",
        "body": "Truly unprecedented events have no historical analog. The system will find the 'least dissimilar' "
                "events but may produce false confidence. The Russia-Ukraine war, COVID-19 lockdowns, "
                "and the 2023 banking crisis all had unique characteristics not fully captured by macro variables."
    },
    {
        "title": "Regime Change Risk",
        "body": "The relationship between macro variables and market behavior is not constant. The post-2008 "
                "QE era behaved differently than the pre-2008 period. Predictions during regime transitions "
                "are particularly unreliable."
    },
    {
        "title": "Limited Sample Size",
        "body": "With 30 events spanning 50 years, the database has a small statistical sample. "
                "Confidence intervals from such samples are wide and should not be interpreted as precise."
    },
    {
        "title": "Policy Response Variability",
        "body": "Modern central banks intervene more aggressively than historical counterparts. The same macro "
                "shock today may be met with rate cuts, QE, or fiscal stimulus that wasn't available before. "
                "This breaks direct historical comparisons."
    },
    {
        "title": "Data Coverage Gaps",
        "body": "Pre-2000 events have significantly less real data because many modern instruments did not exist. "
                "Forecasts for those events lean more heavily on rule-based estimates."
    },
    {
        "title": "No Real-Time Adjustment",
        "body": "The system does not incorporate real-time positioning, sentiment, or options market signals. "
                "These can dominate short-term price action in ways pure macro analysis misses."
    }
]

for lim in limitations:
    st.markdown(f"""
    <div class="glass-card" style="border-left: 3px solid #FF3B6B;">
        <div style="color: #FF3B6B; font-family: 'JetBrains Mono'; font-size: 0.75rem; 
                    font-weight: 700; letter-spacing: 0.1em; margin-bottom: 0.5rem;">
            LIMITATION
        </div>
        <div style="color: #E4E8F1; font-weight: 700; font-size: 1rem; margin-bottom: 0.5rem;">
            {lim['title']}
        </div>
        <div style="color: #B8C0DC; font-size: 0.9rem; line-height: 1.6;">
            {lim['body']}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============ APPROPRIATE USE ============
st.markdown('<div class="section-label">USAGE GUIDANCE</div>', unsafe_allow_html=True)
st.markdown("## How to Use These Forecasts")

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("""
    <div class="glass-card" style="border-left: 3px solid #00F5A0;">
        <div style="color: #00F5A0; font-family: 'JetBrains Mono'; font-size: 0.75rem; 
                    font-weight: 700; letter-spacing: 0.1em;">APPROPRIATE USES</div>
        <ul style="color: #B8C0DC; font-size: 0.9rem; line-height: 1.8; margin-top: 0.5rem;">
            <li>Stress-testing portfolio allocations against historical scenarios</li>
            <li>Identifying which assets historically benefited from specific shocks</li>
            <li>Generating hypotheses for further research</li>
            <li>Educational exploration of crisis dynamics</li>
            <li>Framing risk discussions with historical context</li>
            <li>Identifying overlooked diversifiers in your portfolio</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card" style="border-left: 3px solid #FF3B6B;">
        <div style="color: #FF3B6B; font-family: 'JetBrains Mono'; font-size: 0.75rem; 
                    font-weight: 700; letter-spacing: 0.1em;">INAPPROPRIATE USES</div>
        <ul style="color: #B8C0DC; font-size: 0.9rem; line-height: 1.8; margin-top: 0.5rem;">
            <li>Precise return predictions for specific holdings</li>
            <li>Sole basis for investment decisions</li>
            <li>Short-term tactical trading signals</li>
            <li>Replacement for proper risk management</li>
            <li>Estimating tail risk in unprecedented scenarios</li>
            <li>Forecasting individual stocks or specific securities</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============ MODEL VALIDATION ============
st.markdown('<div class="section-label">MODEL VALIDATION</div>', unsafe_allow_html=True)
st.markdown("## Cross-validation results")
st.markdown("""
<div class="glass-card">
Out-of-sample performance metrics for the gradient boosting ML engine.
Computed using five-fold cross-validation on the historical event database,
with folds preserving temporal order. These numbers reflect how well the
model generalizes to events it has not seen during training.
</div>
""", unsafe_allow_html=True)

cv_horizon = st.select_slider(
    "Horizon for cross-validation analysis",
    options=["1m", "3m", "6m", "1y", "2y"],
    value="3m",
    key="cv_horizon_slider",
)

with st.spinner("Running cross-validation..."):
    try:
        from src.ml_engine import run_cross_validation_suite
        from src.data_loader import ASSET_LABELS
        cv_results = run_cross_validation_suite(
            assets=["sp500", "gold", "us_10y_treasury", "bitcoin", "oil_wti"],
            horizon=cv_horizon,
        )

        if not cv_results:
            st.warning("Insufficient data to run cross-validation.")
        else:
            col1, col2, col3 = st.columns(3)
            avg_mae = sum(r["mae"] for r in cv_results) / len(cv_results)
            avg_dir = sum(r["direction_accuracy"] for r in cv_results) / len(cv_results)
            avg_rmse = sum(r["rmse"] for r in cv_results) / len(cv_results)
            col1.metric(
                "Average MAE",
                f"{avg_mae:.2f}%",
                "Mean absolute error across assets",
            )
            col2.metric(
                "Direction accuracy",
                f"{avg_dir:.1f}%",
                "Correct sign prediction rate",
            )
            col3.metric(
                "Average RMSE",
                f"{avg_rmse:.2f}%",
                "Root mean squared error",
            )

            st.markdown("### Per-asset breakdown")
            st.caption(
                "Lower MAE and higher direction accuracy indicate better "
                "generalization. Bitcoin's lower sample count (n=14 vs n=30) "
                "makes its metrics less reliable."
            )

            import plotly.graph_objects as go
            from src.styles import get_plotly_layout

            asset_names = [
                ASSET_LABELS.get(r["asset_class"], r["asset_class"])
                for r in cv_results
            ]
            mae_values = [r["mae"] for r in cv_results]
            dir_values = [r["direction_accuracy"] for r in cv_results]
            n_values = [r["n_samples"] for r in cv_results]

            fig_cv = go.Figure()
            fig_cv.add_trace(go.Bar(
                name="MAE (%)",
                x=asset_names,
                y=mae_values,
                marker=dict(
                    color="#FF3B6B",
                    opacity=0.85,
                    line=dict(color="rgba(255,255,255,0.1)", width=1),
                ),
                text=[f"{v:.2f}%" for v in mae_values],
                textposition="outside",
                textfont=dict(
                    color="#E4E8F1", size=12, family="JetBrains Mono"
                ),
                yaxis="y",
            ))
            fig_cv.add_trace(go.Scatter(
                name="Direction accuracy (%)",
                x=asset_names,
                y=dir_values,
                mode="lines+markers",
                marker=dict(
                    size=12,
                    color="#00D4FF",
                    line=dict(color="#FFFFFF", width=2),
                ),
                line=dict(color="#00D4FF", width=2),
                text=[f"{v:.1f}%" for v in dir_values],
                textposition="top center",
                textfont=dict(
                    color="#00D4FF", size=11, family="JetBrains Mono"
                ),
                yaxis="y2",
            ))

            layout_cv = get_plotly_layout(
                title=dict(
                    text=(
                        f"<b>ML engine cross-validation — {cv_horizon.upper()} horizon</b>"
                        f"<br><span style='font-size:11px;color:#8B92B0'>"
                        f"Red bars: mean absolute error (lower is better). "
                        f"Blue line: direction accuracy (higher is better).</span>"
                    ),
                    font=dict(size=15, color="#E4E8F1"),
                ),
                height=420,
                yaxis=dict(
                    title="MAE (%)",
                    gridcolor="rgba(42,49,88,0.3)",
                    tickfont=dict(color="#8B92B0"),
                ),
                yaxis2=dict(
                    title="Direction accuracy (%)",
                    overlaying="y",
                    side="right",
                    range=[0, 110],
                    gridcolor="rgba(0,0,0,0)",
                    tickfont=dict(color="#00D4FF"),
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5,
                ),
                margin=dict(l=40, r=60, t=100, b=60),
                barmode="group",
            )
            fig_cv.update_layout(layout_cv)
            st.plotly_chart(fig_cv, width='stretch')

            with st.expander("Fold-by-fold prediction details"):
                st.caption(
                    "Each row shows one held-out event, the model prediction, "
                    "and the actual historical return. Sorted by error descending "
                    "so the hardest-to-predict events appear first."
                )
                for result in cv_results:
                    asset_label = ASSET_LABELS.get(
                        result["asset_class"], result["asset_class"]
                    )
                    st.markdown(f"**{asset_label}** — "
                                f"MAE {result['mae']:.2f}% | "
                                f"Direction accuracy {result['direction_accuracy']:.1f}% | "
                                f"n={result['n_samples']}")
                    details_sorted = sorted(
                        result["fold_details"],
                        key=lambda x: -x["error"],
                    )
                    st.dataframe(
                        details_sorted,
                        width='stretch',
                        hide_index=True,
                        height=200,
                    )

        st.markdown("""
        <div class="glass-card" style="border-left: 3px solid #FFB547; margin-top: 1rem;">
            <div style="color: #FFB547; font-family: JetBrains Mono; font-size: 0.7rem;
                        font-weight: 700; letter-spacing: 0.1em; margin-bottom: 0.5rem;">
                INTERPRETING THESE NUMBERS
            </div>
            <div style="color: #B8C0DC; font-size: 0.9rem; line-height: 1.6;">
                A MAE of 10% means the model's predictions were off by an average of
                10 percentage points on held-out events. Given that crisis returns can
                range from -60% to +60%, this represents meaningful but imperfect signal.
                Direction accuracy above 60% indicates the model correctly predicts
                whether an asset rises or falls more often than a coin flip.
                These metrics should be interpreted alongside the similarity engine
                results, not in isolation.
            </div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"Cross-validation unavailable: {e}")

st.divider()

# ============ TECHNICAL STACK ============
st.markdown('<div class="section-label">TECHNICAL DETAILS</div>', unsafe_allow_html=True)
st.markdown("## Implementation")

stack = [
    ("Frontend", "Streamlit", "Python web framework for analytical applications"),
    ("Visualization", "Plotly", "Interactive charts with custom dark theme"),
    ("Data Source", "Yahoo Finance via yfinance", "Historical price data"),
    ("Live Data", "FRED API", "Real-time macroeconomic indicators"),
    ("Pattern Matching", "scikit-learn / NumPy", "Weighted Euclidean distance"),
    ("Machine Learning", "XGBoost", "Gradient boosting for asset prediction"),
    ("Reports", "ReportLab", "PDF generation for analyses"),
    ("Hosting", "Streamlit Community Cloud", "Continuous deployment from GitHub"),
]

st.markdown("""
<div class="glass-card">
<table class="data-table" style="width: 100%;">
<thead>
<tr>
    <th style="width: 25%;">Component</th>
    <th style="width: 25%;">Technology</th>
    <th>Purpose</th>
</tr>
</thead>
<tbody>
""", unsafe_allow_html=True)

for component, tech, purpose in stack:
    st.markdown(f"""
    <tr>
        <td style="color: #8B92B0;">{component}</td>
        <td style="color: #00D4FF; font-family: 'JetBrains Mono';">{tech}</td>
        <td style="color: #B8C0DC;">{purpose}</td>
    </tr>
    """, unsafe_allow_html=True)

st.markdown("</tbody></table></div>", unsafe_allow_html=True)

st.divider()

# ============ DISCLAIMER ============
st.markdown("""
<div class="glass-card" style="border-left: 3px solid #FFB547; margin-top: 2rem;">
    <div style="color: #FFB547; font-family: 'JetBrains Mono'; font-size: 0.75rem; 
                font-weight: 700; letter-spacing: 0.15em; margin-bottom: 0.75rem;">
        IMPORTANT DISCLAIMER
    </div>
    <div style="color: #B8C0DC; line-height: 1.7;">
        MacroLens is an educational and research tool. It does not constitute financial advice, 
        investment recommendation, or solicitation to buy or sell securities. Past performance 
        does not guarantee future results. The author and contributors assume no responsibility 
        for any financial decisions made based on this analysis. Always consult qualified 
        financial professionals before making investment decisions.
    </div>
</div>
""", unsafe_allow_html=True)