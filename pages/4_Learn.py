import streamlit as st
from src.styles import apply_custom_theme
from src.theory_engine import THEORIES

st.set_page_config(page_title="Learn", layout="wide")
apply_custom_theme()

st.markdown('<div class="section-label"> EDUCATION</div>', unsafe_allow_html=True)
st.markdown("# Economic Theory Library")
st.caption("Understanding the frameworks that explain market behavior")

st.divider()

# Theory sections
for theory_id, theory in THEORIES.items():
    with st.expander(f"{theory['name']}", expanded=False):
        st.markdown(f"### {theory['description']}")
        st.write("")
        st.markdown("**Market Implications:**")
        
        for asset, implication in theory['implications'].items():
            st.markdown(f"""
            <div class="glass-card" style="padding: 1rem; margin-bottom: 0.5rem;">
                <div style="color: #00D4FF; font-weight: 700; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.1em;">
                    {asset.replace('_', ' ')}
                </div>
                <div style="color: #E4E8F1; margin-top: 0.25rem;">
                    {implication}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# Key concepts
st.markdown("## Key Concepts")

concepts = [
    {
        "title": "Duration Risk",
        "description": "The sensitivity of bond prices to interest rate changes. Long-duration assets (long bonds, tech stocks) are most affected by rate movements."
    },
    {
        "title": "Liquidity Crisis",
        "description": "When market participants can't easily buy/sell assets without large price impacts. Often triggers forced selling and correlations spike to 1."
    },
    {
        "title": "Real vs Nominal Rates",
        "description": "Real rate = nominal rate - inflation. Gold thrives when real rates are negative. Bonds suffer when real rates rise."
    },
    {
        "title": "Yield Curve",
        "description": "Graph of interest rates across maturities. Inversion (short > long) has preceded every US recession since 1950."
    },
    {
        "title": "Central Bank Policy",
        "description": "Monetary policy transmission works through rates, asset prices, and credit channels. Fed 'put' has conditioned markets to expect intervention."
    },
    {
        "title": "Dollar Smile",
        "description": "USD strengthens in extreme risk-off (safe haven) AND in strong US growth (divergence). Weakens in 'goldilocks' middle scenarios."
    }
]

cols = st.columns(2)
for i, concept in enumerate(concepts):
    with cols[i % 2]:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-title">{concept['title']}</div>
            <div class="feature-description">{concept['description']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")

st.divider()

# Recommended reading
st.markdown("## Recommended Reading")

books = [
    ("**This Time Is Different**", "Reinhart & Rogoff", "Eight centuries of financial folly"),
    ("**Principles for Navigating Big Debt Crises**", "Ray Dalio", "Template for debt cycles"),
    ("**Manias, Panics, and Crashes**", "Charles Kindleberger", "History of financial crises"),
    ("**The Intelligent Investor**", "Benjamin Graham", "Foundational value investing"),
    ("**Fooled by Randomness**", "Nassim Taleb", "Role of chance in markets"),
    ("**When Genius Failed**", "Roger Lowenstein", "LTCM collapse story"),
]

for book, author, desc in books:
    st.markdown(f"""
    <div class="glass-card" style="padding: 1rem;">
        <div style="color: #E4E8F1;">{book} <span style="color: #8B92B0;">by {author}</span></div>
        <div style="color: #8B92B0; font-size: 0.9rem; margin-top: 0.25rem;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)