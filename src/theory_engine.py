"""Economic theory explanations and frameworks."""

THEORIES = {
    "flight_to_quality": {
        "name": "Flight to Quality",
        "description": "During crises, investors move from risky to safe assets.",
        "implications": {
            "bonds_long": "Typically rise (yields fall) as investors seek safety",
            "gold": "Usually rises as haven asset",
            "usd": "Strengthens in global crises (reserve currency)",
            "equities": "Fall, especially small caps and EM",
            "high_yield": "Spreads widen significantly"
        }
    },
    "inflation_hedge": {
        "name": "Inflation Hedge Dynamics",
        "description": "Certain assets historically hedge against inflation.",
        "implications": {
            "gold": "Strong hedge, especially with negative real rates",
            "commodities": "Direct beneficiary of inflation",
            "tips": "Inflation-protected bonds benefit",
            "equities": "Mixed - pricing power matters",
            "bonds_long": "Hurt most by rising inflation"
        }
    },
    "monetary_policy_transmission": {
        "name": "Monetary Policy Transmission",
        "description": "How Fed policy propagates through markets.",
        "implications": {
            "bonds_short": "Move 1:1 with Fed rate expectations",
            "bonds_long": "Reflect growth + inflation expectations",
            "tech_growth": "Most sensitive to rates (duration risk)",
            "usd": "Strengthens with hawkish policy",
            "em_debt": "Suffers on USD strength + risk-off"
        }
    },
    "risk_on_off": {
        "name": "Risk-On / Risk-Off Regimes",
        "description": "Markets oscillate between risk appetite states.",
        "implications": {
            "risk_on": "Stocks up, USD/JPY up, gold down, yields up",
            "risk_off": "Stocks down, USD/JPY down, gold up, yields down",
            "correlations": "Spike to 1 during severe risk-off events"
        }
    },
    "stagflation": {
        "name": "Stagflation Dynamics",
        "description": "High inflation + low growth is toxic for most assets.",
        "implications": {
            "equities": "Multiple contraction + earnings pressure",
            "bonds": "Worst case - both rates and credit risk",
            "gold": "Historical best performer",
            "commodities": "Strong if supply-driven",
            "cash": "Loses real value but relatively safe"
        }
    }
}

CATEGORY_THEORY_MAP = {
    "Financial Crisis": ["flight_to_quality", "risk_on_off"],
    "Market Crash": ["flight_to_quality", "risk_on_off"],
    "Monetary Policy": ["monetary_policy_transmission"],
    "Inflation Shock": ["inflation_hedge", "stagflation"],
    "Supply Shock": ["stagflation", "inflation_hedge"],
    "Geopolitical": ["flight_to_quality", "risk_on_off"],
    "Currency Crisis": ["flight_to_quality", "monetary_policy_transmission"],
    "Sovereign Debt": ["flight_to_quality"],
    "Health Crisis": ["flight_to_quality", "risk_on_off"]
}

def get_relevant_theories(category):
    """Get applicable theories for an event category."""
    theory_ids = CATEGORY_THEORY_MAP.get(category, [])
    return [THEORIES[tid] for tid in theory_ids if tid in THEORIES]

def get_asset_narrative(asset_class, event_category):
    """Generate narrative explanation for asset under event type."""
    narratives = {
        ("gold", "Financial Crisis"): "Gold typically serves as a safe haven during financial crises, though initial liquidity-driven selling can occur before the flight-to-quality dominates.",
        ("gold", "Inflation Shock"): "Gold is a classic inflation hedge, especially when real interest rates turn negative.",
        ("sp500", "Monetary Policy"): "Equities face pressure from rate hikes through multiple contraction and higher discount rates.",
        ("bitcoin", "Financial Crisis"): "Bitcoin's behavior in crises is still evolving - initially correlates with risk assets but narrative of 'digital gold' may emerge.",
        ("oil", "Geopolitical"): "Oil spikes on supply disruption fears, especially with Middle East or major producer involvement.",
        ("tech", "Monetary Policy"): "Tech stocks are highly rate-sensitive due to long-duration cash flows - rate hikes cause severe multiple compression.",
    }
    return narratives.get((asset_class, event_category), 
        f"{asset_class} behavior during {event_category} depends on specific circumstances and policy response.")
