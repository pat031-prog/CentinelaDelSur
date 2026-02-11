"""Market data endpoints — FX rates and commodity prices via yfinance."""
import asyncio
import time
from fastapi import APIRouter
from backend.utils.logger import logger

router = APIRouter()

# In-memory cache
_fx_cache: dict = {"data": [], "ts": 0}
_comm_cache: dict = {"data": [], "ts": 0}
_CACHE_TTL = 300  # 5 min


def _fetch_batch(symbols: list[str]) -> dict:
    """Fetch latest prices for a batch of symbols using yfinance.download (faster than Ticker)."""
    import yfinance as yf
    result = {}
    try:
        # download last 2 days to compute change
        df = yf.download(symbols, period="2d", progress=False, threads=True)
        if df.empty:
            return result

        close = df["Close"] if "Close" in df.columns else df.get("Adj Close")
        if close is None or close.empty:
            return result

        # Handle single vs multiple symbols
        if isinstance(close, type(df)) and len(close.columns) > 0:
            # Multiple symbols → DataFrame
            for sym in close.columns:
                col = close[sym].dropna()
                if len(col) >= 1:
                    last = float(col.iloc[-1])
                    prev = float(col.iloc[-2]) if len(col) >= 2 else last
                    chg = ((last - prev) / prev * 100) if prev > 0 else 0
                    result[sym] = {"price": round(last, 4), "change_pct": round(chg, 2)}
        else:
            # Single symbol → Series
            col = close.dropna()
            if len(col) >= 1:
                last = float(col.iloc[-1])
                prev = float(col.iloc[-2]) if len(col) >= 2 else last
                chg = ((last - prev) / prev * 100) if prev > 0 else 0
                sym = symbols[0] if symbols else "?"
                result[sym] = {"price": round(last, 4), "change_pct": round(chg, 2)}
    except Exception as e:
        logger.error(f"yfinance download error: {e}")
    return result


async def _get_cached(cache: dict, symbols: list[str], label_map: dict, value_key: str) -> list:
    """Generic cached fetch."""
    now = time.time()
    if cache["data"] and now - cache["ts"] < _CACHE_TTL:
        return cache["data"]

    try:
        data = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, _fetch_batch, symbols),
            timeout=30
        )
    except asyncio.TimeoutError:
        logger.warning("yfinance fetch timed out after 30s")
        return cache["data"]  # return stale
    except Exception as e:
        logger.error(f"Market fetch error: {e}")
        return cache["data"]

    items = []
    for sym in symbols:
        if sym in data:
            meta = label_map.get(sym, {})
            item = {**meta, value_key: data[sym]["price"], "change": data[sym]["change_pct"]}
            items.append(item)

    if items:
        cache["data"] = items
        cache["ts"] = now
    return items


# ===== FX =====
FX_SYMBOLS = [
    "USDARS=X", "USDBRL=X", "USDCLP=X", "USDCOP=X",
    "USDMXN=X", "USDPEN=X", "USDUYU=X", "EURUSD=X",
]
FX_LABELS = {
    "USDARS=X": {"pair": "USD/ARS"},
    "USDBRL=X": {"pair": "USD/BRL"},
    "USDCLP=X": {"pair": "USD/CLP"},
    "USDCOP=X": {"pair": "USD/COP"},
    "USDMXN=X": {"pair": "USD/MXN"},
    "USDPEN=X": {"pair": "USD/PEN"},
    "USDUYU=X": {"pair": "USD/UYU"},
    "EURUSD=X": {"pair": "EUR/USD"},
}


@router.get("/market/fx")
async def get_fx_rates():
    items = await _get_cached(_fx_cache, FX_SYMBOLS, FX_LABELS, "rate")
    return {"rates": items, "source": "Yahoo Finance", "cached": bool(_fx_cache["data"])}


# ===== COMMODITIES =====
COMM_SYMBOLS = ["CL=F", "GC=F", "SI=F", "ZS=F", "HG=F", "NG=F"]
COMM_LABELS = {
    "CL=F": {"name": "Petróleo WTI", "unit": "USD/bbl"},
    "GC=F": {"name": "Oro", "unit": "USD/oz"},
    "SI=F": {"name": "Plata", "unit": "USD/oz"},
    "ZS=F": {"name": "Soja", "unit": "USd/bu"},
    "HG=F": {"name": "Cobre", "unit": "USD/lb"},
    "NG=F": {"name": "Gas Natural", "unit": "USD/MMBtu"},
}


@router.get("/market/commodities")
async def get_commodities():
    items = await _get_cached(_comm_cache, COMM_SYMBOLS, COMM_LABELS, "value")
    return {"commodities": items, "source": "Yahoo Finance", "cached": bool(_comm_cache["data"])}
