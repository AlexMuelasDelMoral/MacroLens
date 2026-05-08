import streamlit as st
from src.data_loader import load_events, get_categories
from src.styles import apply_custom_theme
from src.navbar import render_navbar

st.set_page_config(
    page_title="MacroLens | Economic Intelligence Platform",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_custom_theme()
render_navbar()

st.markdown("""
<div style="padding: 1rem 0 1rem 0;">
    <div class="hero-badge">ECONOMIC INTELLIGENCE PLATFORM</div>
    <div class="hero-title">MacroLens</div>
    <div class="hero-subtitle">
        Institutional-grade market impact analysis powered by historical pattern matching,<br>
        economic theory, and quantitative modeling.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ticker-wrap">
    <div class="ticker">
        <span class="ticker-item">S&P 500 <span class="value-positive">+0.82%</span></span>
        <span class="ticker-item">NASDAQ <span class="value-positive">+1.24%</span></span>
        <span class="ticker-item">OIL <span class="value-negative">-2.15%</span></span>
        <span class="ticker-item">GOLD <span class="value-positive">+0.45%</span></span>
        <span class="ticker-item">BTC <span class="value-positive">+3.72%</span></span>
        <span class="ticker-item">DXY <span class="value-negative">-0.18%</span></span>
        <span class="ticker-item">US10Y <span class="value-positive">+2bps</span></span>
        <span class="ticker-item">VIX <span class="value-negative">-4.21%</span></span>
        <span class="ticker-item">S&P 500 <span class="value-positive">+0.82%</span></span>
        <span class="ticker-item">NASDAQ <span class="value-positive">+1.24%</span></span>
        <span class="ticker-item">OIL <span class="value-negative">-2.15%</span></span>
        <span class="ticker-item">GOLD <span class="value-positive">+0.45%</span></span>
        <span class="ticker-item">BTC <span class="value-positive">+3.72%</span></span>
        <span class="ticker-item">DXY <span class="value-negative">-0.18%</span></span>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

events = load_events()
categories = get_categories()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <div class="stat-number">{len(events)}</div>
        <div class="stat-label">Historical Events</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <div class="stat-number">{len(categories)}</div>
        <div class="stat-label">Event Categories</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="glass-card" style="text-align: center;">
        <div class="stat-number">45</div>
        <div class="stat-label">Asset Classes</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
    <div class="glass-card" style="text-align: center;">
        <div class="stat-number">50+</div>
        <div class="stat-label">Years of Data</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown('<div class="section-label">CAPABILITIES</div>', unsafe_allow_html=True)
st.markdown("## Advanced Market Intelligence")

col1, col2 = st.columns(2, gap="medium")
with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">Event Explorer</div>
        <div class="feature-description">
            Deep-dive into major historical economic events with comprehensive impact
            analysis across 45 asset classes and 5 time horizons.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">Portfolio Stress Testing</div>
        <div class="feature-description">
            Simulate your portfolio under historical crisis scenarios.
            Identify vulnerabilities and optimize allocations for tail risk protection.
        </div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">Scenario Builder</div>
        <div class="feature-description">
            Input custom macro conditions and discover similar historical precedents.
            Get probabilistic forecasts with confidence bands.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">Monte Carlo Simulation</div>
        <div class="feature-description">
            Sample 10,000 return paths from historical analog distributions.
            Surface VaR, CVaR, and full percentile breakdowns per asset.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown('<div class="section-label">METHODOLOGY</div>', unsafe_allow_html=True)
st.markdown("## How It Works")

col1, col2, col3 = st.columns(3, gap="medium")
with col1:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: #00D4FF;">01. Data Layer</h3>
        <p style="color: #8B92B0;">
            Curated database of major economic events with pre-event macro conditions
            and asset performance across multiple time horizons.
        </p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: #00D4FF;">02. Matching Engine</h3>
        <p style="color: #8B92B0;">
            Weighted Euclidean distance algorithm finds the most similar historical
            precedents based on macroeconomic indicators.
        </p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: #00D4FF;">03. Theory Overlay</h3>
        <p style="color: #8B92B0;">
            Economic frameworks provide qualitative context and explain the
            mechanisms behind predicted market responses.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown("""
<div class="glass-card" style="text-align: center; padding: 3rem 2rem;
    background: linear-gradient(135deg, rgba(0,212,255,0.1) 0%, rgba(124,58,237,0.1) 100%);
    border: 1px solid rgba(0,212,255,0.3);">
    <h2 style="border: none; padding: 0; margin: 0 0 1rem 0;">Ready to explore?</h2>
    <p style="color: #B8C0DC; font-size: 1.1rem; margin-bottom: 0;">
        Select a tool from the navigation bar above to begin your analysis.
    </p>
</div>
""", unsafe_allow_html=True)
