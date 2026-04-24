"""Central styling module for MacroLens Pro."""

CUSTOM_CSS = """
<style>
    /* Import Premium Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Root Variables */
    :root {
        --primary: #00D4FF;
        --primary-glow: #00D4FF44;
        --primary-dim: #0099CC;
        --bg-primary: #0A0E27;
        --bg-secondary: #131836;
        --bg-tertiary: #1A2046;
        --bg-card: #151A3A;
        --border: #2A3158;
        --text-primary: #E4E8F1;
        --text-secondary: #8B92B0;
        --text-dim: #5A6182;
        --positive: #00F5A0;
        --negative: #FF3B6B;
        --warning: #FFB547;
        --gradient-primary: linear-gradient(135deg, #00D4FF 0%, #0066FF 100%);
        --gradient-glow: linear-gradient(135deg, #00D4FF 0%, #7C3AED 100%);
    }
    
    /* Global Overrides */
    .stApp {
        background: radial-gradient(ellipse at top, #131836 0%, #0A0E27 50%, #050817 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main Container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }
    
    /* Headers with Neon Effect */
    h1 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        font-size: 2.5rem !important;
        background: linear-gradient(135deg, #00D4FF 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-weight: 700 !important;
        color: #E4E8F1 !important;
        letter-spacing: -0.01em;
        border-left: 4px solid #00D4FF;
        padding-left: 1rem;
        margin-top: 2rem !important;
    }
    
    h3 {
        font-weight: 600 !important;
        color: #B8C0DC !important;
    }
    
    /* Lightning Blue Title */
    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00D4FF 0%, #0066FF 50%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.04em;
        line-height: 1;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 60px rgba(0, 212, 255, 0.3);
    }
    
    .hero-subtitle {
        color: #8B92B0;
        font-size: 1.25rem;
        font-weight: 400;
        margin-bottom: 2rem;
        letter-spacing: 0.02em;
    }
    
    .hero-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 100px;
        color: #00D4FF;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    
    /* Metric Cards - Glass Morphism */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(21, 26, 58, 0.8) 0%, rgba(19, 24, 54, 0.4) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(42, 49, 88, 0.5);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00D4FF, transparent);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: rgba(0, 212, 255, 0.4);
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
        transform: translateY(-2px);
    }
    
    [data-testid="stMetric"]:hover::before {
        opacity: 1;
    }
    
    [data-testid="stMetricLabel"] {
        color: #8B92B0 !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    [data-testid="stMetricValue"] {
        color: #E4E8F1 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-weight: 600 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00D4FF 0%, #0066FF 100%);
        color: #0A0E27 !important;
        font-weight: 700;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-size: 0.95rem;
        letter-spacing: 0.02em;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
        transition: all 0.3s ease;
        text-transform: uppercase;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 30px rgba(0, 212, 255, 0.5);
        transform: translateY(-2px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background: rgba(19, 24, 54, 0.6) !important;
        border: 1px solid rgba(42, 49, 88, 0.8) !important;
        color: #E4E8F1 !important;
        border-radius: 10px !important;
        font-family: 'JetBrains Mono', monospace !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #00D4FF !important;
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1) !important;
    }
    
    /* Sliders */
    .stSlider [data-baseweb="slider"] > div > div {
        background: linear-gradient(90deg, #00D4FF 0%, #0066FF 100%) !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(19, 24, 54, 0.6) !important;
        border: 1px solid rgba(42, 49, 88, 0.5) !important;
        border-radius: 10px !important;
        color: #E4E8F1 !important;
        font-weight: 600 !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(0, 212, 255, 0.4) !important;
        background: rgba(21, 26, 58, 0.8) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        gap: 0.5rem;
        border-bottom: 1px solid rgba(42, 49, 88, 0.5);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #8B92B0 !important;
        border-radius: 10px 10px 0 0 !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #00D4FF !important;
        background: rgba(0, 212, 255, 0.05) !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #00D4FF !important;
        background: rgba(0, 212, 255, 0.1) !important;
        border-bottom: 2px solid #00D4FF !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A0E27 0%, #050817 100%);
        border-right: 1px solid rgba(42, 49, 88, 0.3);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #B8C0DC;
    }
    
    /* DataFrames */
    .stDataFrame {
        border: 1px solid rgba(42, 49, 88, 0.5);
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Alerts */
    .stAlert {
        background: rgba(19, 24, 54, 0.6) !important;
        border-radius: 10px !important;
        border-left-width: 4px !important;
    }
    
    /* Info Alert */
    div[data-baseweb="notification"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 102, 255, 0.05) 100%);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 10px;
    }
    
    /* Custom Card Classes */
    .glass-card {
        background: linear-gradient(135deg, rgba(21, 26, 58, 0.6) 0%, rgba(19, 24, 54, 0.3) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(42, 49, 88, 0.5);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(0, 212, 255, 0.3);
        box-shadow: 0 8px 40px rgba(0, 212, 255, 0.08);
    }
    
    .feature-card {
        background: linear-gradient(135deg, rgba(21, 26, 58, 0.8) 0%, rgba(19, 24, 54, 0.4) 100%);
        border: 1px solid rgba(42, 49, 88, 0.5);
        border-radius: 16px;
        padding: 2rem;
        height: 100%;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s;
        pointer-events: none;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0, 212, 255, 0.4);
        box-shadow: 0 12px 40px rgba(0, 212, 255, 0.15);
    }
    
    .feature-card:hover::after {
        opacity: 1;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: inline-block;
        filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.5));
    }
    
    .feature-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #E4E8F1;
        margin-bottom: 0.75rem;
    }
    
    .feature-description {
        color: #8B92B0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* KPI Stats Row */
    .stat-number {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00D4FF 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        color: #8B92B0;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-top: 0.25rem;
    }
    
    /* Positive/Negative Values */
    .value-positive {
        color: #00F5A0;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
    }
    
    .value-negative {
        color: #FF3B6B;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
    }
    
    /* Divider */
    hr {
        border-color: rgba(42, 49, 88, 0.5) !important;
        margin: 2rem 0 !important;
    }
    
    /* Glow Effect Utility */
    .glow-text {
        color: #00D4FF;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
    }
    
    /* Ticker Tape Animation */
    @keyframes scroll {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    
    .ticker-wrap {
        background: rgba(10, 14, 39, 0.8);
        border-top: 1px solid rgba(0, 212, 255, 0.2);
        border-bottom: 1px solid rgba(0, 212, 255, 0.2);
        padding: 0.75rem 0;
        overflow: hidden;
        white-space: nowrap;
    }
    
    .ticker {
        display: inline-block;
        animation: scroll 60s linear infinite;
    }
    
    .ticker-item {
        display: inline-block;
        padding: 0 2rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        color: #B8C0DC;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #00D4FF 0%, #0066FF 100%) !important;
    }
    
    /* Section Label */
    .section-label {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 6px;
        color: #00D4FF;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    
    /* Code blocks */
    code {
        background: rgba(0, 212, 255, 0.1) !important;
        color: #00D4FF !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
</style>
"""

def apply_custom_theme():
    """Apply the custom theme to Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Plotly dark theme template
PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(10, 14, 39, 0.3)",
        "font": {
            "family": "Inter, sans-serif",
            "color": "#E4E8F1"
        },
        "colorway": ["#00D4FF", "#7C3AED", "#00F5A0", "#FFB547", "#FF3B6B", "#0066FF"],
        "xaxis": {
            "gridcolor": "rgba(42, 49, 88, 0.3)",
            "linecolor": "rgba(42, 49, 88, 0.5)",
            "tickfont": {"color": "#8B92B0"}
        },
        "yaxis": {
            "gridcolor": "rgba(42, 49, 88, 0.3)",
            "linecolor": "rgba(42, 49, 88, 0.5)",
            "tickfont": {"color": "#8B92B0"}
        },
        "legend": {
            "bgcolor": "rgba(19, 24, 54, 0.8)",
            "bordercolor": "rgba(42, 49, 88, 0.5)",
            "borderwidth": 1,
            "font": {"color": "#E4E8F1"}
        }
    }
}


def get_plotly_layout(**kwargs):
    """Get standardized Plotly layout with dark theme."""
    layout = dict(PLOTLY_TEMPLATE["layout"])
    layout.update(kwargs)
    return layout
