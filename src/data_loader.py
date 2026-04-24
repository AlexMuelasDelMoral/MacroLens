import json
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def load_events():
    """Load all historical events."""
    with open(DATA_DIR / "events.json", "r") as f:
        data = json.load(f)
    return data["events"]

def load_impacts():
    """Load asset impact data per event."""
    with open(DATA_DIR / "asset_impacts.json", "r") as f:
        data = json.load(f)
    return data["impacts"]

def get_event_by_id(event_id):
    """Get a specific event by its ID."""
    events = load_events()
    for event in events:
        if event["id"] == event_id:
            return event
    return None

def get_impact_by_id(event_id):
    """Get impact data for a specific event."""
    impacts = load_impacts()
    return impacts.get(event_id, None)

def events_to_dataframe():
    """Convert events to pandas DataFrame for easy filtering."""
    events = load_events()
    df = pd.DataFrame(events)
    # Flatten pre_conditions
    pre_cond_df = pd.json_normalize(df["pre_conditions"])
    pre_cond_df.columns = [f"pre_{col}" for col in pre_cond_df.columns]
    df = pd.concat([df.drop("pre_conditions", axis=1), pre_cond_df], axis=1)
    return df

def get_categories():
    """Get all unique event categories."""
    events = load_events()
    return sorted(set(e["category"] for e in events))

# Full asset taxonomy organized by category
ASSET_CATEGORIES = {
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

# Flattened dictionary for quick lookup
ASSET_LABELS = {}
for category, assets in ASSET_CATEGORIES.items():
    ASSET_LABELS.update(assets)


def get_asset_classes():
    """Get all asset class IDs."""
    return list(ASSET_LABELS.keys())


def get_assets_by_category():
    """Get assets grouped by category."""
    return ASSET_CATEGORIES


def get_category_for_asset(asset_id):
    """Find which category an asset belongs to."""
    for category, assets in ASSET_CATEGORIES.items():
        if asset_id in assets:
            return category
    return None


# Asset characteristics for rule-based estimation
ASSET_CHARACTERISTICS = {
    # US Equities - Size
    "sp500": {"beta": 1.0, "type": "equity", "rate_sens": -0.5, "inflation_sens": -0.3, "crisis_beta": 1.0},
    "nasdaq": {"beta": 1.2, "type": "equity_growth", "rate_sens": -0.9, "inflation_sens": -0.5, "crisis_beta": 1.2},
    "dow_jones": {"beta": 0.9, "type": "equity", "rate_sens": -0.4, "inflation_sens": -0.3, "crisis_beta": 0.9},
    "russell_2000": {"beta": 1.3, "type": "equity_small", "rate_sens": -0.7, "inflation_sens": -0.4, "crisis_beta": 1.4},
    "russell_midcap": {"beta": 1.1, "type": "equity", "rate_sens": -0.6, "inflation_sens": -0.3, "crisis_beta": 1.15},
    
    # US Equities - Sector
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
    
    # International Equities
    "developed_ex_us": {"beta": 1.0, "type": "equity_intl", "rate_sens": -0.5, "inflation_sens": -0.3, "crisis_beta": 1.1},
    "europe_stoxx": {"beta": 1.0, "type": "equity_intl", "rate_sens": -0.5, "inflation_sens": -0.3, "crisis_beta": 1.15},
    "uk_ftse": {"beta": 0.9, "type": "equity_intl", "rate_sens": -0.4, "inflation_sens": -0.2, "crisis_beta": 1.0},
    "japan_nikkei": {"beta": 1.0, "type": "equity_intl", "rate_sens": -0.5, "inflation_sens": -0.3, "crisis_beta": 1.1},
    "china_equity": {"beta": 1.3, "type": "equity_em", "rate_sens": -0.6, "inflation_sens": -0.3, "crisis_beta": 1.3},
    "emerging_markets": {"beta": 1.3, "type": "equity_em", "rate_sens": -0.8, "inflation_sens": -0.4, "crisis_beta": 1.5},
    "india_equity": {"beta": 1.2, "type": "equity_em", "rate_sens": -0.6, "inflation_sens": -0.3, "crisis_beta": 1.3},
    
    # Fixed Income
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
    
    # Commodities
    "oil_wti": {"beta": 0.5, "type": "commodity", "rate_sens": -0.3, "inflation_sens": 1.5, "crisis_beta": -0.3},
    "natural_gas": {"beta": 0.3, "type": "commodity", "rate_sens": -0.2, "inflation_sens": 1.2, "crisis_beta": -0.1},
    "gold": {"beta": -0.1, "type": "commodity_safe", "rate_sens": -0.8, "inflation_sens": 1.0, "crisis_beta": -0.5},
    "silver": {"beta": 0.3, "type": "commodity_safe", "rate_sens": -0.7, "inflation_sens": 1.2, "crisis_beta": 0.0},
    "copper": {"beta": 0.8, "type": "commodity", "rate_sens": -0.5, "inflation_sens": 0.8, "crisis_beta": 1.0},
    "platinum": {"beta": 0.5, "type": "commodity", "rate_sens": -0.6, "inflation_sens": 0.9, "crisis_beta": 0.5},
    "agriculture": {"beta": 0.2, "type": "commodity", "rate_sens": -0.1, "inflation_sens": 0.8, "crisis_beta": 0.1},
    "wheat": {"beta": 0.1, "type": "commodity", "rate_sens": -0.1, "inflation_sens": 0.8, "crisis_beta": 0.0},
    "corn": {"beta": 0.1, "type": "commodity", "rate_sens": -0.1, "inflation_sens": 0.7, "crisis_beta": 0.0},
    
    # Currencies
    "usd_index": {"beta": -0.3, "type": "currency_safe", "rate_sens": 1.5, "inflation_sens": -0.3, "crisis_beta": -0.5},
    "eur_usd": {"beta": 0.3, "type": "currency", "rate_sens": -1.0, "inflation_sens": 0.2, "crisis_beta": 0.4},
    "jpy_usd": {"beta": -0.3, "type": "currency_safe", "rate_sens": -0.8, "inflation_sens": -0.1, "crisis_beta": -0.4},
    "chf_usd": {"beta": -0.4, "type": "currency_safe", "rate_sens": -0.5, "inflation_sens": -0.2, "crisis_beta": -0.5},
    "gbp_usd": {"beta": 0.4, "type": "currency", "rate_sens": -1.0, "inflation_sens": 0.1, "crisis_beta": 0.5},
    "em_fx": {"beta": 0.7, "type": "currency_em", "rate_sens": -1.5, "inflation_sens": -0.3, "crisis_beta": 1.0},
    
    # Alternatives & Crypto
    "bitcoin": {"beta": 1.5, "type": "crypto", "rate_sens": -1.5, "inflation_sens": 0.3, "crisis_beta": 1.3},
    "ethereum": {"beta": 1.7, "type": "crypto", "rate_sens": -1.7, "inflation_sens": 0.2, "crisis_beta": 1.5},
    "reits_global": {"beta": 0.9, "type": "real_asset", "rate_sens": -1.2, "inflation_sens": 0.3, "crisis_beta": 1.2},
    "vix": {"beta": -3.5, "type": "volatility", "rate_sens": 0.5, "inflation_sens": 0.0, "crisis_beta": -4.0},
    "hedge_fund_idx": {"beta": 0.4, "type": "alt", "rate_sens": -0.3, "inflation_sens": 0.0, "crisis_beta": 0.5},
    "private_equity": {"beta": 1.1, "type": "alt", "rate_sens": -0.8, "inflation_sens": -0.2, "crisis_beta": 1.2},
}
