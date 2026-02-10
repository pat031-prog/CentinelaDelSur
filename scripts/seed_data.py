"""Seed script to populate the database with initial data.

Run with: python -m scripts.seed_data
"""

import asyncio
from datetime import datetime, timedelta
import random

from backend.api.models.database import async_session, init_db
from backend.api.models.database import Country, RiskScore, Indicator, Event, HistoricalCrisis
from backend.utils.logger import logger


LATAM_COUNTRIES = [
    ("ARG", "Argentina", "Argentina", "South America", "Southern Cone", "Buenos Aires", 46010000, 641000000000),
    ("BOL", "Bolivia", "Bolivia", "South America", "Andean", "La Paz", 12080000, 44000000000),
    ("BRA", "Brazil", "Brasil", "South America", "Atlantic", "Brasilia", 214300000, 1920000000000),
    ("CHL", "Chile", "Chile", "South America", "Southern Cone", "Santiago", 19490000, 301000000000),
    ("COL", "Colombia", "Colombia", "South America", "Andean", "Bogota", 51870000, 343000000000),
    ("MEX", "Mexico", "Mexico", "North America", "North America", "Mexico City", 128900000, 1322000000000),
    ("PER", "Peru", "Peru", "South America", "Andean", "Lima", 33720000, 242630000000),
    ("VEN", "Venezuela", "Venezuela", "South America", "Andean", "Caracas", 28440000, 92200000000),
]

DOMAINS = ["political", "economic", "supply_chain", "geopolitical", "climate", "technology"]


async def seed():
    """Seed the database with initial data."""
    logger.info("Starting database seed...")
    await init_db()

    async with async_session() as session:
        # Seed countries
        for code, name, name_es, region, subregion, capital, pop, gdp in LATAM_COUNTRIES:
            country = Country(
                code=code, name=name, name_es=name_es,
                region=region, subregion=subregion, capital=capital,
                population=pop, gdp_usd=gdp,
            )
            session.add(country)

        try:
            await session.commit()
            logger.info(f"Seeded {len(LATAM_COUNTRIES)} countries")
        except Exception:
            await session.rollback()
            logger.info("Countries already exist, skipping")

        # Seed risk scores (last 30 days)
        now = datetime.utcnow()
        scores_added = 0
        for code, *_ in LATAM_COUNTRIES:
            base_scores = {d: random.uniform(20, 70) for d in DOMAINS}
            for day in range(30):
                ts = now - timedelta(days=day)
                for domain in DOMAINS:
                    score = base_scores[domain] + random.uniform(-5, 5)
                    score = max(0, min(100, score))
                    level = (
                        "green" if score < 30 else
                        "yellow" if score < 50 else
                        "orange" if score < 70 else
                        "red" if score < 85 else "black"
                    )
                    rs = RiskScore(
                        time=ts, country_code=code, domain=domain,
                        score=round(score, 1), level=level,
                        confidence=round(random.uniform(0.6, 0.95), 2),
                    )
                    session.add(rs)
                    scores_added += 1

        await session.commit()
        logger.info(f"Seeded {scores_added} risk score data points")

    logger.info("Database seed complete")


if __name__ == "__main__":
    asyncio.run(seed())
