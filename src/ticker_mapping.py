"""
Maps internal asset IDs to Yahoo Finance ticker symbols.
Includes data availability dates for honest handling.
"""

TICKER_MAP = {
    # US Equities - Size
    "sp500":                 {"ticker": "^GSPC",     "available_from": "1950-01-01"},
    "nasdaq":                {"ticker": "^IXIC",     "available_from": "1971-02-05"},
    "dow_jones":             {"ticker": "^DJI",      "available_from": "1985-01-29"},
    "russell_2000":          {"ticker": "^RUT",      "available_from": "1987-09-10"},
    "russell_midcap":        {"ticker": "^MID",      "available_from": "1991-01-01"},

    # US Equities - Sector (sector ETFs began Dec 1998)
    "tech":                  {"ticker": "XLK",       "available_from": "1998-12-22"},
    "healthcare":            {"ticker": "XLV",       "available_from": "1998-12-22"},
    "financials":            {"ticker": "XLF",       "available_from": "1998-12-22"},
    "energy":                {"ticker": "XLE",       "available_from": "1998-12-22"},
    "utilities":             {"ticker": "XLU",       "available_from": "1998-12-22"},
    "consumer_staples":      {"ticker": "XLP",       "available_from": "1998-12-22"},
    "consumer_discretionary":{"ticker": "XLY",       "available_from": "1998-12-22"},
    "luxury":                {"ticker": "XLY",       "available_from": "1998-12-22"},
    "industrials":           {"ticker": "XLI",       "available_from": "1998-12-22"},
    "basic_materials":       {"ticker": "XLB",       "available_from": "1998-12-22"},
    "communication":         {"ticker": "XLC",       "available_from": "2018-06-19"},
    "reits_us":              {"ticker": "IYR",       "available_from": "2000-06-19"},

    # International Equities
    "developed_ex_us":       {"ticker": "EFA",       "available_from": "2001-08-17"},
    # Replaced ^STOXX50E (unreliable) with ^GDAXI (German DAX has stable Yahoo data)
    "europe_stoxx":          {"ticker": "^GDAXI",    "available_from": "1990-11-26"},
    "uk_ftse":               {"ticker": "^FTSE",     "available_from": "1984-04-02"},
    "japan_nikkei":          {"ticker": "^N225",     "available_from": "1965-01-05"},
    "china_equity":          {"ticker": "^HSI",      "available_from": "1986-12-31"},
    "emerging_markets":      {"ticker": "EEM",       "available_from": "2003-04-14"},
    "india_equity":          {"ticker": "^NSEI",     "available_from": "2007-09-17"},

    # Fixed Income — using yield indices for older events when ETFs didn't exist
    "us_tbill_3m":           {"ticker": "^IRX",      "available_from": "1960-01-04"},
    # Use ^FVX (5Y yield) as 2Y proxy for older events; SHY for modern
    "us_2y_treasury":        {"ticker": "SHY",       "available_from": "2002-07-22",
                              "fallback_ticker": "^FVX", "fallback_from": "1962-01-02"},
    "us_10y_treasury":       {"ticker": "IEF",       "available_from": "2002-07-22",
                              "fallback_ticker": "^TNX", "fallback_from": "1962-01-02"},
    "us_30y_treasury":       {"ticker": "TLT",       "available_from": "2002-07-22",
                              "fallback_ticker": "^TYX", "fallback_from": "1977-02-15"},
    "tips":                  {"ticker": "TIP",       "available_from": "2003-12-04"},
    "corporate_ig":          {"ticker": "LQD",       "available_from": "2002-07-22"},
    "high_yield":            {"ticker": "HYG",       "available_from": "2007-04-04"},
    "municipal":             {"ticker": "MUB",       "available_from": "2007-09-07"},
    "em_debt":               {"ticker": "EMB",       "available_from": "2007-12-17"},
    "intl_bonds":            {"ticker": "BNDX",      "available_from": "2013-06-04"},

    # Commodities
    "oil_wti":               {"ticker": "CL=F",      "available_from": "2000-08-23"},
    "natural_gas":           {"ticker": "NG=F",      "available_from": "2000-08-23"},
    "gold":                  {"ticker": "GC=F",      "available_from": "2000-08-30"},
    "silver":                {"ticker": "SI=F",      "available_from": "2000-08-30"},
    "copper":                {"ticker": "HG=F",      "available_from": "2000-08-30"},
    "platinum":              {"ticker": "PL=F",      "available_from": "2000-08-30"},
    "agriculture":           {"ticker": "DBA",       "available_from": "2007-01-05"},
    "wheat":                 {"ticker": "ZW=F",      "available_from": "2000-08-30"},
    "corn":                  {"ticker": "ZC=F",      "available_from": "2000-08-30"},

    # Currencies
    "usd_index":             {"ticker": "DX-Y.NYB",  "available_from": "1971-01-04"},
    "eur_usd":               {"ticker": "EURUSD=X",  "available_from": "2003-12-01"},
    "jpy_usd":               {"ticker": "JPYUSD=X",  "available_from": "2003-12-01"},
    "chf_usd":               {"ticker": "CHFUSD=X",  "available_from": "2003-12-01"},
    "gbp_usd":               {"ticker": "GBPUSD=X",  "available_from": "2003-12-01"},
    "em_fx":                 {"ticker": "CEW",       "available_from": "2009-05-06"},

    # Alternatives & Crypto
    "bitcoin":               {"ticker": "BTC-USD",   "available_from": "2014-09-17"},
    "ethereum":              {"ticker": "ETH-USD",   "available_from": "2017-11-09"},
    "reits_global":          {"ticker": "REET",      "available_from": "2014-07-08"},
    "vix":                   {"ticker": "^VIX",      "available_from": "1990-01-02"},
    "hedge_fund_idx":        {"ticker": "QAI",       "available_from": "2009-03-25"},
    "private_equity":        {"ticker": "PSP",       "available_from": "2006-10-25"},
}


def get_ticker(asset_id, target_date=None):
    """
    Get the appropriate Yahoo Finance ticker for an asset.
    If a fallback exists and the primary isn't available for target_date, use fallback.
    """
    info = TICKER_MAP.get(asset_id)
    if not info:
        return None

    # If no target_date specified, return primary ticker
    if target_date is None:
        return info.get("ticker")

    from datetime import datetime
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d")

    primary_from = datetime.strptime(info["available_from"], "%Y-%m-%d")

    # Primary ticker covers the date — use it
    if target_date >= primary_from:
        return info.get("ticker")

    # Try fallback if exists
    if "fallback_ticker" in info:
        fallback_from = datetime.strptime(info["fallback_from"], "%Y-%m-%d")
        if target_date >= fallback_from:
            return info.get("fallback_ticker")

    return None


def is_data_available(asset_id, target_date):
    """Check if Yahoo Finance has any usable data for this asset on this date."""
    ticker = get_ticker(asset_id, target_date)
    return ticker is not None


def get_ticker_for_event(asset_id, event_start_date):
    """Convenience: get the right ticker for an event's start date."""
    return get_ticker(asset_id, event_start_date)