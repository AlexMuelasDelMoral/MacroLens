"""Portfolio weight parser for MacroLens.

Accepts portfolio definitions in five formats and resolves them against the
known asset universe defined in src/data_loader.py:

    1. Space-separated:    sp500 35
    2. Comma-separated:    sp500,35
    3. Colon with percent: sp500: 35%
    4. Tab-separated:      sp500<TAB>35      (Excel and Google Sheets paste)
    5. JSON object:        {"sp500": 35, "bitcoin": 10}

Both raw asset IDs (sp500) and display names (S and P 500, S&P 500) are
accepted. Auto-detects whether values are decimals or percentages, sums
them, and scales the result so weights total exactly 1.0. Unknown labels
are reported but do not block parsing.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Mapping

_PERCENT_SUFFIX = re.compile(r"%\s*$")
_LABEL_VALUE_SPLIT = re.compile(r"^(.+?)[\s,:\t]+([\d.\-+%\s,]+)\s*$")
_NON_ALNUM = re.compile(r"[^a-z0-9]")


class PortfolioParseError(ValueError):
    """Raised when portfolio input cannot be parsed."""


@dataclass(frozen=True)
class ParsedPortfolio:
    """Result of a parse. ``weights`` always sums to 1.0 on success."""
    weights: dict[str, float]
    warnings: tuple[str, ...]
    invalid_entries: tuple[str, ...]
    original_sum: float
    was_normalized: bool


def _parse_value(raw: str) -> float:
    """Parse a numeric weight. A trailing percent sign or a value above 1.5
    is interpreted as a percentage and divided by one hundred."""
    text = raw.strip()
    is_percent = bool(_PERCENT_SUFFIX.search(text))
    cleaned = _PERCENT_SUFFIX.sub("", text).replace(" ", "").replace(",", "")
    try:
        value = float(cleaned)
    except ValueError as exc:
        raise PortfolioParseError(f"Cannot parse number: {raw!r}") from exc
    if is_percent or value > 1.5:
        value /= 100.0
    return value


def _split_line(line: str) -> tuple[str, str]:
    """Split a single line into (label, value)."""
    match = _LABEL_VALUE_SPLIT.match(line)
    if not match:
        raise PortfolioParseError(
            f"Expected 'label value', got {line!r}"
        )
    return match.group(1).strip(), match.group(2).strip()


def _build_lookups(
    asset_labels: Mapping[str, str],
) -> tuple[dict[str, str], dict[str, str]]:
    """Pre-compute lookup tables for asset resolution.

    Returns (exact_lookup, fuzzy_lookup) where keys are lowercased and
    fuzzy keys are stripped of all non-alphanumeric characters so that
    'S&P 500' and 'sp500' both resolve to the same asset_id.
    """
    exact: dict[str, str] = {}
    fuzzy: dict[str, str] = {}
    for asset_id, display_name in asset_labels.items():
        aid_low = asset_id.lower()
        name_low = display_name.lower()
        exact[aid_low] = asset_id
        exact[name_low] = asset_id
        fuzzy[_NON_ALNUM.sub("", aid_low)] = asset_id
        fuzzy[_NON_ALNUM.sub("", name_low)] = asset_id
    return exact, fuzzy


def parse_portfolio(
    text: str,
    asset_labels: Mapping[str, str],
    tolerance: float = 0.01,
) -> ParsedPortfolio:
    """Parse free-form portfolio text into normalized weights.

    Args:
        text: Raw user input in any supported format.
        asset_labels: Mapping of asset_id to display name. Used for both
            validation and reverse lookup of friendly names.
        tolerance: Distance from 1.0 within which the original sum is
            treated as already normalized and no warning is emitted.

    Returns:
        ParsedPortfolio with weights guaranteed to sum to 1.0.

    Raises:
        PortfolioParseError: On structural errors only (empty input,
            malformed lines, negative weights, zero total, no recognized
            assets).
    """
    if not text or not text.strip():
        raise PortfolioParseError("Input is empty.")

    exact_lookup, fuzzy_lookup = _build_lookups(asset_labels)
    stripped = text.strip()
    raw_entries: list[tuple[str, float]] = []

    if stripped.startswith("{"):
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise PortfolioParseError(f"Invalid JSON: {exc.msg}") from exc
        if not isinstance(data, dict):
            raise PortfolioParseError(
                "JSON must be an object mapping asset names to weights."
            )
        for key, value in data.items():
            raw_entries.append((str(key), _parse_value(str(value))))
    else:
        for line_no, raw_line in enumerate(stripped.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                label, value_str = _split_line(line)
                value = _parse_value(value_str)
            except PortfolioParseError as exc:
                raise PortfolioParseError(f"Line {line_no}: {exc}") from exc
            raw_entries.append((label, value))

    if not raw_entries:
        raise PortfolioParseError("No valid entries found.")

    resolved: dict[str, float] = {}
    invalid: list[str] = []

    for label, value in raw_entries:
        if value < 0:
            raise PortfolioParseError(
                f"Negative weight not supported: {label}"
            )
        key = label.lower().strip()
        asset_id = exact_lookup.get(key) or fuzzy_lookup.get(
            _NON_ALNUM.sub("", key)
        )
        if asset_id is None:
            invalid.append(label)
            continue
        if asset_id in resolved:
            raise PortfolioParseError(
                f"Duplicate asset in input: {label}"
            )
        resolved[asset_id] = value

    if not resolved:
        raise PortfolioParseError(
            "None of the entries match known assets. "
            f"Unrecognized: {', '.join(invalid)}"
        )

    total = sum(resolved.values())
    if total <= 0:
        raise PortfolioParseError("Total weight must be greater than zero.")

    warnings: list[str] = []
    was_normalized = abs(total - 1.0) > tolerance
    if was_normalized:
        warnings.append(
            f"Weights summed to {total * 100:.2f} percent. "
            "Auto-scaled to 100 percent."
        )
    if invalid:
        warnings.append(
            f"Unrecognized entries skipped: {', '.join(invalid)}. "
            "Use either the asset ID (sp500, us_10y_treasury) or the "
            "display name shown in the category tabs."
        )

    normalized = {aid: w / total for aid, w in resolved.items()}
    return ParsedPortfolio(
        weights=normalized,
        warnings=tuple(warnings),
        invalid_entries=tuple(invalid),
        original_sum=total,
        was_normalized=was_normalized,
    )