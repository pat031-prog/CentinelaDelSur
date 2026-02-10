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

async def fetch_news_ddg(country_name: str, limit: int = 8) -> List[str]:
    """
    Fetch news using DuckDuckGo Search (robust against RSS blocks).
    Searches for 'economía política crisis' to get relevant context.
    Includes fallback to Google News if DDGS fails (e.g. date issues).
    """
    results = []
    try:
        from duckduckgo_search import DDGS
        
        # Proper async wrapper call because DDGS is blocking by default
        def _search_sync():
            with DDGS() as ddgs:
                # Search WITHOUT timelimit to avoid date parsing errors in future simulation
                query = f"{country_name} economía política crisis inflación"
                return list(ddgs.text(query, region="wt-wt", safesearch="off", max_results=limit))

        raw_results = await asyncio.to_thread(_search_sync)
        
        for r in raw_results:
            title = r.get("title", "No Title")
            snippet = r.get("body", "")
            link = r.get("href", "")
            source = r.get("source", "Web")
            # Format: - TITLE (Source) \n  Snippet... [Link]
            results.append(f"- **{title}** ({source})\n  \"{snippet}\"\n  [Link: {link}]")
            
    except Exception as e:
        log.warning(f"DuckDuckGo search failed: {e}")
        # FALLBACK: Google News RSS (better than nothing)
        try:
            log.info("Falling back to Google News RSS...")
            return await fetch_google_news_fallback(country_name, limit)
        except Exception as ex:
             results.append(f"Search failed: {e} | Fallback failed: {ex}")
        
    return results

async def fetch_google_news_fallback(country_name: str, limit: int = 5) -> List[str]:
    """Fallback Google News RSS scraper."""
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
    return articles

async def get_country_context(country_code: str, country_name: str) -> str:
    """
    Aggregates all real data into a context string for the LLM.
    Stage 0.5 of the pipeline.
    """
    # Run fetches in parallel
    market_task = fetch_market_data(country_code)
    news_task = fetch_news_ddg(country_name)
    # We skip specific indicator scraping as DDGS covers it better via snippets
    
    market, news = await asyncio.gather(market_task, news_task)
    
    context = []
    
    context.append(f"=== REAL-TIME MARKET DATA ({country_code}) ===")
    context.append(f"Currency: {market.get('currency', 'N/A')}")
    context.append(f"Stock Market: {market.get('market_index', 'N/A')}")
    if "source" in market:
        context.append(f"Source: {market['source']}")
    context.append("")
    
    context.append(f"=== SEARCH RESULTS & NEWS Snippets ({country_name}) ===")
    if news:
        context.extend(news)
    else:
        context.append("DATA FETCH FAILED: No recent news found via DuckDuckGo or Fallback.")
        
    return "\n".join(context)
