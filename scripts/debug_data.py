import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.intelligence.data_fetcher import get_country_context

async def main():
    print("Fetching context for Argentina (ARG)...")
    try:
        ctx = await get_country_context("ARG", "Argentina")
        print("\n=== RESULT ===\n")
        print(ctx)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
