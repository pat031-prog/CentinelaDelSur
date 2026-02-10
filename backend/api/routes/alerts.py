from typing import Optional
from fastapi import APIRouter
from backend.intelligence.alert_system import AlertSystem
from backend.api.routes.countries import LATAM_COUNTRIES, SAMPLE_SCORES

router = APIRouter()
alert_system = AlertSystem()

# Generate initial alerts from sample data
for code, scores in SAMPLE_SCORES.items():
    alert_system.evaluate_country(
        country_code=code,
        domain_scores=scores,
    )


@router.get("/alerts")
async def get_active_alerts(
    country_code: Optional[str] = None,
    level: Optional[str] = None,
    domain: Optional[str] = None,
):
    """Get active alerts with optional filters."""
    if country_code:
        country_code = country_code.upper()

    alerts = alert_system.get_active_alerts(
        country_code=country_code,
        level=level,
        domain=domain,
    )

    return {
        "total": len(alerts),
        "alerts": alerts,
    }


@router.get("/alerts/summary")
async def get_alert_summary():
    """Get summary of all active alerts."""
    all_alerts = alert_system.get_active_alerts()

    by_level = {}
    by_country = {}

    for alert in all_alerts:
        level = alert["alert_level"]
        country = alert["country_code"]

        by_level[level] = by_level.get(level, 0) + 1
        by_country[country] = by_country.get(country, 0) + 1

    return {
        "total_active": len(all_alerts),
        "by_level": by_level,
        "by_country": dict(sorted(by_country.items(), key=lambda x: x[1], reverse=True)),
        "most_critical": all_alerts[:5] if all_alerts else [],
    }
