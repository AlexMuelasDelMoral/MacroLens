"""
Rule-based impact generator for asset returns during crisis events.
Uses economic theory and asset characteristics to estimate returns.
"""
import numpy as np
from src.data_loader import ASSET_CHARACTERISTICS


# Event-category archetypes (baseline SP500 impact patterns)
EVENT_ARCHETYPES = {
    "Financial Crisis": {
        "1m": -12, "3m": -22, "6m": -30, "1y": -35, "2y": -15,
        "risk_off": 1.0, "inflation_impact": -0.5, "rate_impact": -1.5
    },
    "Market Crash": {
        "1m": -10, "3m": -18, "6m": -22, "1y": -25, "2y": -10,
        "risk_off": 0.9, "inflation_impact": 0.0, "rate_impact": -1.0
    },
    "Health Crisis": {
        "1m": -15, "3m": -20, "6m": 2, "1y": 15, "2y": 25,
        "risk_off": 1.0, "inflation_impact": -0.3, "rate_impact": -1.5
    },
    "Supply Shock": {
        "1m": -5, "3m": -10, "6m": -18, "1y": -25, "2y": -15,
        "risk_off": 0.6, "inflation_impact": 1.5, "rate_impact": 1.0
    },
    "Inflation Shock": {
        "1m": -3, "3m": -8, "6m": -12, "1y": -15, "2y": -5,
        "risk_off": 0.3, "inflation_impact": 2.0, "rate_impact": 1.5
    },
    "Monetary Policy": {
        "1m": -3, "3m": -7, "6m": -12, "1y": -15, "2y": 5,
        "risk_off": 0.4, "inflation_impact": -0.5, "rate_impact": 2.0
    },
    "Currency Crisis": {
        "1m": -6, "3m": -12, "6m": -18, "1y": -15, "2y": 0,
        "risk_off": 0.7, "inflation_impact": 0.3, "rate_impact": 0.5
    },
    "Sovereign Debt": {
        "1m": -5, "3m": -10, "6m": -15, "1y": -12, "2y": 5,
        "risk_off": 0.7, "inflation_impact": 0.0, "rate_impact": -0.5
    },
    "Geopolitical": {
        "1m": -4, "3m": -6, "6m": -8, "1y": -5, "2y": 10,
        "risk_off": 0.6, "inflation_impact": 0.5, "rate_impact": 0.3
    },
    "Political": {
        "1m": -2, "3m": 2, "6m": 5, "1y": 8, "2y": 12,
        "risk_off": 0.3, "inflation_impact": 0.0, "rate_impact": 0.0
    }
}


def generate_asset_impact(asset_id, event, horizon):
    """
    Generate impact estimate for an asset during an event.
    Uses event archetype + asset characteristics + severity scaling.
    """
    if asset_id not in ASSET_CHARACTERISTICS:
        return None
    
    asset = ASSET_CHARACTERISTICS[asset_id]
    archetype = EVENT_ARCHETYPES.get(event["category"])
    if not archetype:
        return 0.0
    
    # Base impact scaled by severity (archetype assumes severity ~7)
    severity_scalar = event["severity"] / 7.0
    base_equity_impact = archetype[horizon] * severity_scalar
    
    # Compute impact based on asset characteristics
    risk_off = archetype["risk_off"]
    inflation_effect = archetype["inflation_impact"]
    rate_effect = archetype["rate_impact"]
    
    # Start with base impact scaled by crisis beta
    impact = base_equity_impact * asset["crisis_beta"] * risk_off
    
    # Adjust for inflation sensitivity
    impact += inflation_effect * asset["inflation_sens"] * severity_scalar * 3
    
    # Adjust for interest rate sensitivity (simplified)
    impact += rate_effect * asset["rate_sens"] * severity_scalar * 2
    
    # Asset-specific adjustments
    asset_type = asset["type"]
    
    # Time decay/recovery patterns by asset type
    horizon_multiplier = {
        "1m": 1.0, "3m": 1.0, "6m": 1.0, "1y": 1.0, "2y": 1.0
    }
    
    if asset_type == "commodity_safe":  # Gold, Silver
        # Usually positive in crisis except initial liquidity selling
        if horizon == "1m":
            impact = -abs(impact) * 0.3  # Initial dip
        else:
            impact = abs(impact) * 0.5 + 5 * severity_scalar  # Then rally
    
    elif asset_type == "currency_safe":  # USD, JPY, CHF
        # Strengthens in crisis
        impact = abs(base_equity_impact) * 0.3 * risk_off
    
    elif asset_type == "volatility":  # VIX
        # Explodes in crisis
        impact = abs(base_equity_impact) * 5 * risk_off
        if horizon in ["1y", "2y"]:
            impact *= 0.3  # Volatility mean-reverts
    
    elif asset_type == "bond_long":
        # Long bonds rally in deflation/crisis, crash in inflation
        if event["category"] in ["Inflation Shock", "Supply Shock", "Monetary Policy"]:
            impact = -abs(rate_effect) * abs(asset["rate_sens"]) * 0.5 * severity_scalar
        else:
            impact = abs(base_equity_impact) * 0.4 * risk_off
    
    elif asset_type == "bond_short":
        # Less volatile, mild response
        impact = impact * 0.2
    
    elif asset_type == "bond_ip":  # TIPS
        # Mixed - helps in inflation, hurts on real rates
        if event["category"] in ["Inflation Shock", "Supply Shock"]:
            impact = 3 * severity_scalar * horizon_multiplier[horizon]
        else:
            impact = impact * 0.3
    
    elif asset_type == "crypto":
        # Highly volatile, behavior still evolving
        # COVID 2020 special case - massive rally post-initial crash
        if event["id"] == "covid_2020":
            crypto_pattern = {"1m": -25, "3m": 35, "6m": 85, "1y": 330, "2y": 320}
            impact = crypto_pattern.get(horizon, 0)
        else:
            impact = impact * 1.3  # Higher volatility
    
    # Apply horizon-specific recovery for defensive/safe haven in deep crises
    if asset_type in ["equity_defensive"] and horizon in ["1y", "2y"]:
        impact *= 0.6  # Recover faster
    
    # Cap extreme values
    impact = max(-85, min(500, impact))
    
    return round(float(impact), 2)


def generate_full_impact_data(events):
    """Generate complete impact data for all events and assets."""
    from src.data_loader import get_asset_classes
    
    all_impacts = {}
    assets = get_asset_classes()
    horizons = ["1m", "3m", "6m", "1y", "2y"]
    
    for event in events:
        event_id = event["id"]
        all_impacts[event_id] = {}
        
        for asset in assets:
            asset_impacts = {}
            for horizon in horizons:
                # Skip crypto pre-2009
                if asset in ["bitcoin", "ethereum"] and event["year"] < 2009:
                    asset_impacts[horizon] = None
                    continue
                # Skip ETH pre-2015
                if asset == "ethereum" and event["year"] < 2015:
                    asset_impacts[horizon] = None
                    continue
                
                impact = generate_asset_impact(asset, event, horizon)
                asset_impacts[horizon] = impact
            
            all_impacts[event_id][asset] = asset_impacts
    
    return all_impacts


def override_with_curated_data(generated_impacts, curated_impacts):
    """
    Merge curated historical data with generated estimates.
    Curated values take precedence where available.
    """
    for event_id, event_data in curated_impacts.items():
        if event_id not in generated_impacts:
            generated_impacts[event_id] = {}
        for asset, horizons in event_data.items():
            if asset not in generated_impacts[event_id]:
                generated_impacts[event_id][asset] = {}
            for horizon, value in horizons.items():
                if value is not None:
                    generated_impacts[event_id][asset][horizon] = value
    return generated_impacts