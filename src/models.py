"""Domain model dataclasses for MacroLens.

Provides typed, validated representations of the core data structures.
These sit alongside the existing dict-based system and can be adopted
incrementally. Nothing in the existing codebase breaks by adding this file.

Usage:
    from src.models import Event, AssetImpact, Portfolio, ScenarioResult
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class MacroConditions:
    """Pre-event macroeconomic state vector.

    All fields are optional because historical coverage varies.
    The similarity engine handles None values gracefully.
    """
    inflation: Optional[float] = None
    fed_funds_rate: Optional[float] = None
    unemployment: Optional[float] = None
    gdp_growth: Optional[float] = None
    vix: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> MacroConditions:
        return cls(
            inflation=data.get("inflation"),
            fed_funds_rate=data.get("fed_funds_rate"),
            unemployment=data.get("unemployment"),
            gdp_growth=data.get("gdp_growth"),
            vix=data.get("vix"),
        )

    def to_dict(self) -> dict:
        return {
            k: v for k, v in {
                "inflation": self.inflation,
                "fed_funds_rate": self.fed_funds_rate,
                "unemployment": self.unemployment,
                "gdp_growth": self.gdp_growth,
                "vix": self.vix,
            }.items()
            if v is not None
        }


@dataclass(frozen=True)
class Event:
    """A historical macroeconomic event.

    Matches the structure of events.json exactly so from_dict is lossless.
    """
    id: str
    name: str
    year: int
    start_date: str
    end_date: str
    category: str
    severity: int
    duration_months: int
    geography: str
    description: str
    triggers: tuple[str, ...]
    pre_conditions: MacroConditions

    def __post_init__(self) -> None:
        if not 1 <= self.severity <= 10:
            raise ValueError(
                f"Severity must be between 1 and 10, got {self.severity}"
            )
        if self.duration_months < 1:
            raise ValueError(
                f"Duration must be at least 1 month, got {self.duration_months}"
            )

    @classmethod
    def from_dict(cls, data: dict) -> Event:
        return cls(
            id=data["id"],
            name=data["name"],
            year=int(data["year"]),
            start_date=data["start_date"],
            end_date=data["end_date"],
            category=data["category"],
            severity=int(data["severity"]),
            duration_months=int(data["duration_months"]),
            geography=data.get("geography", "Global"),
            description=data.get("description", ""),
            triggers=tuple(data.get("triggers", [])),
            pre_conditions=MacroConditions.from_dict(
                data.get("pre_conditions", {})
            ),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "year": self.year,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "category": self.category,
            "severity": self.severity,
            "duration_months": self.duration_months,
            "geography": self.geography,
            "description": self.description,
            "triggers": list(self.triggers),
            "pre_conditions": self.pre_conditions.to_dict(),
        }


@dataclass(frozen=True)
class HorizonReturn:
    """Return for a single asset at a single time horizon."""
    horizon: str
    value: Optional[float]

    VALID_HORIZONS: frozenset[str] = field(
        default_factory=lambda: frozenset({"1m", "3m", "6m", "1y", "2y"}),
        compare=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        valid = {"1m", "3m", "6m", "1y", "2y"}
        if self.horizon not in valid:
            raise ValueError(
                f"Invalid horizon {self.horizon!r}. Must be one of {valid}."
            )


@dataclass(frozen=True)
class AssetImpact:
    """Impact data for a single asset across all time horizons.

    Immutable. Constructed once per event-asset combination.
    """
    asset_id: str
    returns: dict[str, Optional[float]]

    @classmethod
    def from_dict(cls, asset_id: str, data: dict) -> AssetImpact:
        valid_horizons = {"1m", "3m", "6m", "1y", "2y"}
        returns = {
            h: v for h, v in data.items()
            if h in valid_horizons
        }
        return cls(asset_id=asset_id, returns=returns)

    def get(self, horizon: str) -> Optional[float]:
        return self.returns.get(horizon)

    @property
    def has_data(self) -> bool:
        return any(v is not None for v in self.returns.values())

    @property
    def coverage(self) -> float:
        total = len(self.returns)
        if total == 0:
            return 0.0
        filled = sum(1 for v in self.returns.values() if v is not None)
        return filled / total


@dataclass
class Portfolio:
    """A collection of asset weights summing to one hundred percent.

    Weights are stored as percentages (0 to 100) matching the UI convention.
    Use fractions property when passing to the computation engine.
    """
    weights: dict[str, float] = field(default_factory=dict)
    name: str = "Custom"

    def __post_init__(self) -> None:
        self.weights = {k: float(v) for k, v in self.weights.items()}

    @classmethod
    def from_dict(cls, data: dict, name: str = "Custom") -> Portfolio:
        return cls(weights={k: float(v) for k, v in data.items()}, name=name)

    @property
    def active_positions(self) -> dict[str, float]:
        return {k: v for k, v in self.weights.items() if v > 0}

    @property
    def fractions(self) -> dict[str, float]:
        return {k: v / 100.0 for k, v in self.active_positions.items()}

    @property
    def total_weight(self) -> float:
        return sum(self.weights.values())

    @property
    def is_valid(self) -> bool:
        return abs(self.total_weight - 100.0) <= 0.1

    @property
    def position_count(self) -> int:
        return len(self.active_positions)

    def summary(self, asset_labels: dict[str, str]) -> str:
        positions = self.active_positions
        if not positions:
            return "Empty portfolio"
        top = sorted(positions.items(), key=lambda x: -x[1])[:3]
        parts = [f"{asset_labels.get(k, k)} {v:.0f}%" for k, v in top]
        suffix = (
            f" + {len(positions) - 3} more"
            if len(positions) > 3 else ""
        )
        return ", ".join(parts) + suffix

    def to_dict(self) -> dict[str, float]:
        return dict(self.weights)


@dataclass(frozen=True)
class HorizonPrediction:
    """Aggregated prediction for a single time horizon."""
    horizon: str
    expected: float
    min_return: float
    max_return: float
    std: float
    n_samples: int

    @property
    def confidence_label(self) -> str:
        if self.n_samples >= 8:
            return "High"
        if self.n_samples >= 4:
            return "Medium"
        return "Low"

    @property
    def confidence_color(self) -> str:
        if self.n_samples >= 8:
            return "#00F5A0"
        if self.n_samples >= 4:
            return "#FFB547"
        return "#FF3B6B"

    @classmethod
    def from_dict(cls, horizon: str, data: dict) -> HorizonPrediction:
        return cls(
            horizon=horizon,
            expected=float(data["expected"]),
            min_return=float(data["min"]),
            max_return=float(data["max"]),
            std=float(data["std"]),
            n_samples=int(data["n_samples"]),
        )


@dataclass(frozen=True)
class ScenarioResult:
    """Result of running a portfolio through a single stress scenario
    at a single time horizon."""
    event_id: str
    event_name: str
    horizon: str
    weighted_return: float
    total_weight_applied: float

    @property
    def horizon_label(self) -> str:
        return self.horizon.upper()

    @property
    def is_positive(self) -> bool:
        return self.weighted_return >= 0

    @property
    def color(self) -> str:
        return "#00F5A0" if self.is_positive else "#FF3B6B"
