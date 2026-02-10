from typing import List, Optional
from fastapi import APIRouter, Query
from backend.api.models.schemas import Domain
from backend.api.routes.countries import LATAM_COUNTRIES, SAMPLE_SCORES
from backend.modeling.risk_scoring import RiskScorer

router = APIRouter()
scorer = RiskScorer()

DOMAIN_DESCRIPTIONS = {
    "political": {
        "name": "Political-Institutional",
        "description": "Monitors institutional erosion, democratic backsliding, political instability, and governance failures",
        "key_indicators": ["Democracy Index", "Corruption Perception Index", "Rule of Law Index", "Protest Frequency", "Judicial Impunity Rate"],
    },
    "economic": {
        "name": "Economic-Financial",
        "description": "Tracks sovereign debt risk, inflation, currency stability, capital flows, and banking sector health",
        "key_indicators": ["Inflation Rate", "Debt/GDP Ratio", "Foreign Reserves", "Bond Spreads", "Currency Stability"],
    },
    "supply_chain": {
        "name": "Supply Chain",
        "description": "Monitors port congestion, shipping disruptions, critical resource availability, and logistics bottlenecks",
        "key_indicators": ["Port Congestion Index", "Container Availability", "Freight Rates", "Inventory Levels", "Lead Times"],
    },
    "geopolitical": {
        "name": "Geopolitical-Strategic",
        "description": "Tracks territorial disputes, great power competition, military buildups, and diplomatic incidents",
        "key_indicators": ["Military Expenditure", "Diplomatic Incidents", "FDI Flows by Origin", "Trade Dependencies", "Arms Imports"],
    },
    "climate": {
        "name": "Climate-Environmental",
        "description": "Monitors extreme weather, drought, deforestation, water stress, and environmental tipping points",
        "key_indicators": ["Precipitation Anomalies", "Reservoir Levels", "Crop Yield Deviations", "Deforestation Rate", "Temperature Extremes"],
    },
    "technology": {
        "name": "Technology-Digital",
        "description": "Tracks cyber threats, internet freedom, digital infrastructure vulnerabilities, and information warfare",
        "key_indicators": ["Internet Freedom Score", "Cyber Resilience Index", "Data Breach Incidents", "Digital Infrastructure Age"],
    },
}


@router.get("/domains")
async def list_domains():
    """List all monitored risk domains with descriptions."""
    return DOMAIN_DESCRIPTIONS


@router.get("/domains/{domain}")
async def analyze_domain(
    domain: str,
    countries: Optional[List[str]] = Query(None),
):
    """Cross-country analysis of a specific risk domain."""
    if domain not in DOMAIN_DESCRIPTIONS:
        valid = list(DOMAIN_DESCRIPTIONS.keys())
        return {"error": f"Unknown domain '{domain}'. Valid domains: {valid}"}

    domain_info = DOMAIN_DESCRIPTIONS[domain]
    country_scores = []

    target_countries = {c.upper() for c in countries} if countries else set(LATAM_COUNTRIES.keys())

    for code in target_countries:
        if code not in LATAM_COUNTRIES:
            continue
        scores = SAMPLE_SCORES.get(code, {})
        domain_score = scores.get(domain, 0)
        country_scores.append({
            "country_code": code,
            "country_name": LATAM_COUNTRIES[code]["name"],
            "score": domain_score,
            "level": scorer.score_to_level(domain_score),
        })

    country_scores.sort(key=lambda x: x["score"], reverse=True)
    all_scores = [c["score"] for c in country_scores if c["score"] > 0]

    return {
        "domain": domain,
        **domain_info,
        "regional_average": round(sum(all_scores) / len(all_scores), 1) if all_scores else 0,
        "countries": country_scores,
        "highest_risk": country_scores[0] if country_scores else None,
        "distribution": {
            "critical": sum(1 for c in country_scores if c["score"] > 70),
            "elevated": sum(1 for c in country_scores if 50 < c["score"] <= 70),
            "moderate": sum(1 for c in country_scores if 30 < c["score"] <= 50),
            "low": sum(1 for c in country_scores if c["score"] <= 30),
        },
    }
