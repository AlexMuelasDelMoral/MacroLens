import streamlit as st
from src.theory_engine import THEORIES

from src.styles import apply_custom_theme
apply_custom_theme()

st.set_page_config(page_title="Learn", page_icon="📚", layout="wide")

st.title("Learn: Economic Theory & Market Behavior")
st.markdown("Understand the frameworks that explain how markets respond to economic events.")

st.divider()

# Theories section
st.header("Core Economic Frameworks")

tabs = st.tabs([theory["name"] for theory in THEORIES.values()])

for tab, (theory_id, theory) in zip(tabs, THEORIES.items()):
    with tab:
        st.subheader(theory["name"])
        st.markdown(f"**{theory['description']}**")
        
        st.markdown("### Key Implications by Asset Class")
        for asset, implication in theory["implications"].items():
            st.markdown(f"#### {asset.replace('_', ' ').title()}")
            st.info(implication)

st.divider()

# Additional educational content
st.header("📖 Essential Concepts")

with st.expander("Understanding Central Bank Policy"):
    st.markdown("""
    ### The Fed's Tools
    - **Federal Funds Rate**: Primary short-term interest rate tool
    - **Quantitative Easing (QE)**: Buying bonds to inject liquidity
    - **Quantitative Tightening (QT)**: Selling bonds to reduce balance sheet
    - **Forward Guidance**: Communicating future policy intentions
    
    ### The Taylor Rule
    A formula to estimate appropriate interest rates:
    
    `Rate = Neutral Rate + 0.5*(Inflation - Target) + 0.5*(Output Gap)`
    
    ### Transmission Mechanism
    1. Fed changes rates
    2. Short-term rates adjust immediately
    3. Long-term rates reflect expectations + term premium
    4. Credit conditions tighten/loosen
    5. Asset prices reprice
    6. Real economy responds (6-18 month lag)
    """)

with st.expander("The Yield Curve: A Crystal Ball?"):
    st.markdown("""
    ### What Is It?
    The yield curve plots interest rates across different maturities (e.g., 2Y vs 10Y Treasuries).
    
    ### Shapes and Meaning
    - **Normal (upward sloping)**: Healthy economy, growth expected
    - **Flat**: Uncertainty, transition phase
    - **Inverted (downward sloping)**: Recession signal - short rates > long rates
    
    ### Historical Record
    Every US recession since 1960 was preceded by yield curve inversion (usually 6-24 months lead time).
    
    ### Why It Works
    - Short rates driven by Fed policy (often hiking to fight inflation)
    - Long rates reflect growth expectations (declining = recession fears)
    - Inversion = markets expect Fed to cut rates (because of weak economy)
    """)

with st.expander("Asset Class Correlations in Crises"):
    st.markdown("""
    ### Normal Regime Correlations
    - Stocks & Bonds: Negative (-0.3 to -0.5)
    - Gold & Stocks: Low (~0)
    - USD & Stocks: Varies by regime
    
    ### Crisis Regime: Correlations Go to 1
    During severe stress, investors sell everything for cash:
    - Stocks crash
    - Even "safe" assets initially sell off (liquidity crisis)
    - True diversifiers: USD, long-duration Treasuries, sometimes gold
    
    ### The Exception: 2022
    Stocks AND bonds fell together due to inflation shock + Fed hikes - breaking traditional 60/40 logic.
    
    ### Implication for Portfolio Construction
    - Don't rely on historical correlations during crises
    - True tail hedges: put options, volatility, cash
    - Consider regime-shifting: what hedges one crisis type fails in another
    """)

with st.expander("Stagflation: The Worst Scenario"):
    st.markdown("""
    ### Definition
    High inflation + Low/negative growth + High unemployment
    
    ### Why It's Toxic
    - Central banks face dilemma: fight inflation = hurt growth; support growth = worsen inflation
    - Stocks hit by both multiple contraction AND earnings pressure
    - Bonds hit by both rate hikes AND credit deterioration
    - Classic "nowhere to hide" environment
    
    ### Historical Examples
    - 1970s US (Oil shocks + loose policy legacy)
    - 2022-2023 near-miss (COVID stimulus + supply shocks + Ukraine war)
    
    ### What Works
    - Gold & precious metals
    - Commodities (if supply-driven)
    - Value > Growth stocks
    - Short duration bonds
    - Real assets (real estate, infrastructure)
    - Companies with pricing power
    """)

with st.expander("Safe Haven Assets Explained"):
    st.markdown("""
    ### The Classic Safe Havens
    
    **1. US Treasuries**
    - Backed by world's largest economy
    - Deepest, most liquid market
    - Risk: Interest rate risk if inflation rises
    
    **2. Gold**
    - 5000 years of monetary history
    - No counterparty risk
    - Inflation hedge + crisis hedge
    - Risk: No yield, storage costs
    
    **3. USD (Dollar Index)**
    - World reserve currency
    - Strengthens in global risk-off (dollar funding needs)
    - Risk: Long-term debasement concerns
    
    **4. Swiss Franc & Japanese Yen**
    - Traditional FX safe havens
    - Current account surplus countries
    - Risk: Intervention, policy changes
    
    ### New Candidates (Debated)
    - Bitcoin ("digital gold" thesis, limited history)
    - Chinese RMB (not yet, capital controls)
    """)

st.divider()

# Recommended reading
st.header("Recommended Reading")

books = [
    {
        "title": "This Time Is Different",
        "author": "Reinhart & Rogoff",
        "description": "Eight centuries of financial folly - essential crisis history."
    },
    {
        "title": "Principles for Navigating Big Debt Crises",
        "author": "Ray Dalio",
        "description": "Framework for understanding debt cycles - free PDF online."
    },
    {
        "title": "Manias, Panics, and Crashes",
        "author": "Charles Kindleberger",
        "description": "Classic taxonomy of financial crises."
    },
    {
        "title": "The Alchemy of Finance",
        "author": "George Soros",
        "description": "Reflexivity and market dynamics from a master."
    },
    {
        "title": "When Genius Failed",
        "author": "Roger Lowenstein",
        "description": "LTCM collapse - lessons on leverage and correlation."
    },
    {
        "title": "Lords of Finance",
        "author": "Liaquat Ahamed",
        "description": "Central banking decisions that caused the Great Depression."
    }
]

for book in books:
    st.markdown(f"**{book['title']}** by *{book['author']}*")
    st.caption(book["description"])
    st.markdown("---")
