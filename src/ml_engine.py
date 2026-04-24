"""
ML engine for MacroLens.
Purpose: scenario-based impact estimation (NOT prediction).
Uses small-data-safe Gradient Boosting.
"""

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor

from src.data_loader import load_events, load_impacts


# -------------------------------------------------
# TRAINING DATA PREPARATION
# -------------------------------------------------
def prepare_training_data(asset_class, horizon="3m"):
    """
    Prepare training data from historical macro events.

    Returns:
        X: feature matrix
        y: target impacts
        event_names: reference labels (for debugging)
    """
    events = load_events()
    impacts = load_impacts()

    X, y, event_names = [], [], []

    for event in events:
        event_id = event["id"]

        if event_id not in impacts:
            continue
        if asset_class not in impacts[event_id]:
            continue

        target = impacts[event_id][asset_class].get(horizon)
        if target is None:
            continue

        pre = event["pre_conditions"]
        required = ["inflation", "fed_funds_rate", "unemployment", "gdp_growth"]
        if any(pre.get(k) is None for k in required):
            continue

        features = [
            pre["inflation"],
            pre["fed_funds_rate"],
            pre["unemployment"],
            pre["gdp_growth"],
            event["severity"],
            event["duration_months"],
        ]

        X.append(features)
        y.append(target)
        event_names.append(event["name"])

    return np.array(X), np.array(y), event_names


# -------------------------------------------------
# MODEL TRAINING
# -------------------------------------------------
def train_model(asset_class, horizon="3m"):
    """
    Train a Gradient Boosting model for a given asset/horizon.
    Returns (model, scaler) or (None, None) if insufficient data.
    """
    X, y, _ = prepare_training_data(asset_class, horizon)

    # Guardrail: small data safety
    if len(X) < 5:
        return None, None

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = GradientBoostingRegressor(
        n_estimators=150,
        max_depth=3,
        learning_rate=0.05,
        random_state=42,
    )
    model.fit(X_scaled, y)

    return model, scaler


# -------------------------------------------------
# SINGLE SCENARIO PREDICTION
# -------------------------------------------------
def predict_with_ml(user_conditions, asset_class, horizon="3m",
                    severity=7, duration=6):
    """
    ML-based impact estimate for one horizon.
    """
    model, scaler = train_model(asset_class, horizon)
    if model is None:
        return None

    # Default values protect against missing user inputs
    features = np.array([[
        user_conditions.get("inflation", 3.0),
        user_conditions.get("fed_funds_rate", 5.0),
        user_conditions.get("unemployment", 4.0),
        user_conditions.get("gdp_growth", 2.0),
        severity,
        duration,
    ]])

    features_scaled = scaler.transform(features)
    prediction = float(model.predict(features_scaled)[0])

    feature_importances = dict(zip(
        ["Inflation", "Fed Rate", "Unemployment",
         "GDP Growth", "Severity", "Duration"],
        model.feature_importances_,
    ))

    X, _, _ = prepare_training_data(asset_class, horizon)

    return {
        "prediction": round(prediction, 2),
        "feature_importances": feature_importances,
        "n_training_samples": len(X),
        "model_type": "Gradient Boosting",
    }


# -------------------------------------------------
# MULTI-HORIZON PREDICTION
# -------------------------------------------------
def get_ml_predictions_all_horizons(user_conditions, asset_class,
                                    severity=7, duration=6):
    """
    Run ML estimates across standard time horizons.
    """
    horizons = ["1m", "3m", "6m", "1y", "2y"]
    results = {}

    for horizon in horizons:
        results[horizon] = predict_with_ml(
            user_conditions,
            asset_class,
            horizon=horizon,
            severity=severity,
            duration=duration,
        )

    return results


# -------------------------------------------------
# COMPARISON WITH SIMILARITY ENGINE
# -------------------------------------------------
def compare_models(user_conditions, asset_class, similar_events,
                   severity=7, duration=6):
    """
    Compare similarity-based estimates vs ML estimates.
    """
    from src.similarity_engine import aggregate_impact_prediction

    similarity_pred = aggregate_impact_prediction(similar_events, asset_class)
    ml_pred = get_ml_predictions_all_horizons(
        user_conditions, asset_class, severity, duration
    )

    comparison = {}

    for horizon in ["1m", "3m", "6m", "1y", "2y"]:
        comparison[horizon] = {
            "similarity": (
                similarity_pred[horizon]["expected"]
                if similarity_pred and horizon in similarity_pred
                else None
            ),
            "ml": (
                ml_pred[horizon]["prediction"]
                if ml_pred.get(horizon)
                else None
            ),
        }

    return comparison