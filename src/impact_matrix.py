"""Precomputed impact tensor for vectorized stress test computation.

Builds a NumPy array of shape (n_events, n_horizons, n_assets) from the
nested impacts dict returned by load_impacts(). Once built and cached, a
full stress test across all events and horizons is a single matrix
multiply rather than thousands of Python dictionary lookups.

Typical usage:
    matrix = build_impact_matrix()
    results = compute_portfolio_returns(matrix, portfolio_weights)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import streamlit as st

from src.constants import HORIZONS, DEFAULT_CACHE_TTL_SECONDS
from src.data_loader import load_impacts, ASSET_LABELS


@dataclass(frozen=True)
class ImpactMatrix:
    """Precomputed impact data in array form.

    Attributes:
        tensor:      Float array of shape (n_events, n_horizons, n_assets).
                     NaN where no data exists for that combination.
        event_ids:   Ordered list of event IDs matching axis 0.
        horizon_idx: Mapping of horizon code to axis-1 index.
        asset_idx:   Mapping of asset_id to axis-2 index.
        asset_ids:   Ordered list of asset IDs matching axis 2.
    """
    tensor: np.ndarray
    event_ids: tuple[str, ...]
    horizon_idx: dict[str, int]
    asset_idx: dict[str, int]
    asset_ids: tuple[str, ...]


@st.cache_data(ttl=DEFAULT_CACHE_TTL_SECONDS, show_spinner=False)
def build_impact_matrix() -> ImpactMatrix:
    """Build and cache the impact tensor from the loaded impacts data.

    Called once per session. Subsequent calls within the cache TTL are
    free. The tensor uses float32 to halve memory versus float64 with no
    meaningful precision loss for percentage returns.
    """
    impacts = load_impacts()

    event_ids = tuple(impacts.keys())
    asset_ids = tuple(ASSET_LABELS.keys())
    horizon_idx = {h: i for i, h in enumerate(HORIZONS)}
    asset_idx = {a: i for i, a in enumerate(asset_ids)}

    n_events = len(event_ids)
    n_horizons = len(HORIZONS)
    n_assets = len(asset_ids)

    tensor = np.full(
        (n_events, n_horizons, n_assets),
        fill_value=np.nan,
        dtype=np.float32,
    )

    for e_idx, event_id in enumerate(event_ids):
        event_impacts = impacts[event_id]
        for asset_id, horizon_data in event_impacts.items():
            a_idx = asset_idx.get(asset_id)
            if a_idx is None:
                continue
            for horizon, value in horizon_data.items():
                h_idx = horizon_idx.get(horizon)
                if h_idx is None or value is None:
                    continue
                tensor[e_idx, h_idx, a_idx] = value

    return ImpactMatrix(
        tensor=tensor,
        event_ids=event_ids,
        horizon_idx=horizon_idx,
        asset_idx=asset_idx,
        asset_ids=asset_ids,
    )


def compute_portfolio_returns(
    matrix: ImpactMatrix,
    portfolio_weights: dict[str, float],
    selected_event_ids: Sequence[str],
) -> dict[str, dict[str, float]]:
    """Compute weighted portfolio returns for selected events and all horizons.

    Args:
        matrix: Precomputed ImpactMatrix from build_impact_matrix().
        portfolio_weights: Mapping of asset_id to weight as a fraction
            summing to 1.0. Assets not in the matrix are ignored.
        selected_event_ids: Event IDs to include in the computation.

    Returns:
        Nested mapping: event_id -> horizon_code -> weighted_return_pct.
        Returns are in percentage points (e.g. -15.3 means -15.3%).
        NaN is returned as None for display-layer safety.
    """
    weight_vector = np.zeros(len(matrix.asset_ids), dtype=np.float32)
    for asset_id, weight in portfolio_weights.items():
        idx = matrix.asset_idx.get(asset_id)
        if idx is not None:
            weight_vector[idx] = weight

    event_indices = [
        i for i, eid in enumerate(matrix.event_ids)
        if eid in set(selected_event_ids)
    ]
    if not event_indices:
        return {}

    event_id_at = {i: matrix.event_ids[i] for i in event_indices}
    sub_tensor = matrix.tensor[event_indices]

    valid_mask = ~np.isnan(sub_tensor)
    covered_weights = np.where(valid_mask, weight_vector[np.newaxis, np.newaxis, :], 0.0)
    total_covered = covered_weights.sum(axis=2)

    safe_returns = np.where(valid_mask, sub_tensor, 0.0)
    raw_weighted = (safe_returns * weight_vector[np.newaxis, np.newaxis, :]).sum(axis=2)

    scale = np.where(total_covered > 0, 1.0 / total_covered, 0.0)
    normalized = raw_weighted * scale

    results: dict[str, dict[str, float]] = {}
    horizon_codes = list(HORIZONS)
    for local_idx, global_idx in enumerate(event_indices):
        event_id = event_id_at[global_idx]
        results[event_id] = {}
        for h_idx, horizon in enumerate(horizon_codes):
            value = float(normalized[local_idx, h_idx])
            results[event_id][horizon] = None if np.isnan(value) else round(value, 2)

    return results