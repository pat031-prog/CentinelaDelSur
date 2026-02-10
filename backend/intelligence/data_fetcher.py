"""
Data Fetcher Module for ATALAYA Pipeline.
Fetches real-time market data, news, and economic indicators to prevent AI hallucinations.
"""
import logging
import asyncio
import re
from typing import Dict, Any, List
import yfinance as yf
from bs4 import BeautifulSoup
import httpx

log = logging.getLogger("data_fetcher")

# Mapping for yfinance tickers
CURRENCY_TICKERS = {
    "ARG": "ARS=X", "BRA": "BRL=X", "MEX": "MXN=X", "CHL": "CLP=X",
    "COL": "COP=X", "PER": "PEN=X", "URY": "UYU=X",
}

MARKET_INDICES = {
    "ARG": "^MERV", "BRA": "^BVSP", "MEX": "^MXX", "CHL": "^IPSA",
}

# Source URLs provided by user/config
OFFICIAL_SOURCES = {
    "ARG": {
        "inflation": "https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31",
        "reserves": "https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables_datos.asp",
    }
}

def _fetch_market_data_sync(country_code: str) -> Dict[str, Any]:
    """Sync helper for yfinance (blocking)."""
    data = {"currency": "N/A", "market_index": "N/A", "last_updated": "N/A"}
    try:
        # 1. Currency
        ticker = CURRENCY_TICKERS.get(country_code)
        if ticker:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(period="1d")
            if not hist.empty:
                val = hist["Close"].iloc[-1]
                data["currency"] = f"{val:.2f} (USD/{country_code})"
        
        # 2. Market Index
        idx = MARKET_INDICES.get(country_code)
        if idx:
            idx_obj = yf.Ticker(idx)
            hist = idx_obj.history(period="1d")
            if not hist.empty:
                val = hist["Close"].iloc[-1]
                change = ((val - hist["Open"].iloc[-1]) / hist["Open"].iloc[-1]) * 100
                data["market_index"] = f"{val:.2f} ({change:+.2f}%)"
                
        data["source"] = "Yahoo Finance (Real-time)"
    except Exception as e:
        log.warning(f"Market data fetch failed for {country_code}: {e}")
        data["error"] = str(e)
    return data

async def fetch_market_data(country_code: str) -> Dict[str, Any]:
    """Fetch live market data using yfinance (non-blocking)."""
    return await asyncio.to_thread(_fetch_market_data_sync, country_code)

async def fetch_google_news(country_name: str, limit: int = 5) -> List[str]:
    """Fetch Google News RSS and extract titles + links."""
    articles = []
    try:
        url = f"https://news.google.com/rss/search?q={country_name}+economia+politica&hl=es-419&gl=LATAM&ceid=US:es-419"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "xml")
                items = soup.find_all("item", limit=limit)
                for item in items:
                    title = item.title.text if item.title else "No Title"
                    link = item.link.text if item.link else "No Link"
                    pub_date = item.pubDate.text if item.pubDate else ""
                    articles.append(f"- {title} ({pub_date}) [Link: {link}]")
    except Exception as e:
        log.warning(f"Google News fetch failed: {e}")
        articles.append("News fetch failed.")
        
    return articles

async def fetch_economic_indicators(country_code: str) -> Dict[str, str]:
    """
    Attempt to fetch official economic indicators.
    Currently returns official source URLs for manual verification if scraping is hard.
    """
    sources = OFFICIAL_SOURCES.get(country_code, {})
    indicators = {}
    
    # Check official sources availability (simple HEAD request)
    async with httpx.AsyncClient(timeout=5.0) as client:
        for key, url in sources.items():
            try:
                resp = await client.head(url)
                if resp.status_code < 400:
                    indicators[key] = f"Source Available: {url}"
                else:
                    indicators[key] = f"Source Unreachable ({resp.status_code}): {url}"
            except Exception:
                indicators[key] = f"Connection Failed: {url}"
                
    return indicators

async def get_country_context(country_code: str, country_name: str) -> str:
    """
    Aggregates all real data into a context string for the LLM.
    Stage 0.5 of the pipeline.
    """
    # Run fetches in parallel
    market_task = fetch_market_data(country_code)
    news_task = fetch_google_news(country_name)
    indicators_task = fetch_economic_indicators(country_code)
    
    market, news, indicators = await asyncio.gather(market_task, news_task, indicators_task)
    
    context = []
    
    context.append(f"=== REAL-TIME MARKET DATA ({country_code}) ===")
    context.append(f"Currency: {market.get('currency', 'N/A')}")
    context.append(f"Stock Market: {market.get('market_index', 'N/A')}")
    if "source" in market:
        context.append(f"Source: {market['source']}")
    context.append("")
    
    context.append(f"=== OFFICIAL ECONOMIC SOURCES ({country_code}) ===")
    if indicators:
        for k, v in indicators.items():
            context.append(f"{k.upper()}: {v}")
    else:
        context.append("No specific official sources configured.")
    context.append("INSTRUCTION: If specific values (inflation, reserves) are not listed above, DO NOT INVENT THEM. Use 'Data Unavailable' or cite the source link as 'pending verification'.")
    context.append("")
    
    context.append(f"=== RECENT NEWS ({country_name}) ===")
    if news:
        context.extend(news)
    else:
        context.append("No recent news found.")
        
    return "\n".join(context)
