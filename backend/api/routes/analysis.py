from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from backend.api.models.schemas import AnalysisRequest, CascadeSimulationRequest
from backend.modeling.risk_scoring import RiskScorer
from backend.modeling.scenario_generator import ScenarioGenerator
from backend.modeling.cascade_simulator import CascadeSimulator
from backend.intelligence.report_generator import ReportGenerator
from backend.api.routes.countries import LATAM_COUNTRIES, SAMPLE_SCORES

router = APIRouter()
scorer = RiskScorer()
scenario_gen = ScenarioGenerator()
cascade_sim = CascadeSimulator()
report_gen = ReportGenerator()


@router.post("/countries/{country_code}/analyze")
async def generate_deep_analysis(
    country_code: str,
    request: AnalysisRequest,
):
    """Generate deep analysis for a country using all available models."""
    country_code = country_code.upper()
    if country_code not in LATAM_COUNTRIES:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")

    info = LATAM_COUNTRIES[country_code]
    domain_scores = SAMPLE_SCORES.get(country_code, {
        "political": 30, "economic": 30, "supply_chain": 25,
        "geopolitical": 25, "climate": 30, "technology": 20,
    })

    # Filter by requested domains
    if request.domains:
        domain_scores = {
            d: s for d, s in domain_scores.items()
            if d in [dom.value for dom in request.domains]
        }

    # Calculate risk
    risk = scorer.calculate_country_risk(domain_scores)

    # Generate scenarios
    dominant_domain = max(domain_scores, key=domain_scores.get) if domain_scores else "political"
    scenarios = scenario_gen.generate_scenarios(
        country_code, dominant_domain, risk["score"], domain_scores
    )

    # Generate text report
    signals = [
        {"domain": d, "title": f"Elevated risk in {d}", "severity": "high" if s > 60 else "medium", "trend": "worsening" if s > 50 else "stable"}
        for d, s in domain_scores.items() if s > 40
    ]

    # Try to use AI Analyst for deep report
    try:
        from backend.intelligence.ai_analyst import get_analyst
        analyst = get_analyst()
        
        # Determine events (mock for now, should come from DB)
        events = []
        indicators = []
        
        report = await analyst.generate_country_report(
            country_code=country_code,
            country_name=info["name"],
            risk_scores=risk,
            indicators={}, # Populate with real data eventually
            events=events
        )
    except Exception as e:
        # Fallback to template report if AI fails or not configured
        print(f"AI Analysis failed: {e}")
        report = report_gen.generate_text_report(
            country_code=country_code,
            country_name=info["name"],
            domain_scores=domain_scores,
            trends={d: "worsening" if s > 50 else "stable" for d, s in domain_scores.items()},
            signals=signals,
        )

    return {
        "country_code": country_code,
        "country_name": info["name"],
        "analysis_depth": request.depth,
        "timestamp": datetime.utcnow().isoformat(),
        "risk_assessment": risk,
        "scenarios": scenarios,
        "report_text": report,
    }


@router.post("/scenarios/simulate")
async def simulate_cascade(request: CascadeSimulationRequest):
    """Simulate crisis cascades from a trigger event."""
    country_code = request.country_code.upper()
    if country_code not in LATAM_COUNTRIES:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")

    current_scores = SAMPLE_SCORES.get(country_code, {
        "political": 30, "economic": 30, "supply_chain": 25,
        "geopolitical": 25, "climate": 30, "technology": 20,
    })

    # Determine initial domain from trigger event text
    trigger_lower = request.trigger_event.lower()
    domain_keywords = {
        "political": ["election", "coup", "protest", "government", "president"],
        "economic": ["default", "inflation", "debt", "currency", "recession"],
        "supply_chain": ["port", "shipping", "shortage", "supply", "canal"],
        "geopolitical": ["war", "conflict", "border", "military", "sanctions"],
        "climate": ["drought", "hurricane", "earthquake", "flood", "fire"],
        "technology": ["cyber", "hack", "outage", "internet", "blackout"],
    }

    initial_domain = "political"
    for domain, keywords in domain_keywords.items():
        if any(kw in trigger_lower for kw in keywords):
            initial_domain = domain
            break

    # Run cascade simulation
    result = cascade_sim.simulate(
        initial_domain=initial_domain,
        shock_magnitude=request.parameters.get("shock_magnitude", 30),
        current_scores=current_scores,
        time_horizon_days=request.time_horizon_days,
    )

    # Identify intervention points
    interventions = cascade_sim.identify_intervention_points(result)

    return {
        "country_code": country_code,
        "trigger_event": request.trigger_event,
        "initial_domain": initial_domain,
        "cascade_result": result,
        "intervention_points": interventions,
    }


@router.get("/regional/latam")
async def regional_overview():
    """Overview of systemic risk across all Latin America."""
    country_risks = []

    for code, info in LATAM_COUNTRIES.items():
        domain_scores = SAMPLE_SCORES.get(code, {})
        if domain_scores:
            risk = scorer.calculate_composite_score(domain_scores)
        else:
            risk = {"score": 25.0, "level": "green"}

        country_risks.append({
            "code": code,
            "name": info["name"],
            "region": info["region"],
            "risk_score": risk["score"],
            "risk_level": risk["level"],
            "domain_scores": domain_scores,
        })

    # Sort by risk
    country_risks.sort(key=lambda x: x["risk_score"], reverse=True)

    # Regional aggregates
    all_scores = [c["risk_score"] for c in country_risks if c["risk_score"] > 0]

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_countries": len(LATAM_COUNTRIES),
        "regional_risk_score": round(sum(all_scores) / len(all_scores), 1) if all_scores else 0,
        "countries_by_risk": country_risks,
        "top_5_at_risk": country_risks[:5],
        "risk_distribution": {
            "black": sum(1 for c in country_risks if c["risk_level"] == "black"),
            "red": sum(1 for c in country_risks if c["risk_level"] == "red"),
            "orange": sum(1 for c in country_risks if c["risk_level"] == "orange"),
            "yellow": sum(1 for c in country_risks if c["risk_level"] == "yellow"),
            "green": sum(1 for c in country_risks if c["risk_level"] == "green"),
        },
    }


@router.get("/historical/crises")
async def search_historical_crises(
    crisis_type: Optional[str] = None,
    country_code: Optional[str] = None,
    year_from: Optional[int] = None,
):
    """Search historical crises for pattern matching."""
    crises = [
        {"country_code": "ARG", "year": 2001, "crisis_type": "economic_default", "description": "Sovereign debt default, banking crisis, currency devaluation, social unrest", "outcome": {"recovery_years": 3, "gdp_loss": -11}},
        {"country_code": "VEN", "year": 2014, "crisis_type": "economic_collapse", "description": "Oil price crash triggers economic collapse, hyperinflation, mass migration", "outcome": {"recovery_years": None, "gdp_loss": -75}},
        {"country_code": "PER", "year": 2020, "crisis_type": "political_crisis", "description": "Rapid succession of presidents, institutional vacuum, social protests", "outcome": {"recovery_years": 2, "gdp_loss": -11}},
        {"country_code": "CHL", "year": 2019, "crisis_type": "social_unrest", "description": "Mass protests against inequality, constitutional process initiated", "outcome": {"recovery_years": 2, "gdp_loss": -6}},
        {"country_code": "ECU", "year": 2019, "crisis_type": "social_unrest", "description": "Fuel subsidy removal triggers indigenous-led protests, state of emergency", "outcome": {"recovery_years": 1, "gdp_loss": -1}},
        {"country_code": "BRA", "year": 2015, "crisis_type": "political_economic", "description": "Impeachment crisis combined with deep recession and corruption scandal", "outcome": {"recovery_years": 3, "gdp_loss": -7}},
        {"country_code": "URY", "year": 2002, "crisis_type": "banking_crisis", "description": "Banking system collapse triggered by Argentine contagion", "outcome": {"recovery_years": 2, "gdp_loss": -11}},
        {"country_code": "MEX", "year": 1994, "crisis_type": "currency_crisis", "description": "Tequila crisis - peso devaluation, capital flight, banking crisis", "outcome": {"recovery_years": 2, "gdp_loss": -6}},
    ]

    if crisis_type:
        crises = [c for c in crises if crisis_type.lower() in c["crisis_type"].lower()]
    if country_code:
        crises = [c for c in crises if c["country_code"] == country_code.upper()]
    if year_from:
        crises = [c for c in crises if c["year"] >= year_from]

    return crises
