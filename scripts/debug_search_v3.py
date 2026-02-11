
import asyncio
import httpx
from bs4 import BeautifulSoup
import traceback

async def scraper():
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://html.duckduckgo.com/"
    }
    data = {"q": "Argentina inflation crisis 2026"}
    
    print(f"Sending POST request to {url}...")
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.post(url, data=data, headers=headers)
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "html.parser")
                # Look for result titles and snippets
                # Typically .result__title and .result__snippet in HTML version
                results = soup.select(".result")
                print(f"Found {len(results)} raw results.")
                
                for r in results[:5]:
                    title_elem = r.select_one(".result__title .result__a")
                    snippet_elem = r.select_one(".result__snippet")
                    url_elem = r.select_one(".result__url")
                    
                    if title_elem and snippet_elem:
                        title = title_elem.get_text(strip=True)
                        snippet = snippet_elem.get_text(strip=True)
                        link = url_elem.get_text(strip=True) if url_elem else "No Link"
                        print(f"- {title}: {snippet[:60]}... [{link}]")
            else:
                print(f"Failed with status {resp.status_code}")
                print(resp.text[:500])
                
    except Exception as e:
        print(f"Scraper Exception: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(scraper())
