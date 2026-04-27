"""
Look up historical macroeconomic conditions at any date.
Uses FRED API when available, falls back to interpolating from event database.
"""
from datetime import datetime, timedelta
import streamlit as st


def _get_fred_client():
    """Lazy-load FRED client to avoid import errors."""
    try:
        from src.live_data import get_fred_client
        return get_fred_client()
    except Exception:
        return None


@st.cache_data(ttl=86400)
def get_historical_macro_fred(target_date_str):
    """Get macro conditions at a date from FRED."""
    fred = _get_fred_client()
    if not fred:
        return None

    target = datetime.strptime(target_date_str, "%Y-%m-%d")
    lookback = target - timedelta(days=400)
    forward = target + timedelta(days=30)

    snapshot = {}

    try:
        # CPI for YoY inflation
        cpi = fred.get_series("CPIAUCSL",
                               observation_start=lookback.strftime("%Y-%m-%d"),
                               observation_end=forward.strftime("%Y-%m-%d"))
        if not cpi.empty:
            valid = cpi[cpi.index <= target]
            if len(valid) >= 13:
                current = valid.iloc[-1]
                year_ago = valid.iloc[-13]
                snapshot["inflation"] = round(((current - year_ago) / year_ago) * 100, 2)
    except Exception:
        pass

    try:
        ffr = fred.get_series("DFF",
                               observation_start=(target - timedelta(days=10)).strftime("%Y-%m-%d"),
                               observation_end=forward.strftime("%Y-%m-%d"))
        if not ffr.empty:
            valid = ffr[ffr.index <= target]
            if len(valid) > 0:
                snapshot["fed_funds_rate"] = round(float(valid.iloc[-1]), 2)
    except Exception:
        pass

    try:
        unemp = fred.get_series("UNRATE",
                                  observation_start=lookback.strftime("%Y-%m-%d"),
                                  observation_end=forward.strftime("%Y-%m-%d"))
        if not unemp.empty:
            valid = unemp[unemp.index <= target]
            if len(valid) > 0:
                snapshot["unemployment"] = round(float(valid.iloc[-1]), 2)
    except Exception:
        pass

    try:
        gdp = fred.get_series("A191RL1Q225SBEA",
                                observation_start=lookback.strftime("%Y-%m-%d"),
                                observation_end=forward.strftime("%Y-%m-%d"))
        if not gdp.empty:
            valid = gdp[gdp.index <= target]
            if len(valid) > 0:
                snapshot["gdp_growth"] = round(float(valid.iloc[-1]), 2)
    except Exception:
        pass

    return snapshot if snapshot else None


def get_historical_macro_from_events(target_date_str):
    """Fallback: find the closest event's pre_conditions."""
    from src.data_loader import load_events

    target = datetime.strptime(target_date_str, "%Y-%m-%d")
    events = load_events()

    closest = None
    min_diff = float("inf")
    for event in events:
        event_date = datetime.strptime(event["start_date"], "%Y-%m-%d")
        diff = abs((event_date - target).days)
        if diff < min_diff:
            min_diff = diff
            closest = event

    if closest:
        macro = dict(closest["pre_conditions"])
        macro["_source"] = f"approximated from {closest['name']}"
        macro["_days_off"] = min_diff
        return macro

    return None


def get_historical_macro(target_date_str):
    """Get macro conditions at any historical date. Returns dict with values + source info."""
    # Try FRED first
    fred_data = get_historical_macro_fred(target_date_str)
    if fred_data and len(fred_data) >= 3:
        fred_data["_source"] = "FRED API (Federal Reserve)"
        return fred_data

    # Fallback to event database
    return get_historical_macro_from_events(target_date_str)


# Famous moments — useful presets for users
FAMOUS_MOMENTS = [
    {
        "label": "Pre-COVID Peak (Feb 2020)",
        "date": "2020-02-19",
        "context": "S&P 500 all-time high. Pandemic news emerging from Wuhan.",
        "what_happened": "Markets crashed 34% over the next month."
    },
    {
        "label": "Pre-Lehman Collapse (Sept 2008)",
        "date": "2008-09-12",
        "context": "Last Friday before Lehman Brothers bankruptcy filing.",
        "what_happened": "Global financial crisis. S&P 500 fell 43% over 6 months."
    },
    {
        "label": "Dot-com Peak (March 2000)",
        "date": "2000-03-10",
        "context": "NASDAQ all-time high before dot-com bust.",
        "what_happened": "NASDAQ fell 78% over 2.5 years."
    },
    {
        "label": "Pre-2022 Bear Market (Jan 2022)",
        "date": "2022-01-03",
        "context": "S&P 500 all-time high. Inflation was running hot at 7%.",
        "what_happened": "Fed hiked aggressively. S&P fell 25%, NASDAQ fell 35%."
    },
    {
        "label": "Pre-Russia Invasion (Feb 2022)",
        "date": "2022-02-23",
        "context": "Day before Russia invaded Ukraine.",
        "what_happened": "Energy spiked 40%, equities fell, USD strengthened."
    },
    {
        "label": "Post-COVID Recovery Start (April 2020)",
        "date": "2020-04-01",
        "context": "Markets had crashed 30%. Maximum fear. Massive Fed intervention.",
        "what_happened": "Strongest equity rally in history. S&P up 70% in 12 months."
    },
    {
        "label": "Pre-2008 Housing Peak (Oct 2007)",
        "date": "2007-10-09",
        "context": "S&P 500 peak before financial crisis became visible.",
        "what_happened": "Worst financial crisis since Great Depression."
    },
    {
        "label": "Brexit Vote Day (June 2016)",
        "date": "2016-06-23",
        "context": "UK EU referendum results coming.",
        "what_happened": "Pound crashed, brief global selloff, then recovered quickly."
    },
]