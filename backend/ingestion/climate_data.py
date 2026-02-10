import aiohttp
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from backend.ingestion.base import BaseCollector


# Capital coordinates for weather data
LATAM_CAPITALS = {
    "ARG": {"city": "Buenos Aires", "lat": -34.60, "lon": -58.38},
    "BOL": {"city": "La Paz", "lat": -16.50, "lon": -68.15},
    "BRA": {"city": "Brasilia", "lat": -15.79, "lon": -47.88},
    "CHL": {"city": "Santiago", "lat": -33.45, "lon": -70.67},
    "COL": {"city": "Bogota", "lat": 4.71, "lon": -74.07},
    "CRI": {"city": "San Jose", "lat": 9.93, "lon": -84.08},
    "CUB": {"city": "Havana", "lat": 23.11, "lon": -82.37},
    "ECU": {"city": "Quito", "lat": -0.18, "lon": -78.47},
    "SLV": {"city": "San Salvador", "lat": 13.69, "lon": -89.19},
    "GTM": {"city": "Guatemala City", "lat": 14.63, "lon": -90.51},
    "HND": {"city": "Tegucigalpa", "lat": 14.07, "lon": -87.19},
    "MEX": {"city": "Mexico City", "lat": 19.43, "lon": -99.13},
    "NIC": {"city": "Managua", "lat": 12.11, "lon": -86.27},
    "PAN": {"city": "Panama City", "lat": 8.98, "lon": -79.52},
    "PRY": {"city": "Asuncion", "lat": -25.26, "lon": -57.58},
    "PER": {"city": "Lima", "lat": -12.05, "lon": -77.04},
    "URY": {"city": "Montevideo", "lat": -34.88, "lon": -56.17},
    "VEN": {"city": "Caracas", "lat": 10.49, "lon": -66.88},
}

# Critical environmental hotspots
HOTSPOTS = {
    "amazon_deforestation": {"lat": -3.0, "lon": -60.0, "radius_km": 500},
    "andean_glaciers": {"lat": -15.0, "lon": -70.0, "radius_km": 200},
    "central_america_dry_corridor": {"lat": 14.0, "lon": -88.0, "radius_km": 300},
    "parana_river_basin": {"lat": -25.0, "lon": -55.0, "radius_km": 400},
    "caribbean_hurricane_zone": {"lat": 18.0, "lon": -75.0, "radius_km": 600},
}


class ClimateDataCollector(BaseCollector):
    """Collects climate and environmental data for crisis monitoring.

    Uses Open-Meteo API (free, no key required) for weather data.
    Framework for NASA/ESA satellite data integration.
    """

    def __init__(self):
        super().__init__("climate_data")
        self.open_meteo_url = "https://api.open-meteo.com/v1"

    async def collect(
        self,
        country_code: Optional[str] = None,
        include_forecast: bool = True,
    ) -> List[Dict[str, Any]]:
        """Collect climate data from Open-Meteo API."""
        results = []

        targets = {}
        if country_code and country_code in LATAM_CAPITALS:
            targets[country_code] = LATAM_CAPITALS[country_code]
        else:
            targets = LATAM_CAPITALS

        async with aiohttp.ClientSession() as session:
            for code, location in targets.items():
                try:
                    data = await self._fetch_weather(
                        session, location["lat"], location["lon"],
                        include_forecast=include_forecast,
                    )
                    for item in data:
                        item["country_code"] = code
                        item["city"] = location["city"]
                        results.append(item)
                except Exception as e:
                    self.logger.error(f"Failed to fetch climate data for {code}: {e}")

        return results

    async def _fetch_weather(
        self,
        session: aiohttp.ClientSession,
        lat: float,
        lon: float,
        include_forecast: bool = True,
    ) -> List[Dict[str, Any]]:
        """Fetch weather data from Open-Meteo."""
        past_days = 30
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "past_days": past_days,
            "timezone": "auto",
        }
        if include_forecast:
            params["forecast_days"] = 7

        async with session.get(f"{self.open_meteo_url}/forecast", params=params) as resp:
            if resp.status != 200:
                raise Exception(f"Open-Meteo API error: {resp.status}")
            data = await resp.json()
            daily = data.get("daily", {})

            results = []
            dates = daily.get("time", [])
            temp_max = daily.get("temperature_2m_max", [])
            temp_min = daily.get("temperature_2m_min", [])
            precip = daily.get("precipitation_sum", [])

            for i, date in enumerate(dates):
                results.append({
                    "date": date,
                    "temperature_max": temp_max[i] if i < len(temp_max) else None,
                    "temperature_min": temp_min[i] if i < len(temp_min) else None,
                    "precipitation": precip[i] if i < len(precip) else None,
                    "source": "open-meteo",
                })

            return results

    async def validate(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate climate data points."""
        validated = []
        for item in data:
            if item.get("date") and (
                item.get("temperature_max") is not None
                or item.get("precipitation") is not None
            ):
                validated.append(item)
        return validated
