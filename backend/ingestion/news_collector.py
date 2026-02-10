import aiohttp
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from backend.ingestion.base import BaseCollector
from backend.utils.config import settings


# Latin American country keywords for filtering
LATAM_COUNTRIES = {
    "ARG": ["argentina", "buenos aires"],
    "BOL": ["bolivia", "la paz"],
    "BRA": ["brazil", "brasil", "brasilia", "são paulo"],
    "CHL": ["chile", "santiago"],
    "COL": ["colombia", "bogotá", "bogota"],
    "CRI": ["costa rica", "san josé"],
    "CUB": ["cuba", "havana", "habana"],
    "DOM": ["dominican republic", "república dominicana", "santo domingo"],
    "ECU": ["ecuador", "quito"],
    "SLV": ["el salvador", "san salvador"],
    "GTM": ["guatemala"],
    "HND": ["honduras", "tegucigalpa"],
    "MEX": ["mexico", "méxico", "ciudad de méxico"],
    "NIC": ["nicaragua", "managua"],
    "PAN": ["panama", "panamá"],
    "PRY": ["paraguay", "asunción"],
    "PER": ["peru", "perú", "lima"],
    "URY": ["uruguay", "montevideo"],
    "VEN": ["venezuela", "caracas"],
    "GUY": ["guyana", "georgetown"],
    "SUR": ["suriname", "paramaribo"],
}

CRISIS_KEYWORDS = [
    "crisis", "protest", "coup", "default", "inflation", "devaluation",
    "earthquake", "hurricane", "drought", "sanctions", "military",
    "election fraud", "corruption", "impeachment", "emergency",
    "shortage", "blackout", "cyberattack", "border conflict",
    "protesta", "golpe", "emergencia", "escasez", "apagón",
]


class NewsCollector(BaseCollector):
    """Collects news articles from NewsAPI related to Latin American crises."""

    def __init__(self):
        super().__init__("news_collector")
        self.api_key = settings.news_api_key
        self.base_url = "https://newsapi.org/v2"

    async def collect(
        self,
        country_code: Optional[str] = None,
        days_back: int = 7,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Collect news articles from NewsAPI."""
        if not self.api_key:
            self.logger.warning("NewsAPI key not configured, returning empty results")
            return []

        from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        # Build query
        if country_code and country_code in LATAM_COUNTRIES:
            keywords = LATAM_COUNTRIES[country_code]
            query = " OR ".join(f'"{kw}"' for kw in keywords)
        else:
            query = " OR ".join(f'"{kw}"' for kw in CRISIS_KEYWORDS[:10])

        params = {
            "q": query,
            "from": from_date,
            "sortBy": "relevancy",
            "pageSize": min(page_size, 100),
            "language": "en",
            "apiKey": self.api_key,
        }

        articles = []
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/everything", params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    articles = data.get("articles", [])
                else:
                    self.logger.error(f"NewsAPI returned status {resp.status}")

            # Also collect Spanish-language news
            params["language"] = "es"
            async with session.get(f"{self.base_url}/everything", params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    articles.extend(data.get("articles", []))

        return articles

    async def validate(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and normalize news articles."""
        validated = []
        for article in data:
            if not article.get("title") or article["title"] == "[Removed]":
                continue
            validated.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "content": article.get("content", ""),
                "source": article.get("source", {}).get("name", "unknown"),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
                "author": article.get("author", ""),
            })
        return validated

    def classify_country(self, text: str) -> List[str]:
        """Identify which countries an article relates to."""
        text_lower = text.lower()
        matches = []
        for code, keywords in LATAM_COUNTRIES.items():
            if any(kw in text_lower for kw in keywords):
                matches.append(code)
        return matches
