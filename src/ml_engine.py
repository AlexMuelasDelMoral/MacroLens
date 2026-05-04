"""ML engine for MacroLens.

Provides scenario-based impact estimation using a small-data-safe
Gradient Boosting model. scikit-learn is imported lazily inside
train_model() so it does not contribute to cold-start time on pages
that do not invoke ML predictions.
"""
from __future__ import annotations

import numpy as np

from src.data_loader import load_events, load_impacts
from src.constants import HORIZONS


def prepare_training_data(
    asset_class: str,
    horizon: str = "3m",
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Prepare training data from historical macro events.

    Returns:
        X: Feature matrix of shape (n_samples, 6).
        y: Target impact values of shape (n_samples,).
        event_names: Event name labels aligned with X and y rows.
    """
    events = load_events()
    impacts = load_impacts()

    X: list[list[float]] = []
    y: list[float] = []
    event_names: list[str] = []

    required = ("inflation", "fed_funds_rate", "unemployment", "gdp_growth")

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
        if any(pre.get(k) is None for k in required):
            continue

        X.append([
            pre["inflation"],
            pre["fed_funds_rate"],
            pre["unemployment"],
            pre["gdp_growth"],
            event["severity"],
            event["duration_months"],
        ])
        y.append(target)
        event_names.append(event["name"])

    return np.array(X), np.array(y), event_names


def train_model(
    asset_class: str,
    horizon: str = "3m",
) -> tuple:
    """Train a Gradient Boosting model for a given asset and horizon.

    scikit-learn is imported here rather than at module level to avoid
    paying the import cost on pages that never call this function.

    Returns:
        (model, scaler) on success, or (None, None) if fewer than five
        training samples are available.
    """
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler

    X, y, _ = prepare_training_data(asset_class, horizon)
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


def predict_with_ml(
    user_conditions: dict[str, float],
    asset_class: str,
    horizon: str = "3m",
    severity: float = 7,
    duration: float = 6,
) -> dict | None:
    """ML-based impact estimate for a single horizon.

    Returns a result dict on success, or None if insufficient training data.
    """
    model, scaler = train_model(asset_class, horizon)
    if model is None:
        return None

    features = np.array([[
        user_conditions.get("inflation", 3.0),
        user_conditions.get("fed_funds_rate", 5.0),
        user_conditions.get("unemployment", 4.0),
        user_conditions.get("gdp_growth", 2.0),
        severity,
        duration,
    ]])
    prediction = float(model.predict(scaler.transform(features))[0])

    X, _, _ = prepare_training_data(asset_class, horizon)
    return {
        "prediction": round(prediction, 2),
        "feature_importances": dict(zip(
            ("Inflation", "Fed Rate", "Unemployment",
             "GDP Growth", "Severity", "Duration"),
            model.feature_importances_,
        )),
        "n_training_samples": len(X),
        "model_type": "Gradient Boosting",
    }


def get_ml_predictions_all_horizons(
    user_conditions: dict[str, float],
    asset_class: str,
    severity: float = 7,
    duration: float = 6,
) -> dict[str, dict | None]:
    """Run ML estimates across all standard time horizons."""
    return {
        horizon: predict_with_ml(
            user_conditions, asset_class,
            horizon=horizon, severity=severity, duration=duration,
        )
        for horizon in HORIZONS
    }


def compare_models(
    user_conditions: dict[str, float],
    asset_class: str,
    similar_events: list,
    severity: float = 7,
    duration: float = 6,
) -> dict[str, dict]:
    """Compare similarity-based estimates versus ML estimates per horizon."""
    from src.similarity_engine import aggregate_impact_prediction

    similarity_pred = aggregate_impact_prediction(similar_events, asset_class)
    ml_pred = get_ml_predictions_all_horizons(
        user_conditions, asset_class, severity, duration,
    )

    return {
        horizon: {
            "similarity": (
                similarity_pred[horizon]["expected"]
                if similarity_pred.get(horizon) else None
            ),
            "ml": (
                ml_pred[horizon]["prediction"]
                if ml_pred.get(horizon) else None
            ),
        }
        for horizon in HORIZONS
    }

def get_shap_explanation(
    user_conditions: dict[str, float],
    asset_class: str,
    horizon: str = "3m",
    severity: float = 7,
    duration: float = 6,
) -> dict | None:
    """Compute SHAP values explaining a single ML prediction.

    Returns a dict with feature names, their SHAP values, the base value,
    and the final prediction. Returns None if insufficient training data.

    SHAP is imported lazily here because it is large and only needed
    when this function is called from the Model Comparison tab.
    """
    import shap

    model, scaler = train_model(asset_class, horizon)
    if model is None:
        return None

    X, y, event_names = prepare_training_data(asset_class, horizon)

    features = np.array([[
        user_conditions.get("inflation", 3.0),
        user_conditions.get("fed_funds_rate", 5.0),
        user_conditions.get("unemployment", 4.0),
        user_conditions.get("gdp_growth", 2.0),
        severity,
        duration,
    ]])

    features_scaled = scaler.transform(features)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(features_scaled)

    feature_names = [
        "Inflation",
        "Fed Rate",
        "Unemployment",
        "GDP Growth",
        "Severity",
        "Duration",
    ]

    prediction = float(model.predict(features_scaled)[0])
    base_value = float(explainer.expected_value)

    return {
        "feature_names": feature_names,
        "shap_values": shap_values[0].tolist(),
        "base_value": base_value,
        "prediction": round(prediction, 2),
        "asset_class": asset_class,
        "horizon": horizon,
        "n_training_samples": len(X),
    }

def run_cross_validation(
    asset_class: str,
    horizon: str = "3m",
    n_splits: int = 5,
) -> dict | None:
    """Run leave-one-out style cross-validation for a given asset and horizon.

    Uses KFold with shuffle disabled to respect temporal ordering.
    Returns MAE, RMSE, direction accuracy, and per-fold details.
    Returns None if fewer than five training samples exist.
    """
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import KFold

    X, y, event_names = prepare_training_data(asset_class, horizon)
    if len(X) < n_splits:
        return None

    kf = KFold(n_splits=n_splits, shuffle=False)
    mae_scores: list[float] = []
    rmse_scores: list[float] = []
    direction_correct: list[bool] = []
    fold_details: list[dict] = []

    for fold, (train_idx, test_idx) in enumerate(kf.split(X), start=1):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        model = GradientBoostingRegressor(
            n_estimators=150,
            max_depth=3,
            learning_rate=0.05,
            random_state=42,
        )
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)

        fold_mae = float(np.mean(np.abs(preds - y_test)))
        fold_rmse = float(np.sqrt(np.mean((preds - y_test) ** 2)))
        fold_dir = [
            (float(p) >= 0) == (float(a) >= 0)
            for p, a in zip(preds, y_test)
        ]

        mae_scores.append(fold_mae)
        rmse_scores.append(fold_rmse)
        direction_correct.extend(fold_dir)

        for name, pred, actual in zip(
            [event_names[i] for i in test_idx], preds, y_test
        ):
            fold_details.append({
                "fold": fold,
                "event": name,
                "predicted": round(float(pred), 2),
                "actual": round(float(actual), 2),
                "error": round(abs(float(pred) - float(actual)), 2),
                "direction_correct": (float(pred) >= 0) == (float(actual) >= 0),
            })

    return {
        "asset_class": asset_class,
        "horizon": horizon,
        "n_samples": len(X),
        "n_splits": n_splits,
        "mae": round(float(np.mean(mae_scores)), 2),
        "mae_std": round(float(np.std(mae_scores)), 2),
        "rmse": round(float(np.mean(rmse_scores)), 2),
        "direction_accuracy": round(
            sum(direction_correct) / len(direction_correct) * 100, 1
        ),
        "fold_details": fold_details,
    }


def run_cross_validation_suite(
    assets: list[str] | None = None,
    horizon: str = "3m",
) -> list[dict]:
    """Run cross-validation across multiple assets for a single horizon.

    Returns a list of result dicts sorted by MAE ascending so the best
    performing assets appear first.
    """
    if assets is None:
        assets = ["sp500", "gold", "us_10y_treasury", "bitcoin", "oil_wti"]

    results = []
    for asset in assets:
        result = run_cross_validation(asset, horizon)
        if result is not None:
            results.append(result)

    return sorted(results, key=lambda x: x["mae"])