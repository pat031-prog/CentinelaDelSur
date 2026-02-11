
import asyncio
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("debug_search")

async def test_ddg():
    print("\n--- Testing DuckDuckGo ---")
    try:
        from duckduckgo_search import DDGS
        print("Imported DDGS successfully.")
        
        def _search():
            with DDGS() as ddgs:
                # Simple search
                return list(ddgs.text("Argentina inflation crisis", max_results=3))
        
        results = await asyncio.to_thread(_search)
        print(f"DDGS returned {len(results)} results.")
        for r in results:
            print(f"- {r.get('title')}: {r.get('body')[:50]}...")
            
    except Exception as e:
        print(f"DDGS FAILED: {e}")
        import traceback
        traceback.print_exc()

async def test_google_python():
    print("\n--- Testing googlesearch-python ---")
    try:
        from googlesearch import search
        print("Imported googlesearch successfully.")
        
        def _search():
            # advanced=True returns objects with title/description
            return list(search("Argentina inflation crisis", num_results=3, advanced=True))
            
        results = await asyncio.to_thread(_search)
        print(f"GoogleSearch returned {len(results)} results.")
        for r in results:
            print(f"- {r.title}: {r.description[:50]}...")
            
    except Exception as e:
        print(f"GoogleSearch FAILED: {e}")
        traceback.print_exc()

async def main():
    await test_ddg()
    await test_google_python()

if __name__ == "__main__":
    import traceback
    asyncio.run(main())
