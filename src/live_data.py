"""Live macro data fetching from FRED API."""
import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fredapi import Fred

# Series IDs for key indicators
FRED_SERIES = {
    "inflation_cpi": "CPIAUCSL",        # CPI
    "fed_funds_rate": "DFF",             # Federal Funds Rate
    "unemployment": "UNRATE",            # Unemployment Rate
    "gdp_growth": "A191RL1Q225SBEA",    # Real GDP % change
    "us_10y_yield": "DGS10",             # 10Y Treasury
    "us_2y_yield": "DGS2",               # 2Y Treasury
    "vix": "VIXCLS",                     # VIX
    "yield_curve": "T10Y2Y",             # 10Y-2Y spread
    "dxy": "DTWEXBGS",                   # Dollar Index
}

def get_fred_client():
    """Initialize FRED API client. Store key in .streamlit/secrets.toml"""
    try:
        api_key = st.secrets.get("FRED_API_KEY") or os.getenv("FRED_API_KEY")
        if not api_key:
            return None
        return Fred(api_key=api_key)
    except Exception:
        return None


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_latest_indicator(series_id):
    """Fetch latest value of a FRED series."""
    fred = get_fred_client()
    if not fred:
        return None
    try:
        data = fred.get_series(series_id, 
                                observation_start=datetime.now() - timedelta(days=90))
        if data.empty:
            return None
        return {
            "value": float(data.iloc[-1]),
            "date": data.index[-1].strftime("%Y-%m-%d"),
            "previous": float(data.iloc[-2]) if len(data) > 1 else None
        }
    except Exception as e:
        return None


@st.cache_data(ttl=3600)
def fetch_historical_series(series_id, years=5):
    """Fetch historical time series."""
    fred = get_fred_client()
    if not fred:
        return None
    try:
        data = fred.get_series(
            series_id,
            observation_start=datetime.now() - timedelta(days=365*years)
        )
        return data
    except Exception:
        return None


def get_current_macro_snapshot():
    """Get current macro conditions for scenario builder."""
    snapshot = {}
    
    # CPI - calculate YoY inflation
    cpi_data = fetch_historical_series("CPIAUCSL", years=2)
    if cpi_data is not None and len(cpi_data) >= 13:
        current = cpi_data.iloc[-1]
        year_ago = cpi_data.iloc[-13]
        snapshot["inflation"] = round(((current - year_ago) / year_ago) * 100, 2)
    
    # Fed Funds Rate
    ffr = fetch_latest_indicator("DFF")
    if ffr:
        snapshot["fed_funds_rate"] = round(ffr["value"], 2)
    
    # Unemployment
    unemp = fetch_latest_indicator("UNRATE")
    if unemp:
        snapshot["unemployment"] = round(unemp["value"], 2)
    
    # 10Y Yield
    ten_y = fetch_latest_indicator("DGS10")
    if ten_y:
        snapshot["us_10y_yield"] = round(ten_y["value"], 2)
    
    # VIX
    vix = fetch_latest_indicator("VIXCLS")
    if vix:
        snapshot["vix"] = round(vix["value"], 2)
    
    # Yield curve
    yc = fetch_latest_indicator("T10Y2Y")
    if yc:
        snapshot["yield_curve"] = round(yc["value"], 2)
    
    return snapshot


def get_recession_probability():
    """Simple recession probability based on yield curve."""
    yc = fetch_latest_indicator("T10Y2Y")
    if not yc:
        return None
    
    spread = yc["value"]
    # Historical rule: inverted curve = ~70% recession within 18 months
    if spread < -0.5:
        return 85
    elif spread < 0:
        return 70
    elif spread < 0.5:
        return 40
    elif spread < 1:
        return 20
    else:
        return 10