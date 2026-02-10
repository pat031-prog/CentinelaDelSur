"""
Data Fetcher Module for ATALAYA Pipeline.
Fetches real-time market data, news, and official reports.
Stage 0.5: Aggressive Data Collection from Multiple Verticals.
"""
import logging
import asyncio
import re
from typing import Dict, Any, List
import yfinance as yf
from bs4 import BeautifulSoup
import httpx

log = logging.getLogger("data_fetcher")

# --- CONFIGURATION ---

CURRENCY_TICKERS = {
    "ARG": "ARS=X", "BRA": "BRL=X", "MEX": "MXN=X", "CHL": "CLP=X",
    "COL": "COP=X", "PER": "PEN=X", "URY": "UYU=X",
}

MARKET_INDICES = {
    "ARG": "^MERV", "BRA": "^BVSP", "MEX": "^MXX", "CHL": "^IPSA",
}

# Targeted Domains for Deep Search
COUNTRY_RESEARCH_TARGETS = {
    "ARG": {
        "media": ["lanacion.com.ar", "clarin.com", "infobae.com", "ambito.com", "cronista.com"],
        "official": ["argentina.gob.ar", "bcra.gob.ar", "indec.gob.ar"]
    },
    "BRA": {
        "media": ["globo.com", "folha.uol.com.br", "estadao.com.br", "valor.globo.com"],
        "official": ["gov.br", "bcb.gov.br", "ibge.gov.br"]
    },
    "default": {
        "media": ["cnn.com", "elpais.com", "bbc.com"],
        "official": []
    }
}

# --- MARKET DATA FUNCTIONS ---

def _fetch_market_data_sync(country_code: str) -> Dict[str, Any]:
    """Sync helper for yfinance (blocking). Uses 5d period for robustness."""
    data = {"currency": "N/A", "market_index": "N/A", "last_updated": "N/A"}
    try:
        # 1. Currency
        ticker = CURRENCY_TICKERS.get(country_code)
        if ticker:
            ticker_obj = yf.Ticker(ticker)
            # Fetch 5 days to handle weekends/holidays/future-sim lags
            hist = ticker_obj.history(period="5d")
            if not hist.empty:
                val = hist["Close"].iloc[-1]
                date = hist.index[-1].strftime("%Y-%m-%d")
                data["currency"] = f"{val:.2f} (USD/{country_code}) [{date}]"
        
        # 2. Market Index
        idx = MARKET_INDICES.get(country_code)
        if idx:
            idx_obj = yf.Ticker(idx)
            hist = idx_obj.history(period="5d")
            if not hist.empty:
                val = hist["Close"].iloc[-1]
                prev = hist["Open"].iloc[-1]
                change = ((val - prev) / prev) * 100
                date = hist.index[-1].strftime("%Y-%m-%d")
                data["market_index"] = f"{val:.2f} ({change:+.2f}%) [{date}]"
                
        data["source"] = "Yahoo Finance (Real-time)"
    except Exception as e:
        log.warning(f"Market data fetch failed for {country_code}: {e}")
        data["error"] = str(e)
    return data

async def fetch_market_data(country_code: str) -> Dict[str, Any]:
    """Fetch live market data using yfinance (non-blocking)."""
    return await asyncio.to_thread(_fetch_market_data_sync, country_code)

# --- SEARCH FUNCTIONS ---

async def search_ddg_category(query: str, label: str, limit: int = 3) -> List[str]:
    """Run a specific DDG search and format results with a label."""
    results = []
    try:
        from duckduckgo_search import DDGS
        
        def _search():
            with DDGS() as ddgs:
                return list(ddgs.text(query, region="wt-wt", safesearch="off", max_results=limit))
        
        raw = await asyncio.to_thread(_search)
        for r in raw:
            title = r.get("title", "No Title")
            snippet = r.get("body", "")
            results.append(f"- [{label}] **{title}**: \"{snippet}\"")
            
    except Exception as e:
        log.warning(f"DDG Search '{query}' failed: {e}")
    return results

async def fetch_comprehensive_search(country_name: str, country_code: str) -> List[str]:
    """
    Orchestrate parallel searches:
    1. General News (Recent)
    2. Official Sources (site:.gov...)
    3. Major Media (site:outlet...)
    """
    targets = COUNTRY_RESEARCH_TARGETS.get(country_code, COUNTRY_RESEARCH_TARGETS["default"])
    
    tasks = []
    
    # 1. General Crisis/Economy Context
    tasks.append(search_ddg_category(
        f"{country_name} crisis economía inflación política", 
        "GENERAL"
    ))
    
    # 2. Official Sources Search
    if targets["official"]:
        sites = " OR ".join([f"site:{d}" for d in targets["official"]])
        # Query: site:gov.ar (inflación OR reservas OR comunicado)
        q_official = f"({sites}) (inflación OR reservas OR comunicado OR decreto)"
        tasks.append(search_ddg_category(q_official, "OFFICIAL SOURCE", limit=4))
        
    # 3. Major Media Search
    if targets["media"]:
        # Pick top 2 for specific query
        sites_media = " OR ".join([f"site:{d}" for d in targets["media"][:3]])
        q_media = f"({sites_media}) (economía OR política)"
        tasks.append(search_ddg_category(q_media, "REGIONAL MEDIA", limit=4))

    # Execute all
    results_list = await asyncio.gather(*tasks)
    
    # Flatten
    flat_results = []
    for r in results_list:
        flat_results.extend(r)
        
    # Fallback if empty
    if not flat_results:
        log.warning("All DDG searches failed. Attempting Google RSS fallback.")
        return await fetch_google_news_fallback(country_name)
        
    return flat_results

async def fetch_google_news_fallback(country_name: str) -> List[str]:
    """Last resort fallback."""
    articles = []
    try:
        url = f"https://news.google.com/rss/search?q={country_name}+economia&hl=es-419&gl=LATAM&ceid=US:es-419"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "xml")
                items = soup.find_all("item", limit=5)
                for item in items:
                    title = item.title.text if item.title else "?"
                    articles.append(f"- [FALLBACK RSS] {title}")
    except Exception:
        pass
    return articles

async def get_country_context(country_code: str, country_name: str) -> str:
    """
    Stage 0.5: Aggregate Market Data + Multi-Vertical Search.
    """
    market_task = fetch_market_data(country_code)
    search_task = fetch_comprehensive_search(country_name, country_code)
    
    market, search_results = await asyncio.gather(market_task, search_task)
    
    context = []
    
    context.append(f"=== REAL-TIME MARKET DATA ({country_code}) ===")
    context.append(f"Currency: {market.get('currency', 'N/A')}")
    context.append(f"Index: {market.get('market_index', 'N/A')}")
    if "error" in market:
        context.append(f"Market Data Status: Failed ({market['error']})")
    
    context.append(f"\n=== COMPREHENSIVE INTELLIGENCE FEED ({country_name}) ===")
    if search_results:
        context.extend(search_results)
    else:
        context.append("DATA FETCH FAILED: No intelligence gathered from any source.")
        
    return "\n".join(context)
