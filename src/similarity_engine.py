"""Pattern matching engine for MacroLens.

Identifies historical events whose pre-conditions most closely resemble
a user-supplied or current macroeconomic state. Uses a weighted Euclidean
distance over normalized macro features, converted to a similarity score
on a 0 to 100 scale.
"""
from __future__ import annotations

from typing import Any, TypedDict

import numpy as np

from src.constants import HORIZONS
from src.data_loader import load_events, load_impacts


_FEATURES: tuple[str, ...] = (
    "inflation", "fed_funds_rate", "unemployment", "gdp_growth",
)

_DEFAULT_WEIGHTS: dict[str, float] = {
    "inflation": 1.0,
    "fed_funds_rate": 1.0,
    "unemployment": 0.8,
    "gdp_growth": 1.0,
}

_FEATURE_RANGES: dict[str, float] = {
    "inflation": 15.0,
    "fed_funds_rate": 20.0,
    "unemployment": 12.0,
    "gdp_growth": 10.0,
}


class SimilarEvent(TypedDict):
    """Result row from find_similar_events."""
    event: dict[str, Any]
    similarity: float


class HorizonPrediction(TypedDict):
    """Aggregated prediction for a single time horizon."""
    expected: float
    min: float
    max: float
    std: float
    n_samples: int


def calculate_similarity(
    user_conditions: dict[str, float | None],
    event_conditions: dict[str, float | None],
    weights: dict[str, float] | None = None,
) -> float:
    """Calculate similarity between user scenario and historical event.

    Uses weighted Euclidean distance on normalized macro features,
    converted to a 0 to 100 similarity score (higher means more similar).

    Args:
        user_conditions: Mapping of macro feature names to current values.
        event_conditions: Mapping of macro feature names to historical values.
        weights: Optional per-feature weights. Defaults to the module-level
            weighting that prioritizes inflation, rates, and growth over
            unemployment.

    Returns:
        Similarity score in [0, 100], rounded to one decimal place.
    """
    feature_weights = weights if weights is not None else _DEFAULT_WEIGHTS

    distance = 0.0
    total_weight = 0.0
    for feature in _FEATURES:
        user_val = user_conditions.get(feature)
        event_val = event_conditions.get(feature)
        if user_val is None or event_val is None:
            continue
        normalized_diff = abs(user_val - event_val) / _FEATURE_RANGES[feature]
        weight = feature_weights[feature]
        distance += weight * normalized_diff ** 2
        total_weight += weight

    if total_weight == 0:
        return 0.0

    distance = float(np.sqrt(distance / total_weight))
    similarity = max(0.0, 100.0 * (1.0 - distance))
    return round(similarity, 1)


def find_similar_events(
    user_conditions: dict[str, float | None],
    event_category: str | None = None,
    top_n: int = 5,
) -> list[SimilarEvent]:
    """Find the most similar historical events based on macro conditions.

    Args:
        user_conditions: Current or hypothetical macro state.
        event_category: Optional category filter. Pass None or "All" to
            consider every event.
        top_n: Maximum number of results to return.

    Returns:
        List of dicts each containing the matched event and its similarity
        score, sorted in descending order of similarity.
    """
    events = load_events()
    if event_category and event_category != "All":
        events = [e for e in events if e["category"] == event_category]

    results: list[SimilarEvent] = [
        {
            "event": event,
            "similarity": calculate_similarity(
                user_conditions, event["pre_conditions"]
            ),
        }
        for event in events
    ]
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_n]


def aggregate_impact_prediction(
    similar_events: list[SimilarEvent],
    asset_class: str,
) -> dict[str, HorizonPrediction | None]:
    """Create a similarity-weighted prediction across multiple horizons.

    For each horizon, the expected return is the similarity-weighted mean
    of the matched events' actual returns for the given asset class. The
    min, max, and std are computed unweighted to give a sense of the raw
    dispersion across analogs.

    Args:
        similar_events: Output of find_similar_events.
        asset_class: Asset ID to predict (e.g. "sp500", "us_10y_treasury").

    Returns:
        Mapping of horizon code to prediction dict, or None for that
        horizon if no historical analog had data for it.
    """
    impacts = load_impacts()
    predictions: dict[str, HorizonPrediction | None] = {}

    for horizon in HORIZONS:
        values: list[float] = []
        weights: list[float] = []

        for item in similar_events:
            event_id = item["event"]["id"]
            event_impacts = impacts.get(event_id)
            if event_impacts is None:
                continue
            asset_impacts = event_impacts.get(asset_class)
            if asset_impacts is None:
                continue
            value = asset_impacts.get(horizon)
            if value is None:
                continue
            values.append(value)
            weights.append(item["similarity"])

        if not values:
            predictions[horizon] = None
            continue

        values_arr = np.asarray(values, dtype=float)
        weights_arr = np.asarray(weights, dtype=float)
        weight_sum = weights_arr.sum()
        weighted_mean = (
            float((values_arr * weights_arr).sum() / weight_sum)
            if weight_sum > 0
            else float(values_arr.mean())
        )

        predictions[horizon] = {
            "expected": round(weighted_mean, 2),
            "min": round(float(values_arr.min()), 2),
            "max": round(float(values_arr.max()), 2),
            "std": round(float(values_arr.std()), 2),
            "n_samples": len(values),
        }

    return predictions
