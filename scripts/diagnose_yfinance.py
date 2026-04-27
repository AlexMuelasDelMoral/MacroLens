"""Diagnose why yfinance isn't returning data."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
import pandas as pd

print(f"yfinance version: {yf.__version__}")
print(f"pandas version:   {pd.__version__}")
print()

# Test 1: Simple ticker that should always work
print("TEST 1: Fetch S&P 500 (^GSPC) for 2008 GFC period")
print("-" * 60)
try:
    data = yf.download(
        "^GSPC",
        start="2008-09-15",
        end="2009-12-31",
        progress=False,
    )
    print(f"  Shape: {data.shape}")
    print(f"  Empty: {data.empty}")
    print(f"  Columns: {list(data.columns)}")
    print(f"  Column type: {type(data.columns)}")
    if not data.empty:
        print(f"  First close value: {data['Close'].iloc[0] if 'Close' in data.columns else 'NO CLOSE COL'}")
        print(f"  First 3 rows:")
        print(data.head(3))
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

print()

# Test 2: Using Ticker.history()
print("TEST 2: Using yf.Ticker().history() instead")
print("-" * 60)
try:
    ticker = yf.Ticker("^GSPC")
    data = ticker.history(start="2008-09-15", end="2009-12-31")
    print(f"  Shape: {data.shape}")
    print(f"  Empty: {data.empty}")
    print(f"  Columns: {list(data.columns)}")
    if not data.empty:
        print(f"  First close: {data['Close'].iloc[0]}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

print()

# Test 3: Multi-ticker test
print("TEST 3: Fetch multiple tickers")
print("-" * 60)
try:
    data = yf.download(
        ["^GSPC", "GLD", "TLT"],
        start="2020-01-01",
        end="2020-06-30",
        progress=False,
    )
    print(f"  Shape: {data.shape}")
    print(f"  Columns: {list(data.columns)[:5]}")
    print(f"  Column type: {type(data.columns)}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

print()
print("Diagnosis complete. Share the output to identify the issue.")