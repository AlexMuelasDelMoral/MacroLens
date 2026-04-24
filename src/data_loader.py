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

def get_asset_classes():
    """Get all asset classes tracked."""
    return [
        "sp500", "nasdaq", "tech", "oil", "gold",
        "us_10y_yield", "us_2y_yield", "usd_index", "bitcoin",
        "emerging_markets", "luxury", "basic_materials",
        "corporate_bonds_ig", "high_yield_bonds"
    ]

ASSET_LABELS = {
    "sp500": "S&P 500",
    "nasdaq": "NASDAQ",
    "tech": "Tech Stocks",
    "oil": "Crude Oil",
    "gold": "Gold",
    "us_10y_yield": "US 10Y Yield (bps)",
    "us_2y_yield": "US 2Y Yield (bps)",
    "usd_index": "US Dollar Index",
    "bitcoin": "Bitcoin",
    "emerging_markets": "Emerging Markets",
    "luxury": "Luxury Goods",
    "basic_materials": "Basic Materials",
    "corporate_bonds_ig": "IG Corporate Bonds",
    "high_yield_bonds": "High Yield Bonds"
}
