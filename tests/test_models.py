"""Tests for domain model dataclasses."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import (
    Event, AssetImpact, Portfolio, ScenarioResult,
    MacroConditions, HorizonPrediction,
)


class TestMacroConditions:

    def test_from_dict_partial(self):
        data = {"inflation": 3.5, "fed_funds_rate": 2.0}
        mc = MacroConditions.from_dict(data)
        assert mc.inflation == 3.5
        assert mc.unemployment is None

    def test_to_dict_excludes_none(self):
        mc = MacroConditions(inflation=3.5, fed_funds_rate=2.0)
        d = mc.to_dict()
        assert "inflation" in d
        assert "unemployment" not in d

    def test_roundtrip(self):
        data = {"inflation": 3.5, "fed_funds_rate": 2.0,
                "unemployment": 4.0, "gdp_growth": 2.5}
        mc = MacroConditions.from_dict(data)
        assert mc.to_dict() == data


class TestEvent:

    def _sample_dict(self):
        return {
            "id": "gfc_2008",
            "name": "Global Financial Crisis",
            "year": 2008,
            "start_date": "2008-09-15",
            "end_date": "2009-03-09",
            "category": "Financial Crisis",
            "severity": 10,
            "duration_months": 18,
            "geography": "Global",
            "description": "Collapse of Lehman Brothers.",
            "triggers": ["Housing bubble", "Lehman collapse"],
            "pre_conditions": {
                "inflation": 3.8,
                "fed_funds_rate": 2.0,
                "unemployment": 6.1,
                "gdp_growth": -0.1,
            },
        }

    def test_from_dict_parses_correctly(self):
        e = Event.from_dict(self._sample_dict())
        assert e.id == "gfc_2008"
        assert e.severity == 10
        assert e.year == 2008
        assert isinstance(e.triggers, tuple)
        assert isinstance(e.pre_conditions, MacroConditions)

    def test_invalid_severity_raises(self):
        data = self._sample_dict()
        data["severity"] = 11
        with pytest.raises(ValueError):
            Event.from_dict(data)

    def test_invalid_duration_raises(self):
        data = self._sample_dict()
        data["duration_months"] = 0
        with pytest.raises(ValueError):
            Event.from_dict(data)

    def test_roundtrip(self):
        data = self._sample_dict()
        e = Event.from_dict(data)
        result = e.to_dict()
        assert result["id"] == data["id"]
        assert result["severity"] == data["severity"]
        assert result["triggers"] == data["triggers"]


class TestAssetImpact:

    def test_from_dict_parses_horizons(self):
        data = {"1m": -16.9, "3m": -29.3, "6m": -36.3, "1y": -43.3, "2y": -18.5}
        ai = AssetImpact.from_dict("sp500", data)
        assert ai.get("1m") == -16.9
        assert ai.get("2y") == -18.5

    def test_get_missing_horizon_returns_none(self):
        ai = AssetImpact.from_dict("sp500", {"1m": -10.0})
        assert ai.get("2y") is None

    def test_has_data_true_when_values_present(self):
        ai = AssetImpact.from_dict("sp500", {"1m": -10.0})
        assert ai.has_data is True

    def test_has_data_false_when_all_none(self):
        ai = AssetImpact.from_dict("sp500", {"1m": None, "3m": None})
        assert ai.has_data is False

    def test_coverage_calculation(self):
        ai = AssetImpact.from_dict("sp500", {"1m": -10.0, "3m": None})
        assert ai.coverage == 0.5


class TestPortfolio:

    def test_valid_portfolio(self):
        p = Portfolio(weights={"sp500": 60.0, "us_10y_treasury": 40.0})
        assert p.is_valid is True

    def test_invalid_portfolio_not_100(self):
        p = Portfolio(weights={"sp500": 60.0, "us_10y_treasury": 30.0})
        assert p.is_valid is False

    def test_fractions_sum_to_1(self):
        p = Portfolio(weights={"sp500": 60.0, "us_10y_treasury": 40.0})
        assert abs(sum(p.fractions.values()) - 1.0) < 1e-6

    def test_active_positions_excludes_zero(self):
        p = Portfolio(weights={"sp500": 60.0, "gold": 0.0,
                               "us_10y_treasury": 40.0})
        assert "gold" not in p.active_positions

    def test_position_count(self):
        p = Portfolio(weights={"sp500": 60.0, "gold": 0.0,
                               "us_10y_treasury": 40.0})
        assert p.position_count == 2

    def test_summary_shows_top_3(self):
        labels = {"sp500": "S&P 500", "gold": "Gold",
                  "us_10y_treasury": "US 10Y", "bitcoin": "Bitcoin"}
        p = Portfolio(weights={"sp500": 40.0, "gold": 30.0,
                               "us_10y_treasury": 20.0, "bitcoin": 10.0})
        summary = p.summary(labels)
        assert "more" in summary
        assert "S&P 500" in summary


class TestHorizonPrediction:

    def test_confidence_label_high(self):
        hp = HorizonPrediction(
            horizon="1y", expected=-10.0, min_return=-30.0,
            max_return=5.0, std=8.0, n_samples=10
        )
        assert hp.confidence_label == "High"
        assert hp.confidence_color == "#00F5A0"

    def test_confidence_label_medium(self):
        hp = HorizonPrediction(
            horizon="1y", expected=-10.0, min_return=-30.0,
            max_return=5.0, std=8.0, n_samples=5
        )
        assert hp.confidence_label == "Medium"
        assert hp.confidence_color == "#FFB547"

    def test_confidence_label_low(self):
        hp = HorizonPrediction(
            horizon="1y", expected=-10.0, min_return=-30.0,
            max_return=5.0, std=8.0, n_samples=2
        )
        assert hp.confidence_label == "Low"
        assert hp.confidence_color == "#FF3B6B"

    def test_from_dict(self):
        data = {"expected": -10.0, "min": -30.0, "max": 5.0,
                "std": 8.0, "n_samples": 7}
        hp = HorizonPrediction.from_dict("1y", data)
        assert hp.horizon == "1y"
        assert hp.expected == -10.0
