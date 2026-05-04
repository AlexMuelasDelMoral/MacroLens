"""Live macro data fetching from the FRED API.

fredapi is imported lazily inside get_fred_client() so it does not
contribute to cold-start time on pages that do not load live data,
or when no FRED API key is configured.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

FRED_SERIES: dict[str, str] = {
    "inflation_cpi": "CPIAUCSL",
    "fed_funds_rate": "DFF",
    "unemployment": "UNRATE",
    "gdp_growth": "A191RL1Q225SBEA",
    "us_10y_yield": "DGS10",
    "us_2y_yield": "DGS2",
    "vix": "VIXCLS",
    "yield_curve": "T10Y2Y",
    "dxy": "DTWEXBGS",
}


def get_fred_client():
    """Initialize and return a FRED API client.

    fredapi is imported here rather than at module level to avoid
    paying the import cost when FRED data is not needed.

    Returns None if no API key is configured or if the import fails.
    """
    try:
        from fredapi import Fred
        api_key = st.secrets.get("FRED_API_KEY") or os.getenv("FRED_API_KEY")
        if not api_key:
            return None
        return Fred(api_key=api_key)
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_latest_indicator(series_id: str) -> dict | None:
    """Fetch the latest value of a FRED series.

    Returns a dict with keys value, date, and previous, or None on failure.
    """
    fred = get_fred_client()
    if not fred:
        return None
    try:
        data = fred.get_series(
            series_id,
            observation_start=datetime.now() - timedelta(days=90),
        )
        if data.empty:
            return None
        return {
            "value": float(data.iloc[-1]),
            "date": data.index[-1].strftime("%Y-%m-%d"),
            "previous": float(data.iloc[-2]) if len(data) > 1 else None,
        }
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_historical_series(series_id: str, years: int = 5) -> pd.Series | None:
    """Fetch a historical time series from FRED."""
    fred = get_fred_client()
    if not fred:
        return None
    try:
        return fred.get_series(
            series_id,
            observation_start=datetime.now() - timedelta(days=365 * years),
        )
    except Exception:
        return None


def get_current_macro_snapshot() -> dict[str, float]:
    """Get current macro conditions for the scenario builder."""
    snapshot: dict[str, float] = {}

    cpi_data = fetch_historical_series("CPIAUCSL", years=2)
    if cpi_data is not None and len(cpi_data) >= 13:
        current = cpi_data.iloc[-1]
        year_ago = cpi_data.iloc[-13]
        snapshot["inflation"] = round(((current - year_ago) / year_ago) * 100, 2)

    ffr = fetch_latest_indicator("DFF")
    if ffr:
        snapshot["fed_funds_rate"] = round(ffr["value"], 2)

    unemp = fetch_latest_indicator("UNRATE")
    if unemp:
        snapshot["unemployment"] = round(unemp["value"], 2)

    ten_y = fetch_latest_indicator("DGS10")
    if ten_y:
        snapshot["us_10y_yield"] = round(ten_y["value"], 2)

    vix = fetch_latest_indicator("VIXCLS")
    if vix:
        snapshot["vix"] = round(vix["value"], 2)

    yc = fetch_latest_indicator("T10Y2Y")
    if yc:
        snapshot["yield_curve"] = round(yc["value"], 2)

    return snapshot


def get_recession_probability() -> int | None:
    """Return a simple recession probability estimate based on the yield curve."""
    yc = fetch_latest_indicator("T10Y2Y")
    if not yc:
        return None
    spread = yc["value"]
    if spread < -0.5:
        return 85
    if spread < 0:
        return 70
    if spread < 0.5:
        return 40
    if spread < 1:
        return 20
    return 10