"""Tests for the similarity engine.

Verifies that the weighted Euclidean distance calculation and event
ranking produce sensible results against known historical conditions.
All tests use synthetic or real event data without requiring a live
Streamlit runtime.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.similarity_engine import (
    calculate_similarity,
    find_similar_events,
    aggregate_impact_prediction,
)


# ---------------------------------------------------------------------------
# calculate_similarity
# ---------------------------------------------------------------------------

class TestCalculateSimilarity:

    def test_identical_conditions_returns_100(self):
        conditions = {
            "inflation": 3.8,
            "fed_funds_rate": 2.0,
            "unemployment": 6.1,
            "gdp_growth": -0.1,
        }
        score = calculate_similarity(conditions, conditions)
        assert score == 100.0

    def test_completely_different_conditions_returns_low_score(self):
        user = {
            "inflation": 0.0,
            "fed_funds_rate": 0.0,
            "unemployment": 2.0,
            "gdp_growth": 5.0,
        }
        event = {
            "inflation": 15.0,
            "fed_funds_rate": 20.0,
            "unemployment": 12.0,
            "gdp_growth": -10.0,
        }
        score = calculate_similarity(user, event)
        assert score < 30.0

    def test_score_is_between_0_and_100(self):
        user = {"inflation": 5.0, "fed_funds_rate": 3.0}
        event = {"inflation": 2.0, "fed_funds_rate": 18.0}
        score = calculate_similarity(user, event)
        assert 0.0 <= score <= 100.0

    def test_missing_fields_returns_zero(self):
        score = calculate_similarity({}, {})
        assert score == 0.0

    def test_partial_overlap_uses_available_fields(self):
        user = {"inflation": 3.0}
        event = {"inflation": 3.0, "fed_funds_rate": 5.0}
        score = calculate_similarity(user, event)
        assert score == 100.0

    def test_symmetry(self):
        a = {"inflation": 2.0, "fed_funds_rate": 1.0, "unemployment": 4.0}
        b = {"inflation": 5.0, "fed_funds_rate": 3.0, "unemployment": 6.0}
        assert calculate_similarity(a, b) == calculate_similarity(b, a)

    def test_custom_weights_shift_score(self):
        user = {"inflation": 10.0, "fed_funds_rate": 1.0}
        event = {"inflation": 1.0, "fed_funds_rate": 10.0}
        default = calculate_similarity(user, event)
        inflation_heavy = calculate_similarity(
            user, event,
            weights={"inflation": 5.0, "fed_funds_rate": 0.1,
                     "unemployment": 0.0, "gdp_growth": 0.0}
        )
        assert inflation_heavy != default

    def test_result_rounded_to_one_decimal(self):
        user = {"inflation": 3.5, "fed_funds_rate": 2.5}
        event = {"inflation": 4.0, "fed_funds_rate": 3.0}
        score = calculate_similarity(user, event)
        assert score == round(score, 1)


# ---------------------------------------------------------------------------
# find_similar_events
# ---------------------------------------------------------------------------

class TestFindSimilarEvents:

    def test_returns_list(self):
        conditions = {"inflation": 3.8, "fed_funds_rate": 2.0,
                      "unemployment": 6.1, "gdp_growth": -0.1}
        results = find_similar_events(conditions, top_n=5)
        assert isinstance(results, list)

    def test_respects_top_n(self):
        conditions = {"inflation": 3.0, "fed_funds_rate": 5.0}
        for n in (1, 3, 5):
            results = find_similar_events(conditions, top_n=n)
            assert len(results) <= n

    def test_results_sorted_descending(self):
        conditions = {"inflation": 3.0, "fed_funds_rate": 5.0,
                      "unemployment": 4.0, "gdp_growth": 2.0}
        results = find_similar_events(conditions, top_n=10)
        scores = [r["similarity"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_each_result_has_required_keys(self):
        conditions = {"inflation": 3.0, "fed_funds_rate": 5.0}
        results = find_similar_events(conditions, top_n=3)
        for r in results:
            assert "event" in r
            assert "similarity" in r
            assert "id" in r["event"]
            assert "name" in r["event"]

    def test_high_inflation_ranks_1973_oil_crisis_above_2020_covid(self):
        high_inflation = {
            "inflation": 12.0,
            "fed_funds_rate": 10.0,
            "unemployment": 6.0,
            "gdp_growth": -1.0,
        }
        results = find_similar_events(high_inflation, top_n=30)
        ids = [r["event"]["id"] for r in results]
        if "oil_crisis_1973" in ids and "covid_2020" in ids:
            assert ids.index("oil_crisis_1973") < ids.index("covid_2020"), (
                "High inflation conditions should rank 1973 Oil Crisis "
                "above COVID-19 pandemic"
            )

    def test_category_filter_restricts_results(self):
        conditions = {"inflation": 3.0, "fed_funds_rate": 5.0}
        all_results = find_similar_events(conditions, top_n=30)
        categories = {r["event"]["category"] for r in all_results}
        if len(categories) > 1:
            target = next(iter(categories))
            filtered = find_similar_events(
                conditions, event_category=target, top_n=30
            )
            assert all(
                r["event"]["category"] == target for r in filtered
            )

    def test_all_filter_returns_same_as_none(self):
        conditions = {"inflation": 3.0, "fed_funds_rate": 5.0}
        none_results = find_similar_events(conditions, top_n=30)
        all_results = find_similar_events(
            conditions, event_category="All", top_n=30
        )
        assert [r["event"]["id"] for r in none_results] == \
               [r["event"]["id"] for r in all_results]


# ---------------------------------------------------------------------------
# aggregate_impact_prediction
# ---------------------------------------------------------------------------

class TestAggregateImpactPrediction:

    def _get_similar_events(self):
        conditions = {"inflation": 3.8, "fed_funds_rate": 2.0,
                      "unemployment": 6.1, "gdp_growth": -0.1}
        return find_similar_events(conditions, top_n=5)

    def test_returns_dict_with_all_horizons(self):
        similar = self._get_similar_events()
        result = aggregate_impact_prediction(similar, "sp500")
        assert set(result.keys()) == {"1m", "3m", "6m", "1y", "2y"}

    def test_non_none_horizons_have_required_keys(self):
        similar = self._get_similar_events()
        result = aggregate_impact_prediction(similar, "sp500")
        for horizon, pred in result.items():
            if pred is not None:
                assert "expected" in pred
                assert "min" in pred
                assert "max" in pred
                assert "std" in pred
                assert "n_samples" in pred

    def test_min_lte_expected_lte_max(self):
        similar = self._get_similar_events()
        result = aggregate_impact_prediction(similar, "sp500")
        for pred in result.values():
            if pred is not None:
                assert pred["min"] <= pred["expected"] <= pred["max"], (
                    f"Expected {pred['expected']} not between "
                    f"{pred['min']} and {pred['max']}"
                )

    def test_std_is_non_negative(self):
        similar = self._get_similar_events()
        result = aggregate_impact_prediction(similar, "gold")
        for pred in result.values():
            if pred is not None:
                assert pred["std"] >= 0.0

    def test_n_samples_matches_number_of_contributing_events(self):
        similar = self._get_similar_events()
        result = aggregate_impact_prediction(similar, "sp500")
        for pred in result.values():
            if pred is not None:
                assert 1 <= pred["n_samples"] <= len(similar)

    def test_unknown_asset_returns_all_none(self):
        similar = self._get_similar_events()
        result = aggregate_impact_prediction(similar, "nonexistent_asset_xyz")
        assert all(v is None for v in result.values())

    def test_empty_similar_events_returns_all_none(self):
        result = aggregate_impact_prediction([], "sp500")
        assert all(v is None for v in result.values())

    def test_sp500_negative_during_crisis_conditions(self):
        crisis_conditions = {
            "inflation": 3.8,
            "fed_funds_rate": 2.0,
            "unemployment": 6.1,
            "gdp_growth": -0.1,
        }
        similar = find_similar_events(crisis_conditions, top_n=5)
        result = aggregate_impact_prediction(similar, "sp500")
        one_year = result.get("1y")
        if one_year is not None:
            assert one_year["expected"] < 0, (
                "S&P 500 should show negative expected return at 1Y "
                "under GFC-like crisis conditions"
            )

    def test_gold_positive_during_crisis_conditions(self):
        crisis_conditions = {
            "inflation": 3.8,
            "fed_funds_rate": 2.0,
            "unemployment": 6.1,
            "gdp_growth": -0.1,
        }
        similar = find_similar_events(crisis_conditions, top_n=5)
        result = aggregate_impact_prediction(similar, "gold")
        one_year = result.get("1y")
        if one_year is not None:
            assert one_year["expected"] > 0, (
                "Gold should show positive expected return at 1Y "
                "under crisis conditions due to flight-to-quality"
            )
