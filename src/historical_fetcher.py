"""
Fetches real historical price data from Yahoo Finance.
Robust against yfinance API changes (MultiIndex columns, auto_adjust changes, etc.)
"""
import time
import warnings
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

from src.ticker_mapping import TICKER_MAP, get_ticker, is_data_available

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


HORIZON_DAYS = {
    "1m": 30,
    "3m": 90,
    "6m": 180,
    "1y": 365,
    "2y": 730,
}

# Tickers where we report absolute change (yields, vol)
ABSOLUTE_CHANGE_TICKERS = {"^TNX", "^IRX", "^TYX", "^FVX", "^VIX"}


def _normalize_dataframe(data, ticker):
    """
    yfinance returns different shapes depending on version:
    - Single ticker, old version: flat columns
    - Single ticker, new version: MultiIndex columns ('Close', '^GSPC')
    Normalize to flat columns.
    """
    if data is None or data.empty:
        return None

    # Flatten MultiIndex columns if present
    if isinstance(data.columns, pd.MultiIndex):
        # If it's (price_field, ticker), keep just price_field
        new_cols = []
        for col in data.columns:
            if isinstance(col, tuple):
                new_cols.append(col[0])
            else:
                new_cols.append(col)
        data.columns = new_cols

    # Drop duplicate columns if any
    data = data.loc[:, ~data.columns.duplicated()]

    # Ensure we have a Close column
    if "Close" not in data.columns:
        if "Adj Close" in data.columns:
            data["Close"] = data["Adj Close"]
        else:
            return None

    # Drop NaN-only rows
    data = data.dropna(subset=["Close"])

    if data.empty:
        return None

    return data


def fetch_price_series(ticker, start_date, end_date, retries=2):
    """Fetch historical prices using yfinance Ticker API (more reliable)."""
    if not ticker:
        return None

    last_err = None
    for attempt in range(retries):
        try:
            t = yf.Ticker(ticker)
            data = t.history(
                start=start_date,
                end=end_date,
                auto_adjust=True,
                actions=False,
            )
            data = _normalize_dataframe(data, ticker)
            if data is not None and not data.empty:
                return data

            # Fallback: try yf.download
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False,
                auto_adjust=True,
                threads=False,
            )
            data = _normalize_dataframe(data, ticker)
            if data is not None and not data.empty:
                return data

            return None
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(1.5)
                continue
    return None


def calculate_horizon_returns(price_data, event_start_date, ticker):
    """Calculate returns at 1m, 3m, 6m, 1y, 2y from event start date."""
    if price_data is None or price_data.empty:
        return {h: None for h in HORIZON_DAYS}

    # Make event_dt timezone-naive to match yfinance index
    event_dt = pd.Timestamp(event_start_date).tz_localize(None)
    idx = price_data.index
    if idx.tz is not None:
        idx = idx.tz_localize(None)
        price_data = price_data.copy()
        price_data.index = idx

    # Find first trading day at/after event start
    available = price_data.index[price_data.index >= event_dt]
    if len(available) == 0:
        return {h: None for h in HORIZON_DAYS}

    start_price = float(price_data.loc[available[0], "Close"])
    if start_price == 0 or pd.isna(start_price):
        return {h: None for h in HORIZON_DAYS}

    is_absolute = ticker in ABSOLUTE_CHANGE_TICKERS
    returns = {}

    for horizon, days in HORIZON_DAYS.items():
        target_dt = event_dt + pd.Timedelta(days=days)
        future = price_data.index[price_data.index >= target_dt]

        if len(future) == 0:
            returns[horizon] = None
            continue

        end_price = float(price_data.loc[future[0], "Close"])
        if pd.isna(end_price):
            returns[horizon] = None
            continue

        if is_absolute:
            returns[horizon] = round(end_price - start_price, 2)
        else:
            pct = ((end_price - start_price) / start_price) * 100
            returns[horizon] = round(pct, 2)

    return returns

def fetch_event_returns(event, asset_ids, verbose=False):
    """Fetch real returns for all assets for a single event."""
    event_start = event["start_date"]
    fetch_start = event_start
    fetch_end = (
        datetime.strptime(event_start, "%Y-%m-%d") + timedelta(days=800)
    ).strftime("%Y-%m-%d")

    results = {}
    success_count = 0
    fail_count = 0

    for asset_id in asset_ids:
        # Get the right ticker for this event's date (uses fallback if needed)
        ticker = get_ticker(asset_id, event_start)

        if ticker is None:
            results[asset_id] = {h: None for h in HORIZON_DAYS}
            fail_count += 1
            if verbose:
                print(f"     [SKIP] {asset_id}: pre-inception or no ticker")
            continue

        price_data = fetch_price_series(ticker, fetch_start, fetch_end)

        if price_data is None or price_data.empty:
            results[asset_id] = {h: None for h in HORIZON_DAYS}
            fail_count += 1
            if verbose:
                print(f"     [FAIL] {asset_id} ({ticker}): no data returned")
        else:
            returns = calculate_horizon_returns(price_data, event_start, ticker)
            results[asset_id] = returns
            real_count = sum(1 for v in returns.values() if v is not None)
            if real_count > 0:
                success_count += 1
            if verbose:
                fb = " (fallback)" if ticker != TICKER_MAP[asset_id].get("ticker") else ""
                print(f"     [ OK ] {asset_id} ({ticker}{fb}): {real_count}/5 horizons")

        time.sleep(0.2)

    return results, success_count, fail_count