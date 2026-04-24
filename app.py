import streamlit as st
from src.data_loader import load_events, get_categories

st.set_page_config(
    page_title="MacroLens - Economic Event Market Predictor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f9fafb;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">📊 MacroLens</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Predict market impacts of major economic events using historical data & economic theory</p>', unsafe_allow_html=True)

# Stats row
events = load_events()
categories = get_categories()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Historical Events", len(events))
col2.metric("Event Categories", len(categories))
col3.metric("Asset Classes", 14)
col4.metric("Time Horizons", 5)

st.divider()

# Introduction
st.header("🎯 What is MacroLens?")
st.markdown("""
MacroLens analyzes how major economic events historically impacted financial markets, 
and uses pattern matching to predict how current or hypothetical scenarios might play out. 

**Key Features:**
- 📊 **Event Explorer**: Deep dive into historical economic events
- 🔮 **Scenario Builder**: Input custom macro conditions to find similar historical precedents
- 📈 **Portfolio Stress Test**: See how your portfolio might fare under different scenarios
- 📚 **Learn**: Economic theory explanations behind market movements
""")

st.divider()

# Feature cards
st.header("🚀 Start Exploring")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Event Explorer</h3>
        <p>Browse historical economic events and see their impacts on different asset classes across multiple time horizons.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h3>📈 Portfolio Stress Test</h3>
        <p>Enter your portfolio allocation and see projected impacts under different crisis scenarios.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>🔮 Scenario Builder</h3>
        <p>Set current macro conditions (inflation, rates, etc.) and get probabilistic predictions based on similar historical precedents.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h3>📚 Learn</h3>
        <p>Understand the economic theories and frameworks that explain why markets respond the way they do.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Methodology
with st.expander("🔬 Methodology & Limitations"):
    st.markdown("""
    ### How It Works
    1. **Historical Database**: Curated database of major economic events with pre-event macro conditions
    2. **Similarity Matching**: Weighted Euclidean distance on key macro variables (inflation, rates, unemployment, GDP)
    3. **Impact Aggregation**: Similarity-weighted average of historical returns with uncertainty bands
    4. **Theory Overlay**: Economic frameworks provide qualitative context
    
    ### Limitations
    - **Past ≠ Future**: Historical patterns may not repeat; regimes change
    - **Limited Data**: Some events (crypto during 2008) have no precedent
    - **Black Swans**: Truly unprecedented events by definition aren't in the database
    - **Policy Response**: Modern central banks may react differently than historical counterparts
    - **Survivorship Bias**: Database focuses on major events, may miss minor ones
    
    ### Disclaimer
    ⚠️ **This tool is for educational and research purposes only. Not financial advice.**
    Always consult qualified financial advisors before making investment decisions.
    """)

st.sidebar.success("👆 Select a tool from above")
st.sidebar.info("Built with ❤️ using Streamlit, Python, and economic data.")
