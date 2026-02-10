import aiohttp
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from backend.ingestion.base import BaseCollector
from backend.utils.config import settings


# FRED series IDs for Latin American economic indicators
FRED_SERIES = {
    "BRA": {
        "gdp_growth": "NYGDPMKTPKDZBRAICPEN",
        "inflation": "FPCPITOTLZGBRA",
        "unemployment": "SLUEM1524ZSBRA",
        "interest_rate": "INTDSRBRAM193N",
    },
    "MEX": {
        "gdp_growth": "NYGDPMKTPKDZMEX",
        "inflation": "FPCPITOTLZGMEX",
        "unemployment": "SLUEM1524ZSMEX",
        "interest_rate": "INTDSRMEXM193N",
    },
    "ARG": {
        "gdp_growth": "NYGDPMKTPKDZARG",
        "inflation": "FPCPITOTLZGARG",
    },
    "COL": {
        "gdp_growth": "NYGDPMKTPKDZCOL",
        "inflation": "FPCPITOTLZGCOL",
    },
    "CHL": {
        "gdp_growth": "NYGDPMKTPKDZCHL",
        "inflation": "FPCPITOTLZGCHL",
    },
    "PER": {
        "gdp_growth": "NYGDPMKTPKDZPER",
        "inflation": "FPCPITOTLZGPER",
    },
}

# Global indicators relevant to Latin America
GLOBAL_INDICATORS = {
    "us_fed_rate": "FEDFUNDS",
    "oil_price": "DCOILWTICO",
    "copper_price": "PCOPPUSDM",
    "soybean_price": "PSOYBUSDQ",
    "vix": "VIXCLS",
    "dxy": "DTWEXBGS",
    "us_10y": "DGS10",
}


class EconomicDataCollector(BaseCollector):
    """Collects economic indicators from FRED and other APIs."""

    def __init__(self):
        super().__init__("economic_data")
        self.fred_api_key = settings.fred_api_key
        self.fred_base_url = "https://api.stlouisfed.org/fred"

    async def collect(
        self,
        country_code: Optional[str] = None,
        include_global: bool = True,
    ) -> List[Dict[str, Any]]:
        """Collect economic data from FRED API."""
        if not self.fred_api_key:
            self.logger.warning("FRED API key not configured, returning empty results")
            return []

        results = []
        series_to_fetch = {}

        # Country-specific series
        if country_code and country_code in FRED_SERIES:
            for name, series_id in FRED_SERIES[country_code].items():
                series_to_fetch[f"{country_code}_{name}"] = {
                    "series_id": series_id,
                    "country_code": country_code,
                    "indicator_type": name,
                }
        elif not country_code:
            for cc, indicators in FRED_SERIES.items():
                for name, series_id in indicators.items():
                    series_to_fetch[f"{cc}_{name}"] = {
                        "series_id": series_id,
                        "country_code": cc,
                        "indicator_type": name,
                    }

        # Global indicators
        if include_global:
            for name, series_id in GLOBAL_INDICATORS.items():
                series_to_fetch[f"GLOBAL_{name}"] = {
                    "series_id": series_id,
                    "country_code": None,
                    "indicator_type": name,
                }

        async with aiohttp.ClientSession() as session:
            for key, info in series_to_fetch.items():
                try:
                    data = await self._fetch_fred_series(
                        session, info["series_id"]
                    )
                    for obs in data:
                        results.append({
                            "country_code": info["country_code"],
                            "indicator_type": info["indicator_type"],
                            "value": obs["value"],
                            "date": obs["date"],
                            "source": f"FRED:{info['series_id']}",
                        })
                except Exception as e:
                    self.logger.error(f"Failed to fetch {key}: {e}")

        return results

    async def _fetch_fred_series(
        self,
        session: aiohttp.ClientSession,
        series_id: str,
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        """Fetch a single FRED time series."""
        params = {
            "series_id": series_id,
            "api_key": self.fred_api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit,
        }
        async with session.get(
            f"{self.fred_base_url}/series/observations", params=params
        ) as resp:
            if resp.status != 200:
                raise Exception(f"FRED API error: {resp.status}")
            data = await resp.json()
            observations = []
            for obs in data.get("observations", []):
                if obs.get("value") and obs["value"] != ".":
                    observations.append({
                        "date": obs["date"],
                        "value": float(obs["value"]),
                    })
            return observations

    async def validate(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate economic data points."""
        validated = []
        for item in data:
            if item.get("value") is not None and item.get("indicator_type"):
                validated.append(item)
        return validated
