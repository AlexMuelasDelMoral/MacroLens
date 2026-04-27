import streamlit as st
from src.styles import apply_custom_theme

st.set_page_config(page_title="About", layout="wide")
apply_custom_theme()

# ============ HEADER ============
st.markdown('<div class="section-label">PROJECT</div>', unsafe_allow_html=True)
st.markdown("# About MacroLens")
st.markdown('<div class="hero-subtitle">Why this exists, what it does, who built it.</div>', unsafe_allow_html=True)

st.divider()

# ============ THESIS ============
st.markdown('<div class="section-label">THESIS</div>', unsafe_allow_html=True)
st.markdown("## The Idea")

st.markdown("""
<div class="glass-card">
<p style="color: #B8C0DC; font-size: 1.05rem; line-height: 1.7;">
Most retail investors and even many professionals lack a structured way to think about 
how their portfolios would behave during major economic shocks. Crisis events feel 
chaotic and unpredictable in the moment, but financial history shows clear patterns — 
similar macroeconomic configurations tend to produce similar market responses.
</p>
<p style="color: #B8C0DC; font-size: 1.05rem; line-height: 1.7; margin-top: 1rem;">
MacroLens makes those historical patterns accessible. Instead of asking "what will happen 
next?" — a question no one can reliably answer — it asks "when conditions like these 
existed before, what happened?" That reframing makes the analysis grounded, defensible, 
and actually useful.
</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ============ WHAT IT DOES ============
st.markdown('<div class="section-label">CAPABILITIES</div>', unsafe_allow_html=True)
st.markdown("## What MacroLens Does")

capabilities = [
    {
        "title": "HISTORICAL ANALYSIS",
        "body": "Examine 30 major economic events spanning 50 years. See how 45 asset classes "
                "performed at five time horizons during each event."
    },
    {
        "title": "SCENARIO MATCHING",
        "body": "Input current or hypothetical macro conditions. The system finds the most "
                "similar historical precedents and aggregates their outcomes."
    },
    {
        "title": "PORTFOLIO STRESS TESTING",
        "body": "Build a portfolio across 45 asset classes. Run it through historical crisis "
                "scenarios to identify drawdown vulnerabilities."
    },
    {
        "title": "LIVE MACRO MONITORING",
        "body": "Real-time data from the Federal Reserve. Yield curve status, recession "
                "probability signals, and current-vs-historical positioning."
    },
    {
        "title": "TRANSPARENT METHODOLOGY",
        "body": "Every prediction is labeled with its data source — real Yahoo Finance data, "
                "manually curated, or rule-based estimate. No black boxes."
    },
    {
        "title": "ECONOMIC THEORY OVERLAY",
        "body": "Quantitative output is contextualized with theoretical frameworks: "
                "flight-to-quality, monetary transmission, stagflation dynamics."
    },
]

cols = st.columns(2, gap="medium")
for i, cap in enumerate(capabilities):
    with cols[i % 2]:
        st.markdown(f"""
        <div class="feature-card">
            <div style="color: #00D4FF; font-family: 'JetBrains Mono'; font-size: 0.75rem; 
                        font-weight: 700; letter-spacing: 0.15em;">
                {cap['title']}
            </div>
            <div style="color: #B8C0DC; font-size: 0.9rem; line-height: 1.6; margin-top: 0.75rem;">
                {cap['body']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")

st.divider()

# ============ AUTHOR ============
st.markdown('<div class="section-label">AUTHOR</div>', unsafe_allow_html=True)
st.markdown("## Built By")

st.markdown("""
<div class="glass-card">
    <div style="display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 300px;">
            <div style="color: #E4E8F1; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.25rem;">
                ALEX MUELAS DEL MORAL
            </div>
            <div style="color: #00D4FF; font-family: 'JetBrains Mono'; font-size: 0.85rem; 
                        letter-spacing: 0.1em; margin-bottom: 1rem;">
                BUILDER · ANALYST · DEVELOPER
            </div>
            <p style="color: #B8C0DC; line-height: 1.7;">
                I built MacroLens to combine my interests in financial markets, economics
                and portfolio management into a single tool I would actually use. 
                It started as a personal project to understand how my own portfolio would 
                fare during different crisis scenarios, and grew into a platform that 
                others can use for the same purpose.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# Contact links
st.markdown("### Connect")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="glass-card" style="text-align: center;">
        <div style="color: #8B92B0; font-family: 'JetBrains Mono'; font-size: 0.7rem; 
                    letter-spacing: 0.15em; margin-bottom: 0.5rem;">GITHUB</div>
        <a href="https://github.com/alexmuelasdelmoral" target="_blank" 
           style="color: #00D4FF; text-decoration: none; font-family: 'JetBrains Mono';">
            github.com/AlexMuelasDelMoral
        </a>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="glass-card" style="text-align: center;">
        <div style="color: #8B92B0; font-family: 'JetBrains Mono'; font-size: 0.7rem; 
                    letter-spacing: 0.15em; margin-bottom: 0.5rem;">LINKEDIN</div>
        <a href="https://linkedin.com/in/alexmuelasdelmoral" target="_blank" 
           style="color: #00D4FF; text-decoration: none; font-family: 'JetBrains Mono';">
            Alex Muelas Del Moral
        </a>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="glass-card" style="text-align: center;">
        <div style="color: #8B92B0; font-family: 'JetBrains Mono'; font-size: 0.7rem; 
                    letter-spacing: 0.15em; margin-bottom: 0.5rem;">EMAIL</div>
        <a href="mailto:alex.muelas6@gmail.com" 
           style="color: #00D4FF; text-decoration: none; font-family: 'JetBrains Mono';">
            alex.muelas6@gmail.com
        </a>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============ SKILLS DEMONSTRATED ============
st.markdown('<div class="section-label">TECHNICAL SCOPE</div>', unsafe_allow_html=True)
st.markdown("## Skills Demonstrated")

skills = {
    "Quantitative Finance": [
        "Multi-asset portfolio analysis",
        "Cross-asset correlation dynamics",
        "Crisis regime identification",
        "Risk metrics (drawdown, dispersion)",
        "Macroeconomic indicator interpretation",
    ],
    "Data Engineering": [
        "API integration (Yahoo Finance, FRED)",
        "Time-series data processing",
        "Multi-source data reconciliation",
        "Quality tracking and provenance",
        "Reproducible data pipelines",
    ],
    "Software Engineering": [
        "Modular Python architecture",
        "Streamlit application development",
        "Custom CSS theme design",
        "PDF report generation",
        "Version control and CI/CD",
    ],
    "Machine Learning": [
        "Similarity-based retrieval",
        "Gradient boosting (XGBoost)",
        "Feature engineering",
        "Probabilistic forecasting",
        "Uncertainty quantification",
    ],
}

cols = st.columns(2, gap="medium")
for i, (category, items) in enumerate(skills.items()):
    with cols[i % 2]:
        items_html = "".join([
            f'<li style="color: #B8C0DC; padding: 0.3rem 0;">{item}</li>'
            for item in items
        ])
        st.markdown(f"""
        <div class="glass-card">
            <div style="color: #00D4FF; font-family: 'JetBrains Mono'; font-size: 0.75rem; 
                        font-weight: 700; letter-spacing: 0.15em; margin-bottom: 0.75rem;">
                {category.upper()}
            </div>
            <ul style="list-style: none; padding-left: 0; font-size: 0.9rem; line-height: 1.5;">
                {items_html}
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.write("")

st.divider()

# ============ TIMELINE ============
st.markdown('<div class="section-label">DEVELOPMENT</div>', unsafe_allow_html=True)
st.markdown("## Project Timeline")

timeline = [
    ("V0.1", "Initial Concept", "Designed event taxonomy and similarity matching algorithm"),
    ("V0.5", "MVP Launch", "First working version with 15 events and 8 asset classes"),
    ("V0.8", "Real Data Integration", "Replaced rule-based estimates with Yahoo Finance historical data"),
    ("V1.0", "Production Release", "30 events, 45 asset classes, professional UI, published methodology"),
    ("V1.x", "In Progress", "Backtesting mode, risk analytics dashboard, scenario comparison"),
]

st.markdown('<div class="glass-card" style="padding: 1.5rem 2rem;">', unsafe_allow_html=True)
for version, milestone, body in timeline:
    is_current = version == "V1.x"
    color = "#FFB547" if is_current else "#00D4FF"
    st.markdown(f"""
    <div style="display: flex; gap: 1.5rem; padding: 1rem 0; 
                border-bottom: 1px solid rgba(30, 42, 63, 0.5);">
        <div style="min-width: 80px; color: {color}; font-family: 'JetBrains Mono'; 
                    font-weight: 700; font-size: 0.95rem;">
            {version}
        </div>
        <div style="flex: 1;">
            <div style="color: #E4E8F1; font-weight: 600; margin-bottom: 0.25rem;">
                {milestone}
            </div>
            <div style="color: #8B92B0; font-size: 0.85rem; line-height: 1.5;">
                {body}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ============ ROADMAP ============
st.markdown('<div class="section-label">ROADMAP</div>', unsafe_allow_html=True)
st.markdown("## What's Next")

roadmap = [
    {
        "title": "BACKTESTING MODE",
        "status": "IN PROGRESS",
        "body": "Run the analysis as if it were any historical date. Compare predictions "
                "against what actually happened. Track accuracy over time."
    },
    {
        "title": "RISK ANALYTICS DASHBOARD",
        "status": "PLANNED",
        "body": "Value at Risk, Conditional VaR, Sharpe and Sortino ratios, maximum "
                "drawdown analysis. Institutional-grade portfolio analytics."
    },
    {
        "title": "SCENARIO COMPARISON",
        "status": "PLANNED",
        "body": "Side-by-side comparison of multiple scenarios. Visualize how different "
                "events would impact the same portfolio."
    },
    {
        "title": "MONTE CARLO SIMULATION",
        "status": "PLANNED",
        "body": "Generate thousands of scenario paths to produce full probability "
                "distributions instead of point estimates."
    },
    {
        "title": "NATURAL LANGUAGE INPUT",
        "status": "EXPLORING",
        "body": "Parse questions like 'What if the Fed cuts 50bps with inflation at 4%?' "
                "into structured scenario inputs."
    },
]

for item in roadmap:
    status_color = {
        "IN PROGRESS": "#FFB547",
        "PLANNED": "#00D4FF",
        "EXPLORING": "#7C3AED",
    }.get(item["status"], "#8B92B0")
    
    st.markdown(f"""
    <div class="feature-card">
        <div style="display: flex; justify-content: space-between; align-items: start; 
                    margin-bottom: 0.75rem;">
            <div style="color: #E4E8F1; font-weight: 700; font-size: 1rem;">
                {item['title']}
            </div>
            <div style="color: {status_color}; font-family: 'JetBrains Mono'; font-size: 0.7rem; 
                        font-weight: 700; letter-spacing: 0.15em; padding: 0.2rem 0.6rem; 
                        border: 1px solid {status_color}; border-radius: 2px;">
                {item['status']}
            </div>
        </div>
        <div style="color: #B8C0DC; font-size: 0.9rem; line-height: 1.6;">
            {item['body']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

st.divider()

# ============ ACKNOWLEDGEMENTS ============
st.markdown('<div class="section-label">CREDITS</div>', unsafe_allow_html=True)
st.markdown("## Acknowledgements")

st.markdown("""
<div class="glass-card">
    <div style="color: #B8C0DC; line-height: 1.8;">
        <p>This project would not be possible without the open-source community and 
        the institutions that make financial data publicly available:</p>
        <ul style="color: #8B92B0; font-size: 0.9rem;">
            <li><strong style="color: #E4E8F1;">Yahoo Finance</strong> — Historical price data across all asset classes</li>
            <li><strong style="color: #E4E8F1;">Federal Reserve Bank of St. Louis (FRED)</strong> — Macroeconomic indicators</li>
            <li><strong style="color: #E4E8F1;">Streamlit</strong> — Application framework</li>
            <li><strong style="color: #E4E8F1;">Plotly</strong> — Interactive visualizations</li>
            <li><strong style="color: #E4E8F1;">yfinance, scikit-learn, XGBoost, ReportLab</strong> — Python ecosystem</li>
        </ul>
        <p style="margin-top: 1rem;">Influences and intellectual debts to the work of 
        Ray Dalio (economic machine framework), Howard Marks (memos on cycles), 
        Reinhart and Rogoff (crisis analysis), and Nassim Taleb (uncertainty 
        quantification).</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ============ FOOTER ============
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0;">
    <div style="color: #4A5572; font-family: 'JetBrains Mono'; font-size: 0.75rem; 
                letter-spacing: 0.15em;">
        MACROLENS · ECONOMIC INTELLIGENCE PLATFORM
    </div>
    <div style="color: #4A5572; font-family: 'JetBrains Mono'; font-size: 0.7rem; 
                letter-spacing: 0.1em; margin-top: 0.5rem;">
        OPEN SOURCE · MIT LICENSE
    </div>
</div>
""", unsafe_allow_html=True)