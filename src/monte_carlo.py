"""Monte Carlo simulation engine for MacroLens.

Samples from the distribution of similar historical events to produce
a return distribution rather than a point estimate. The raw simulated
array is never stored in a dataclass field to avoid Streamlit Arrow
serialization issues. Only computed statistics are stored.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class MonteCarloResult:
    """Computed statistics from a Monte Carlo simulation.

    Raw simulated returns are not stored here. They are returned
    separately from run_monte_carlo as a plain Python list.
    """
    asset_class: str
    horizon: str
    n_simulations: int
    n_historical_analogs: int
    expected: float
    std: float
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    percentile_10: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    percentile_90: float
    prob_positive: float
    prob_loss_10pct: float
    prob_loss_20pct: float


def _compute_stats(
    asset_class: str,
    horizon: str,
    returns: np.ndarray,
    n_historical: int,
) -> MonteCarloResult:
    sorted_r = np.sort(returns)
    var_95 = float(np.percentile(returns, 5))
    var_99 = float(np.percentile(returns, 1))
    tail_95 = sorted_r[sorted_r <= var_95]
    tail_99 = sorted_r[sorted_r <= var_99]
    cvar_95 = float(tail_95.mean()) if len(tail_95) > 0 else var_95
    cvar_99 = float(tail_99.mean()) if len(tail_99) > 0 else var_99

    return MonteCarloResult(
        asset_class=asset_class,
        horizon=horizon,
        n_simulations=len(returns),
        n_historical_analogs=n_historical,
        expected=round(float(returns.mean()), 2),
        std=round(float(returns.std()), 2),
        var_95=round(var_95, 2),
        var_99=round(var_99, 2),
        cvar_95=round(cvar_95, 2),
        cvar_99=round(cvar_99, 2),
        percentile_10=round(float(np.percentile(returns, 10)), 2),
        percentile_25=round(float(np.percentile(returns, 25)), 2),
        percentile_50=round(float(np.percentile(returns, 50)), 2),
        percentile_75=round(float(np.percentile(returns, 75)), 2),
        percentile_90=round(float(np.percentile(returns, 90)), 2),
        prob_positive=round(float((returns > 0).mean() * 100), 1),
        prob_loss_10pct=round(float((returns < -10).mean() * 100), 1),
        prob_loss_20pct=round(float((returns < -20).mean() * 100), 1),
    )


def run_monte_carlo(
    prediction: dict,
    asset_class: str,
    horizon: str,
    n_simulations: int = 10000,
    random_seed: int = 42,
) -> tuple[MonteCarloResult, list[float]] | tuple[None, None]:
    """Run Monte Carlo simulation for a single asset at a single horizon.

    Returns (MonteCarloResult, simulated_returns_list) or (None, None).
    The simulated returns are returned as a plain Python list of floats
    to avoid Arrow serialization issues when passed to Plotly or Streamlit.
    """
    if prediction is None:
        return None, None

    expected = prediction["expected"]
    std = prediction["std"]
    n_historical = prediction["n_samples"]

    if std <= 0:
        return None, None

    rng = np.random.default_rng(random_seed)

    if n_historical >= 8:
        low = prediction["min"]
        high = prediction["max"]
        historical_points = np.linspace(low, high, n_historical)
        noise = rng.normal(0, std * 0.3, size=n_simulations)
        bootstrap_idx = rng.integers(0, n_historical, size=n_simulations)
        simulated = historical_points[bootstrap_idx] + noise
    else:
        simulated = rng.normal(expected, std, size=n_simulations)

    result = _compute_stats(asset_class, horizon, simulated, n_historical)
    return result, [float(v) for v in simulated]
