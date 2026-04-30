"""Shared constants for MacroLens.

Single source of truth for time horizons, display labels, color palettes,
and preset portfolios. Import from here rather than redeclaring literals
in individual pages or modules.
"""
from __future__ import annotations

from typing import Final

HORIZONS: Final[tuple[str, ...]] = ("1m", "3m", "6m", "1y", "2y")

HORIZON_LABELS: Final[dict[str, str]] = {
    "1m": "1M",
    "3m": "3M",
    "6m": "6M",
    "1y": "1Y",
    "2y": "2Y",
}

HORIZON_DAYS: Final[dict[str, int]] = {
    "1m": 21,
    "3m": 63,
    "6m": 126,
    "1y": 252,
    "2y": 504,
}

CHART_PALETTE: Final[tuple[str, ...]] = (
    "#00D4FF", "#7C3AED", "#00F5A0", "#FFB547", "#FF3B6B",
    "#0066FF", "#FF6B00", "#A78BFA", "#06B6D4", "#F472B6",
    "#FFD700", "#FF69B4", "#00FA9A", "#1E90FF", "#FFA07A",
)

COLOR_POSITIVE: Final[str] = "#00F5A0"
COLOR_NEGATIVE: Final[str] = "#FF3B6B"
COLOR_NEUTRAL: Final[str] = "#8B92B0"
COLOR_ACCENT: Final[str] = "#00D4FF"
COLOR_BACKGROUND: Final[str] = "#0A0E27"
COLOR_TEXT_PRIMARY: Final[str] = "#E4E8F1"
COLOR_TEXT_SECONDARY: Final[str] = "#B8C0DC"

DATA_QUALITY_REAL: Final[str] = "real"
DATA_QUALITY_CURATED: Final[str] = "curated"
DATA_QUALITY_ESTIMATED: Final[str] = "estimated"

DEFAULT_CACHE_TTL_SECONDS: Final[int] = 3600

PRESET_PORTFOLIOS: Final[dict[str, dict[str, float]]] = {
    "Custom": {},
    "60/40 Classic": {"sp500": 60, "us_10y_treasury": 40},
    "Aggressive Growth": {
        "sp500": 35, "nasdaq": 25, "tech": 15,
        "emerging_markets": 15, "bitcoin": 10,
    },
    "Permanent Portfolio": {
        "sp500": 25, "us_30y_treasury": 25,
        "gold": 25, "us_tbill_3m": 25,
    },
    "All-Weather (Dalio)": {
        "sp500": 30, "us_30y_treasury": 40, "us_10y_treasury": 15,
        "gold": 7.5, "basic_materials": 7.5,
    },
    "Global Diversified": {
        "sp500": 25, "developed_ex_us": 15, "emerging_markets": 10,
        "us_10y_treasury": 20, "corporate_ig": 10,
        "gold": 10, "reits_global": 10,
    },
    "Defensive": {
        "consumer_staples": 15, "utilities": 15, "healthcare": 15,
        "us_10y_treasury": 25, "gold": 15, "us_tbill_3m": 15,
    },
    "Crypto Heavy": {
        "bitcoin": 40, "ethereum": 20, "sp500": 20,
        "gold": 10, "us_10y_treasury": 10,
    },
    "Commodity Bull": {
        "oil_wti": 20, "gold": 20, "silver": 10, "copper": 10,
        "agriculture": 10, "energy": 15, "basic_materials": 15,
    },
}