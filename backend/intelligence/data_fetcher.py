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

# --- SEARCH FUNCTIONS (HTML SCRAPER) ---

async def search_ddg_html(query: str, label: str, limit: int = 3) -> List[str]:
    """
    Robust scraper for html.duckduckgo.com.
    Bypasses library limitations (date parsing) and JS blockers.
    """
    results_text = []
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://html.duckduckgo.com/"
    }
    data = {"q": query}
    
    try:
        def _scrape_sync():
            # httpx sync inside thread to avoid async context issues if strict
            import httpx
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                resp = client.post(url, data=data, headers=headers)
                if resp.status_code == 200:
                    return resp.content
            return None

        content = await asyncio.to_thread(_scrape_sync)
        
        if content:
            soup = BeautifulSoup(content, "html.parser")
            # Select result blocks
            results = soup.select(".result")
            count = 0
            for r in results:
                if count >= limit: break
                
                title_elem = r.select_one(".result__title .result__a")
                snippet_elem = r.select_one(".result__snippet")
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '#')
                    # snippet is optional
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    results_text.append(f"- [{label}] **{title}**: \"{snippet}\" [Link: {link}]")
                    count += 1
                    
    except Exception as e:
        log.warning(f"DDG HTML Search '{query}' failed: {e}")
        
    return results_text

async def fetch_comprehensive_search(country_name: str, country_code: str) -> List[str]:
    """
    Orchestrate parallel searches using the robust HTML scraper.
    """
    targets = COUNTRY_RESEARCH_TARGETS.get(country_code, COUNTRY_RESEARCH_TARGETS["default"])
    
    tasks = []
    
    # 1. General Context (Expanded query)
    tasks.append(search_ddg_html(
        f"{country_name} crisis economía inflación 2026", 
        "GENERAL"
    ))
    
    # 2. Official Sources
    if targets["official"]:
        sites = " OR ".join([f"site:{d}" for d in targets["official"]])
        q_official = f"({sites}) (inflación OR reservas OR comunicado) {country_name}"
        tasks.append(search_ddg_html(q_official, "OFFICIAL", limit=3))
        
    # 3. Regional Media
    if targets["media"]:
        sites_media = " OR ".join([f"site:{d}" for d in targets["media"][:3]])
        q_media = f"({sites_media}) (economía OR política) {country_name}"
        tasks.append(search_ddg_html(q_media, "MEDIA", limit=3))

    # Execute all
    results_list = await asyncio.gather(*tasks)
    
    # Flatten
    flat_results = []
    for r in results_list:
        flat_results.extend(r)
        
    # Fallback if empty (try simplified query)
    if not flat_results:
        log.warning("Primary DDG searches yielded no results. Trying fallback query.")
        flat_results.extend(await search_ddg_html(f"{country_name} news", "FALLBACK"))
        
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
