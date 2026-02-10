from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.api.models.schemas import (
    CountryOverview, Domain, IndicatorResponse, EventResponse
)
from backend.modeling.risk_scoring import RiskScorer

router = APIRouter()
scorer = RiskScorer()

# In-memory data store for demo (replace with DB queries in production)
LATAM_COUNTRIES = {
    "ARG": {"name": "Argentina", "name_es": "Argentina", "region": "South America", "subregion": "Southern Cone", "capital": "Buenos Aires", "population": 46010000, "gdp_usd": 641000000000},
    "BOL": {"name": "Bolivia", "name_es": "Bolivia", "region": "South America", "subregion": "Andean", "capital": "La Paz", "population": 12080000, "gdp_usd": 44000000000},
    "BRA": {"name": "Brazil", "name_es": "Brasil", "region": "South America", "subregion": "Atlantic", "capital": "Brasilia", "population": 214300000, "gdp_usd": 1920000000000},
    "CHL": {"name": "Chile", "name_es": "Chile", "region": "South America", "subregion": "Southern Cone", "capital": "Santiago", "population": 19490000, "gdp_usd": 301000000000},
    "COL": {"name": "Colombia", "name_es": "Colombia", "region": "South America", "subregion": "Andean", "capital": "Bogota", "population": 51870000, "gdp_usd": 343000000000},
    "CRI": {"name": "Costa Rica", "name_es": "Costa Rica", "region": "Central America", "subregion": "Central America", "capital": "San Jose", "population": 5150000, "gdp_usd": 68400000000},
    "CUB": {"name": "Cuba", "name_es": "Cuba", "region": "Caribbean", "subregion": "Caribbean", "capital": "Havana", "population": 11260000, "gdp_usd": 107000000000},
    "DOM": {"name": "Dominican Republic", "name_es": "Republica Dominicana", "region": "Caribbean", "subregion": "Caribbean", "capital": "Santo Domingo", "population": 11120000, "gdp_usd": 113000000000},
    "ECU": {"name": "Ecuador", "name_es": "Ecuador", "region": "South America", "subregion": "Andean", "capital": "Quito", "population": 18000000, "gdp_usd": 115000000000},
    "SLV": {"name": "El Salvador", "name_es": "El Salvador", "region": "Central America", "subregion": "Central America", "capital": "San Salvador", "population": 6520000, "gdp_usd": 32490000000},
    "GTM": {"name": "Guatemala", "name_es": "Guatemala", "region": "Central America", "subregion": "Central America", "capital": "Guatemala City", "population": 17610000, "gdp_usd": 95000000000},
    "GUY": {"name": "Guyana", "name_es": "Guyana", "region": "South America", "subregion": "Caribbean", "capital": "Georgetown", "population": 805000, "gdp_usd": 14720000000},
    "HND": {"name": "Honduras", "name_es": "Honduras", "region": "Central America", "subregion": "Central America", "capital": "Tegucigalpa", "population": 10280000, "gdp_usd": 31720000000},
    "MEX": {"name": "Mexico", "name_es": "Mexico", "region": "North America", "subregion": "North America", "capital": "Mexico City", "population": 128900000, "gdp_usd": 1322000000000},
    "NIC": {"name": "Nicaragua", "name_es": "Nicaragua", "region": "Central America", "subregion": "Central America", "capital": "Managua", "population": 6950000, "gdp_usd": 15670000000},
    "PAN": {"name": "Panama", "name_es": "Panama", "region": "Central America", "subregion": "Central America", "capital": "Panama City", "population": 4380000, "gdp_usd": 76520000000},
    "PRY": {"name": "Paraguay", "name_es": "Paraguay", "region": "South America", "subregion": "Southern Cone", "capital": "Asuncion", "population": 7220000, "gdp_usd": 42960000000},
    "PER": {"name": "Peru", "name_es": "Peru", "region": "South America", "subregion": "Andean", "capital": "Lima", "population": 33720000, "gdp_usd": 242630000000},
    "URY": {"name": "Uruguay", "name_es": "Uruguay", "region": "South America", "subregion": "Southern Cone", "capital": "Montevideo", "population": 3490000, "gdp_usd": 71180000000},
    "VEN": {"name": "Venezuela", "name_es": "Venezuela", "region": "South America", "subregion": "Andean", "capital": "Caracas", "population": 28440000, "gdp_usd": 92200000000},
}

# Sample domain scores for demo
SAMPLE_SCORES = {
    "ARG": {"political": 55, "economic": 75, "supply_chain": 40, "geopolitical": 30, "climate": 35, "technology": 25},
    "BRA": {"political": 45, "economic": 40, "supply_chain": 30, "geopolitical": 35, "climate": 55, "technology": 30},
    "CHL": {"political": 35, "economic": 30, "supply_chain": 25, "geopolitical": 20, "climate": 40, "technology": 20},
    "COL": {"political": 50, "economic": 45, "supply_chain": 35, "geopolitical": 45, "climate": 35, "technology": 25},
    "CUB": {"political": 70, "economic": 80, "supply_chain": 65, "geopolitical": 55, "climate": 40, "technology": 60},
    "ECU": {"political": 55, "economic": 50, "supply_chain": 40, "geopolitical": 35, "climate": 40, "technology": 30},
    "GUY": {"political": 40, "economic": 35, "supply_chain": 30, "geopolitical": 60, "climate": 35, "technology": 35},
    "MEX": {"political": 50, "economic": 40, "supply_chain": 35, "geopolitical": 45, "climate": 45, "technology": 30},
    "NIC": {"political": 75, "economic": 60, "supply_chain": 45, "geopolitical": 50, "climate": 40, "technology": 50},
    "PER": {"political": 60, "economic": 45, "supply_chain": 30, "geopolitical": 25, "climate": 45, "technology": 25},
    "VEN": {"political": 85, "economic": 90, "supply_chain": 70, "geopolitical": 65, "climate": 35, "technology": 55},
}


@router.get("/countries")
async def list_countries(
    region: Optional[str] = None,
    min_risk: Optional[int] = None,
):
    """List all monitored countries with optional filters."""
    results = []
    for code, info in LATAM_COUNTRIES.items():
        if region and info["region"].lower() != region.lower():
            continue

        domain_scores = SAMPLE_SCORES.get(code, {})
        risk = scorer.calculate_composite_score(domain_scores) if domain_scores else {"score": 0, "level": "green"}

        if min_risk and risk["score"] < min_risk:
            continue

        results.append({
            "code": code,
            **info,
            "current_risk_score": risk["score"],
            "current_risk_level": risk["level"],
        })

    return sorted(results, key=lambda x: x["current_risk_score"], reverse=True)


@router.get("/countries/{country_code}")
async def get_country_overview(country_code: str):
    """Get comprehensive overview of a country."""
    country_code = country_code.upper()
    if country_code not in LATAM_COUNTRIES:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")

    info = LATAM_COUNTRIES[country_code]
    domain_scores = SAMPLE_SCORES.get(country_code, {
        "political": 30, "economic": 30, "supply_chain": 25,
        "geopolitical": 25, "climate": 30, "technology": 20,
    })

    risk = scorer.calculate_country_risk(domain_scores)

    return {
        "code": country_code,
        **info,
        "risk_assessment": risk,
    }


@router.get("/countries/{country_code}/risk")
async def get_country_risk(
    country_code: str,
    domains: Optional[List[str]] = Query(None),
):
    """Get risk scores for a country, optionally filtered by domain."""
    country_code = country_code.upper()
    if country_code not in LATAM_COUNTRIES:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")

    all_scores = SAMPLE_SCORES.get(country_code, {})

    if domains:
        all_scores = {d: s for d, s in all_scores.items() if d in domains}

    risk = scorer.calculate_country_risk(all_scores)
    return risk


@router.get("/countries/{country_code}/indicators")
async def get_indicators(
    country_code: str,
    types: Optional[List[str]] = Query(None),
):
    """Get indicators for a country."""
    country_code = country_code.upper()
    if country_code not in LATAM_COUNTRIES:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")

    # Return sample indicators
    indicators = [
        {"time": datetime.utcnow().isoformat(), "country_code": country_code, "indicator_type": "inflation_yoy", "value": 4.5, "unit": "%", "source": "Central Bank"},
        {"time": datetime.utcnow().isoformat(), "country_code": country_code, "indicator_type": "gdp_growth", "value": 2.1, "unit": "%", "source": "FRED"},
        {"time": datetime.utcnow().isoformat(), "country_code": country_code, "indicator_type": "unemployment", "value": 7.2, "unit": "%", "source": "ILO"},
        {"time": datetime.utcnow().isoformat(), "country_code": country_code, "indicator_type": "debt_to_gdp", "value": 65.3, "unit": "%", "source": "IMF"},
        {"time": datetime.utcnow().isoformat(), "country_code": country_code, "indicator_type": "reserves_months", "value": 5.8, "unit": "months", "source": "Central Bank"},
    ]

    if types:
        indicators = [i for i in indicators if i["indicator_type"] in types]

    return indicators
