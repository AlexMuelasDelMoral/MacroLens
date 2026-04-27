import streamlit as st
from src.styles import apply_custom_theme
from src.data_loader import load_events, get_asset_classes, calculate_quality_score

st.set_page_config(page_title="Methodology", layout="wide")
apply_custom_theme()

# ============ HEADER ============
st.markdown('<div class="section-label">DOCUMENTATION</div>', unsafe_allow_html=True)
st.markdown("# Methodology")
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