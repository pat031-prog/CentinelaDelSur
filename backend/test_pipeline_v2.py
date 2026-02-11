import asyncio
import sys
import os

# Add project root to sys.path (parent of backend)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.intelligence.pipeline import run_pipeline

scores = {
    "political": 65.0,
    "economic": 70.0,
    "supply_chain": 40.0,
    "technology": 30.0,
    "geopolitical": 50.0,
    "climate": 20.0
}

async def run():
    print(">>> STARTING PIPELINE V2 TEST...")
    try:
        res = await run_pipeline(
            "ARG", "Argentina", scores
        )
        print("\n>>> PIPELINE SUCCESS!")
        print(f"Final Score: {res['final_score']}")
        print(f"Report: {res['report_text'][:200]}...")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
