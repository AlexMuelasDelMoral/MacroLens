from __future__ import annotations
import json
import streamlit as st
from src.data_loader import ASSET_LABELS

_STATE_KEY = "active_portfolio"
_LAST_SOURCE_KEY = "active_portfolio_source"


def get_portfolio() -> dict:
    return st.session_state.get(_STATE_KEY, {})


def set_portfolio(weights: dict, source: str = "unknown") -> None:
    st.session_state[_STATE_KEY] = {k: float(v) for k, v in weights.items()}
    st.session_state[_LAST_SOURCE_KEY] = source


def clear_portfolio() -> None:
    st.session_state.pop(_STATE_KEY, None)
    st.session_state.pop(_LAST_SOURCE_KEY, None)


def get_portfolio_source() -> str | None:
    return st.session_state.get(_LAST_SOURCE_KEY)


def get_active_positions() -> dict:
    return {k: v for k, v in get_portfolio().items() if v > 0}


def has_portfolio() -> bool:
    return bool(get_active_positions())


def sync_from_stress_test_widgets() -> None:
    weights = {
        asset_id: float(st.session_state.get(f"port_{asset_id}", 0.0))
        for asset_id in ASSET_LABELS
    }
    set_portfolio(weights, source="Stress Test")


def portfolio_as_fractions() -> dict:
    return {k: v / 100.0 for k, v in get_active_positions().items()}


def portfolio_summary_string() -> str:
    positions = get_active_positions()
    if not positions:
        return "No portfolio active"
    top = sorted(positions.items(), key=lambda x: -x[1])[:3]
    parts = [f"{ASSET_LABELS.get(k, k)} {v:.0f}%" for k, v in top]
    suffix = f" + {len(positions) - 3} more" if len(positions) > 3 else ""
    return ", ".join(parts) + suffix


def encode_portfolio_for_url(weights: dict) -> str:
    parts = [
        f"{asset_id}:{round(weight, 2)}"
        for asset_id, weight in weights.items()
        if weight > 0
    ]
    return ",".join(parts)


def decode_portfolio_from_url(encoded: str) -> dict:
    if not encoded or not encoded.strip():
        return {}
    weights = {}
    for part in encoded.split(","):
        part = part.strip()
        if ":" not in part:
            continue
        asset_id, _, raw_weight = part.partition(":")
        try:
            weights[asset_id.strip()] = float(raw_weight.strip())
        except ValueError:
            continue
    return weights


def portfolio_to_csv(weights: dict) -> str:
    lines = [
        f"{asset_id},{weight:.2f}"
        for asset_id, weight in sorted(weights.items(), key=lambda x: -x[1])
        if weight > 0
    ]
    return "\n".join(lines)


def portfolio_to_json(weights: dict) -> str:
    active = {
        asset_id: round(weight, 2)
        for asset_id, weight in sorted(weights.items(), key=lambda x: -x[1])
        if weight > 0
    }
    return json.dumps(active, indent=2)
