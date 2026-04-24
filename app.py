import streamlit as st
from src.data_loader import load_events, get_categories
from src.styles import apply_custom_theme

st.set_page_config(
    page_title="MacroLens | Economic Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_theme()

# Hero Section
st.markdown("""
<div style="padding: 2rem 0 1rem 0;">
    <div class="hero-badge"> ECONOMIC INTELLIGENCE PLATFORM</div>
    <div class="hero-title">MacroLens</div>
    <div class="hero-subtitle">
        Institutional-grade market impact analysis powered by historical pattern matching,<br>
        economic theory, and quantitative modeling.
    </div>
</div>
""", unsafe_allow_html=True)

# Live Market Ticker
st.markdown("""
<div class="ticker-wrap">
    <div class="ticker">
        <span class="ticker-item"> S&P 500 <span class="value-positive">+0.82%</span></span>
        <span class="ticker-item"> NASDAQ <span class="value-positive">+1.24%</span></span>
        <span class="ticker-item"> OIL <span class="value-negative">-2.15%</span></span>
        <span class="ticker-item"> GOLD <span class="value-positive">+0.45%</span></span>
        <span class="ticker-item"> BTC <span class="value-positive">+3.72%</span></span>
        <span class="ticker-item"> DXY <span class="value-negative">-0.18%</span></span>
        <span class="ticker-item"> US10Y <span class="value-positive">+2bps</span></span>
        <span class="ticker-item"> VIX <span class="value-negative">-4.21%</span></span>
        <span class="ticker-item"> S&P 500 <span class="value-positive">+0.82%</span></span>
        <span class="ticker-item"> NASDAQ <span class="value-positive">+1.24%</span></span>
        <span class="ticker-item"> OIL <span class="value-negative">-2.15%</span></span>
        <span class="ticker-item"> GOLD <span class="value-positive">+0.45%</span></span>
        <span class="ticker-item"> BTC <span class="value-positive">+3.72%</span></span>
        <span class="ticker-item"> DXY <span class="value-negative">-0.18%</span></span>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")
st.write("")

# Stats Row
events = load_events()
categories = get_categories()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="glass-card" style="text-align: center;">
        <div class="stat-number">{}</div>
        <div class="stat-label">Historical Events</div>
    </div>
    """.format(len(events)), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card" style="text-align: center;">
        <div class="stat-number">{}</div>
        <div class="stat-label">Event Categories</div>
    </div>
    """.format(len(categories)), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="glass-card" style="text-align: center;">
        <div class="stat-number">14</div>
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

# Features Grid
st.markdown('<div class="section-label">CAPABILITIES</div>', unsafe_allow_html=True)
st.markdown("## Advanced Market Intelligence")

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">Event Explorer</div>
        <div class="feature-description">
            Deep-dive into major historical economic events with comprehensive impact 
            analysis across 14 asset classes and 5 time horizons. From 1973 Oil Crisis 
            to 2023 Banking Crisis.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📈</div>
        <div class="feature-title">Portfolio Stress Testing</div>
        <div class="feature-description">
            Simulate your portfolio's behavior under historical crisis scenarios. 
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
            Get probabilistic forecasts with confidence bands powered by similarity 
            matching algorithms.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">Theory Engine</div>
        <div class="feature-description">
            Understand the WHY behind market movements. Flight to quality, monetary 
            transmission, stagflation dynamics — economic frameworks explained.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# Methodology Section
st.markdown('<div class="section-label">🔬 METHODOLOGY</div>', unsafe_allow_html=True)
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

# CTA Section
st.markdown("""
<div class="glass-card" style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%); border: 1px solid rgba(0, 212, 255, 0.3);">
    <h2 style="border: none; padding: 0; margin: 0 0 1rem 0;">Ready to explore?</h2>
    <p style="color: #B8C0DC; font-size: 1.1rem; margin-bottom: 1.5rem;">
        Select a tool from the sidebar to begin your analysis →
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0;">
        <div style="font-size: 1.5rem; font-weight: 800; background: linear-gradient(135deg, #00D4FF 0%, #7C3AED 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ⚡ MacroLens
        </div>
        <div style="color: #8B92B0; font-size: 0.75rem; letter-spacing: 0.1em;">INTELLIGENCE PLATFORM</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("###  Navigation")
    st.caption("Select a tool above to begin")
    
    st.markdown("---")
    st.markdown("### Disclaimer")
    st.caption("For educational and research purposes only. Not financial advice.")
    
    st.markdown("---")
    st.markdown("### Data Sources")
    st.caption("Federal Reserve (FRED) • Yahoo Finance • Historical Archives")
