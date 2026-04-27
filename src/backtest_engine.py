"""
Backtest engine: runs MacroLens analysis as if it were any historical date,
using only events that occurred before that date.
"""
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import streamlit as st

from src.data_loader import load_events
from src.similarity_engine import calculate_similarity, aggregate_impact_prediction
from src.historical_fetcher import fetch_price_series, calculate_horizon_returns
from src.ticker_mapping import get_ticker


def get_events_before_date(target_date_str):
    """Return only events that started before the target date."""
    target = datetime.strptime(target_date_str, "%Y-%m-%d")
    events = load_events()
    return [e for e in events if datetime.strptime(e["start_date"], "%Y-%m-%d") < target]


def find_similar_events_at_date(user_conditions, target_date_str, top_n=5, category=None):
    """Find similar events using only those that happened before target date."""
    available_events = get_events_before_date(target_date_str)

    if category and category != "All":
        available_events = [e for e in available_events if e["category"] == category]

    results = []
    for event in available_events:
        sim = calculate_similarity(user_conditions, event["pre_conditions"])
        results.append({"event": event, "similarity": sim})

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_n]


@st.cache_data(ttl=3600)
def fetch_actual_returns(asset_id, target_date_str):
    """Fetch what actually happened to an asset starting from target_date."""
    ticker = get_ticker(asset_id, target_date_str)
    if not ticker:
        return None

    target = datetime.strptime(target_date_str, "%Y-%m-%d")
    fetch_end = (target + timedelta(days=800)).strftime("%Y-%m-%d")

    price_data = fetch_price_series(ticker, target_date_str, fetch_end)
    if price_data is None or price_data.empty:
        return None

    returns = calculate_horizon_returns(price_data, target_date_str, ticker)
    return returns


def run_backtest(user_conditions, target_date_str, asset_ids, top_n=5, category=None):
    """
    Full backtest: predict using only past events, then compare to what actually happened.
    Returns dict with predictions, actuals, errors, and accuracy metrics.
    """
    # Find similar events (only those before target date)
    similar = find_similar_events_at_date(user_conditions, target_date_str, top_n, category)

    if not similar:
        return None

    results = {
        "target_date": target_date_str,
        "similar_events": similar,
        "assets": {},
    }

    for asset_id in asset_ids:
        # Generate prediction
        prediction = aggregate_impact_prediction(similar, asset_id)
        # Fetch actual returns
        actual = fetch_actual_returns(asset_id, target_date_str)

        asset_result = {
            "predicted": {},
            "actual": {},
            "error": {},
            "direction_correct": {},
        }

        for horizon in ["1m", "3m", "6m", "1y", "2y"]:
            pred_val = prediction.get(horizon, {}).get("expected") if prediction.get(horizon) else None
            actual_val = actual.get(horizon) if actual else None

            asset_result["predicted"][horizon] = pred_val
            asset_result["actual"][horizon] = actual_val

            if pred_val is not None and actual_val is not None:
                asset_result["error"][horizon] = round(actual_val - pred_val, 2)
                # Direction correct if both same sign or both close to zero
                pred_dir = 1 if pred_val > 1 else (-1 if pred_val < -1 else 0)
                actual_dir = 1 if actual_val > 1 else (-1 if actual_val < -1 else 0)
                asset_result["direction_correct"][horizon] = (pred_dir == actual_dir)
            else:
                asset_result["error"][horizon] = None
                asset_result["direction_correct"][horizon] = None

        results["assets"][asset_id] = asset_result

    # Calculate aggregate metrics
    all_errors = []
    direction_hits = 0
    direction_total = 0
    for asset_id, data in results["assets"].items():
        for h, err in data["error"].items():
            if err is not None:
                all_errors.append(abs(err))
            d = data["direction_correct"][h]
            if d is not None:
                direction_total += 1
                if d:
                    direction_hits += 1

    results["metrics"] = {
        "mean_absolute_error": round(np.mean(all_errors), 2) if all_errors else None,
        "median_absolute_error": round(np.median(all_errors), 2) if all_errors else None,
        "direction_accuracy": round((direction_hits / direction_total) * 100, 1) if direction_total > 0 else None,
        "n_predictions": len(all_errors),
        "n_direction_correct": direction_hits,
        "n_direction_total": direction_total,
    }

    return results


def calculate_asset_accuracy(asset_result):
    """Calculate accuracy for a single asset."""
    errors = [e for e in asset_result["error"].values() if e is not None]
    directions = [d for d in asset_result["direction_correct"].values() if d is not None]

    return {
        "mae": round(np.mean([abs(e) for e in errors]), 2) if errors else None,
        "direction_pct": round(sum(directions) / len(directions) * 100, 1) if directions else None,
        "n_horizons": len(errors),
    }