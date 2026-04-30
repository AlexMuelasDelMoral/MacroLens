"""Data access layer for MacroLens.

All JSON file reads are cached via Streamlit's @st.cache_data so repeated
calls within and across pages are free after the first load. The cache
invalidates after one hour or when the underlying file changes.

Asset taxonomy and characteristics are module-level constants and are
imported directly rather than through accessor functions where possible.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src.constants import DEFAULT_CACHE_TTL_SECONDS

DATA_DIR: Path = Path(__file__).parent.parent / "data"


@st.cache_data(ttl=DEFAULT_CACHE_TTL_SECONDS, show_spinner=False)
def load_events() -> list[dict[str, Any]]:
    """Load all historical events. Cached for one hour."""
    with open(DATA_DIR / "events.json", "r") as f:
        data = json.load(f)
    return data["events"]


@st.cache_data(ttl=DEFAULT_CACHE_TTL_SECONDS, show_spinner=False)
def load_impacts() -> dict[str, dict[str, dict[str, float]]]:
    """Load asset impact data per event. Cached for one hour.

    Returns a nested mapping: event_id -> asset_id -> horizon -> return_pct.
    """
    with open(DATA_DIR / "asset_impacts.json", "r") as f:
        data = json.load(f)
    return data["impacts"]


@st.cache_data(ttl=DEFAULT_CACHE_TTL_SECONDS, show_spinner=False)
def load_data_quality() -> dict[str, dict[str, dict[str, str]]]:
    """Load data quality metadata. Cached for one hour.

    Returns event_id -> asset_id -> horizon -> quality_label, where
    quality_label is one of 'real', 'curated', 'estimated', or 'missing'.
    Returns an empty dict if the quality file is not present.
    """
    quality_path = DATA_DIR / "data_quality.json"
    if not quality_path.exists():
        return {}
    with open(quality_path, "r") as f:
        return json.load(f)


def get_event_by_id(event_id: str) -> dict[str, Any] | None:
    """Get a specific event by its ID."""
    for event in load_events():
        if event["id"] == event_id:
            return event
    return None


def get_impact_by_id(event_id: str) -> dict[str, dict[str, float]] | None:
    """Get impact data for a specific event."""
    return load_impacts().get(event_id)


@st.cache_data(ttl=DEFAULT_CACHE_TTL_SECONDS, show_spinner=False)
def events_to_dataframe() -> pd.DataFrame:
    """Convert events to pandas DataFrame for easy filtering. Cached.

    Pre-conditions are flattened into separate columns prefixed with 'pre_'.
    """
    events = load_events()
    df = pd.DataFrame(events)
    pre_cond_df = pd.json_normalize(df["pre_conditions"])
    pre_cond_df.columns = [f"pre_{col}" for col in pre_cond_df.columns]
    df = pd.concat([df.drop("pre_conditions", axis=1), pre_cond_df], axis=1)
    return df


def get_categories() -> list[str]:
    """Get all unique event categories sorted alphabetically."""
    return sorted({e["category"] for e in load_events()})


def get_data_quality_for_event(event_id: str) -> dict[str, dict[str, str]]:
    """Get quality breakdown for a specific event."""
    return load_data_quality().get(event_id, {})


def calculate_quality_score(event_id: str) -> dict[str, int]:
    """Return counts of each quality label for a given event."""
    quality = get_data_quality_for_event(event_id)
    counts: dict[str, int] = {"real": 0, "curated": 0, "estimated": 0, "missing": 0}
    for asset_data in quality.values():
        for label in asset_data.values():
            counts[label] = counts.get(label, 0) + 1
    return counts


ASSET_CATEGORIES: dict[str, dict[str, str]] = {
    "US Equities - Size": {
        "sp500": "S&P 500",
        "nasdaq": "NASDAQ 100",
        "dow_jones": "Dow Jones Industrial",
        "russell_2000": "Russell 2000 (Small Cap)",
        "russell_midcap": "Russell Midcap"
    },
    "US Equities - Sector": {
        "tech": "Technology",
        "healthcare": "Healthcare",
        "financials": "Financials",
        "energy": "Energy",
        "utilities": "Utilities",
        "consumer_staples": "Consumer Staples",
        "consumer_discretionary": "Consumer Discretionary",
        "luxury": "Luxury Goods",
        "industrials": "Industrials",
        "basic_materials": "Basic Materials",
        "communication": "Communication Services",
        "reits_us": "US REITs"
    },
    "International Equities": {
        "developed_ex_us": "Developed Markets ex-US (EAFE)",
        "europe_stoxx": "Europe STOXX 600",
        "uk_ftse": "UK FTSE 100",
        "japan_nikkei": "Japan Nikkei 225",
        "china_equity": "China (Hang Seng/Shanghai)",
        "emerging_markets": "Emerging Markets (broad)",
        "india_equity": "India (Nifty 50)"
    },
    "Fixed Income": {
        "us_tbill_3m": "US 3M T-Bill",
        "us_2y_treasury": "US 2Y Treasury",
        "us_10y_treasury": "US 10Y Treasury",
        "us_30y_treasury": "US 30Y Treasury",
        "tips": "TIPS (Inflation Protected)",
        "corporate_ig": "Investment Grade Corporate",
        "high_yield": "High Yield Bonds",
        "municipal": "Municipal Bonds",
        "em_debt": "Emerging Market Debt",
        "intl_bonds": "International Developed Bonds"
    },
    "Commodities": {
        "oil_wti": "Crude Oil (WTI)",
        "natural_gas": "Natural Gas",
        "gold": "Gold",
        "silver": "Silver",
        "copper": "Copper",
        "platinum": "Platinum",
        "agriculture": "Agriculture (broad)",
        "wheat": "Wheat",
        "corn": "Corn"
    },
    "Currencies": {
        "usd_index": "US Dollar Index (DXY)",
        "eur_usd": "EUR/USD",
        "jpy_usd": "JPY/USD",
        "chf_usd": "Swiss Franc (CHF)",
        "gbp_usd": "British Pound",
        "em_fx": "EM Currencies Basket"
    },
    "Alternatives & Crypto": {
        "bitcoin": "Bitcoin",
        "ethereum": "Ethereum",
        "reits_global": "Global REITs",
        "vix": "VIX (Volatility)",
        "hedge_fund_idx": "Hedge Fund Index (HFRX)",
        "private_equity": "Private Equity Proxy"
    }
}

ASSET_LABELS: dict[str, str] = {}
for _category, _assets in ASSET_CATEGORIES.items():
    ASSET_LABELS.update(_assets)


def get_asset_classes() -> list[str]:
    """Get all asset class IDs."""
    return list(ASSET_LABELS.keys())


def get_assets_by_category() -> dict[str, dict[str, str]]:
    """Get assets grouped by category."""
    return ASSET_CATEGORIES


def get_category_for_asset(asset_id: str) -> str | None:
    """Find which category an asset belongs to."""
    for category, assets in ASSET_CATEGORIES.items():
        if asset_id in assets:
            return category
    return None


ASSET_CHARACTERISTICS: dict[str, dict[str, Any]] = {
    "sp500": {"beta": 1.0, "type": "equity", "rate_sens": -0.5, "inflation_sens": -0.3, "crisis_beta": 1.0},
    "nasdaq": {"beta": 1.2, "type": "equity_growth", "rate_sens": -0.9, "inflation_sens": -0.5, "crisis_beta": 1.2},
    "dow_jones": {"beta": 0.9, "type": "equity", "rate_sens": -0.4, "inflation_sens": -0.3, "crisis_beta": 0.9},
    "russell_2000": {"beta": 1.3, "type": "equity_small", "rate_sens": -0.7, "inflation_sens": -0.4, "crisis_beta": 1.4},
    "russell_midcap": {"beta": 1.1, "type": "equity", "rate_sens": -0.6, "inflation_sens": -0.3, "crisis_beta": 1.15},
    "tech": {"beta": 1.3, "type": "equity_growth", "rate_sens": -1.0, "inflation_sens": -0.6, "crisis_beta": 1.25},
    "healthcare": {"beta": 0.7, "type": "equity_defensive", "rate_sens": -0.3, "inflation_sens": -0.2, "crisis_beta": 0.75},
    "financials": {"beta": 1.3, "type": "equity_cyclical", "rate_sens": 0.4, "inflation_sens": -0.2, "crisis_beta": 1.5},
    "energy": {"beta": 1.2, "type": "equity_cyclical", "rate_sens": -0.2, "inflation_sens": 0.8, "crisis_beta": 1.1},
    "utilities": {"beta": 0.5, "type": "equity_defensive", "rate_sens": -0.8, "inflation_sens": -0.3, "crisis_beta": 0.6},
    "consumer_staples": {"beta": 0.6, "type": "equity_defensive", "rate_sens": -0.3, "inflation_sens": 0.0, "crisis_beta": 0.65},
    "consumer_discretionary": {"beta": 1.2, "type": "equity_cyclical", "rate_sens": -0.7, "inflation_sens": -0.5, "crisis_beta": 1.3},
    "luxury": {"beta": 1.3, "type": "equity_cyclical", "rate_sens": -0.6, "inflation_sens": -0.4, "crisis_beta": 1.4},
    "industrials": {"beta": 1.1, "type": "equity_cyclical", "rate_sens": -0.4, "inflation_sens": -0.2, "crisis_beta": 1.2},
    "basic_materials": {"beta": 1.2, "type": "equity_cyclical", "rate_sens": -0.3, "inflation_sens": 0.6, "crisis_beta": 1.3},
    "communication": {"beta": 1.1, "type": "equity_growth", "rate_sens": -0.8, "inflation_sens": -0.4, "crisis_beta": 1.1},
    "reits_us": {"beta": 0.9, "type": "real_asset", "rate_sens": -1.1, "inflation_sens": 0.3, "crisis_beta": 1.15},
    "developed_ex_us": {"beta": 1.0, "type": "equity_intl", "rate_sens": -0.5, "inflation_sens": -0.3, "crisis_beta": 1.1},
    "europe_stoxx": {"beta": 1.0, "type": "equity_intl", "rate_sens": -0.5, "inflation_sens": -0.3, "crisis_beta": 1.15},
    "uk_ftse": {"beta": 0.9, "type": "equity_intl", "rate_sens": -0.4, "inflation_sens": -0.2, "crisis_beta": 1.0},
    "japan_nikkei": {"beta": 1.0, "type": "equity_intl", "rate_sens": -0.5, "inflation_sens": -0.3, "crisis_beta": 1.1},
    "china_equity": {"beta": 1.3, "type": "equity_em", "rate_sens": -0.6, "inflation_sens": -0.3, "crisis_beta": 1.3},
    "emerging_markets": {"beta": 1.3, "type": "equity_em", "rate_sens": -0.8, "inflation_sens": -0.4, "crisis_beta": 1.5},
    "india_equity": {"beta": 1.2, "type": "equity_em", "rate_sens": -0.6, "inflation_sens": -0.3, "crisis_beta": 1.3},
    "us_tbill_3m": {"beta": 0.0, "type": "bond_short", "rate_sens": 0.05, "inflation_sens": 0.0, "crisis_beta": -0.1},
    "us_2y_treasury": {"beta": 0.0, "type": "bond_short", "rate_sens": -2.0, "inflation_sens": -0.5, "crisis_beta": -0.3},
    "us_10y_treasury": {"beta": -0.1, "type": "bond_long", "rate_sens": -8.0, "inflation_sens": -1.5, "crisis_beta": -0.5},
    "us_30y_treasury": {"beta": -0.2, "type": "bond_long", "rate_sens": -18.0, "inflation_sens": -2.5, "crisis_beta": -0.7},
    "tips": {"beta": 0.0, "type": "bond_ip", "rate_sens": -5.0, "inflation_sens": 2.0, "crisis_beta": -0.2},
    "corporate_ig": {"beta": 0.3, "type": "bond_credit", "rate_sens": -6.0, "inflation_sens": -1.0, "crisis_beta": 0.4},
    "high_yield": {"beta": 0.6, "type": "bond_credit", "rate_sens": -3.0, "inflation_sens": -0.3, "crisis_beta": 0.9},
    "municipal": {"beta": 0.1, "type": "bond_credit", "rate_sens": -5.0, "inflation_sens": -0.8, "crisis_beta": 0.2},
    "em_debt": {"beta": 0.7, "type": "bond_em", "rate_sens": -4.0, "inflation_sens": -0.5, "crisis_beta": 1.1},
    "intl_bonds": {"beta": 0.1, "type": "bond_intl", "rate_sens": -5.0, "inflation_sens": -0.8, "crisis_beta": 0.2},
    "oil_wti": {"beta": 0.5, "type": "commodity", "rate_sens": -0.3, "inflation_sens": 1.5, "crisis_beta": -0.3},
    "natural_gas": {"beta": 0.3, "type": "commodity", "rate_sens": -0.2, "inflation_sens": 1.2, "crisis_beta": -0.1},
    "gold": {"beta": -0.1, "type": "commodity_safe", "rate_sens": -0.8, "inflation_sens": 1.0, "crisis_beta": -0.5},
    "silver": {"beta": 0.3, "type": "commodity_safe", "rate_sens": -0.7, "inflation_sens": 1.2, "crisis_beta": 0.0},
    "copper": {"beta": 0.8, "type": "commodity", "rate_sens": -0.5, "inflation_sens": 0.8, "crisis_beta": 1.0},
    "platinum": {"beta": 0.5, "type": "commodity", "rate_sens": -0.6, "inflation_sens": 0.9, "crisis_beta": 0.5},
    "agriculture": {"beta": 0.2, "type": "commodity", "rate_sens": -0.1, "inflation_sens": 0.8, "crisis_beta": 0.1},
    "wheat": {"beta": 0.1, "type": "commodity", "rate_sens": -0.1, "inflation_sens": 0.8, "crisis_beta": 0.0},
    "corn": {"beta": 0.1, "type": "commodity", "rate_sens": -0.1, "inflation_sens": 0.7, "crisis_beta": 0.0},
    "usd_index": {"beta": -0.3, "type": "currency_safe", "rate_sens": 1.5, "inflation_sens": -0.3, "crisis_beta": -0.5},
    "eur_usd": {"beta": 0.3, "type": "currency", "rate_sens": -1.0, "inflation_sens": 0.2, "crisis_beta": 0.4},
    "jpy_usd": {"beta": -0.3, "type": "currency_safe", "rate_sens": -0.8, "inflation_sens": -0.1, "crisis_beta": -0.4},
    "chf_usd": {"beta": -0.4, "type": "currency_safe", "rate_sens": -0.5, "inflation_sens": -0.2, "crisis_beta": -0.5},
    "gbp_usd": {"beta": 0.4, "type": "currency", "rate_sens": -1.0, "inflation_sens": 0.1, "crisis_beta": 0.5},
    "em_fx": {"beta": 0.7, "type": "currency_em", "rate_sens": -1.5, "inflation_sens": -0.3, "crisis_beta": 1.0},
    "bitcoin": {"beta": 1.5, "type": "crypto", "rate_sens": -1.5, "inflation_sens": 0.3, "crisis_beta": 1.3},
    "ethereum": {"beta": 1.7, "type": "crypto", "rate_sens": -1.7, "inflation_sens": 0.2, "crisis_beta": 1.5},
    "reits_global": {"beta": 0.9, "type": "real_asset", "rate_sens": -1.2, "inflation_sens": 0.3, "crisis_beta": 1.2},
    "vix": {"beta": -3.5, "type": "volatility", "rate_sens": 0.5, "inflation_sens": 0.0, "crisis_beta": -4.0},
    "hedge_fund_idx": {"beta": 0.4, "type": "alt", "rate_sens": -0.3, "inflation_sens": 0.0, "crisis_beta": 0.5},
    "private_equity": {"beta": 1.1, "type": "alt", "rate_sens": -0.8, "inflation_sens": -0.2, "crisis_beta": 1.2},
}