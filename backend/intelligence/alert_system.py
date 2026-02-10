from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.utils.logger import logger


# Alert trigger conditions
ALERT_RULES = [
    {
        "name": "rapid_risk_increase",
        "description": "Risk score increased by >15 points in 7 days",
        "condition": lambda current, previous: current - previous > 15,
        "level": "red",
    },
    {
        "name": "critical_threshold",
        "description": "Any domain score exceeds 85",
        "condition": lambda score, _: score > 85,
        "level": "black",
    },
    {
        "name": "multi_domain_elevation",
        "description": "3+ domains above 60",
        "condition": lambda elevated_count, _: elevated_count >= 3,
        "level": "orange",
    },
    {
        "name": "high_crisis_probability",
        "description": "30-day crisis probability exceeds 50%",
        "condition": lambda prob, _: prob > 0.5,
        "level": "red",
    },
]


class AlertSystem:
    """Manages crisis alerts and notifications.

    Evaluates risk conditions against defined rules and generates
    alerts when thresholds are exceeded.
    """

    def __init__(self):
        self.logger = logger.getChild("alert_system")
        self.active_alerts: List[Dict[str, Any]] = []

    def evaluate_country(
        self,
        country_code: str,
        domain_scores: Dict[str, float],
        previous_scores: Optional[Dict[str, float]] = None,
        crisis_probability_30d: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Evaluate alert conditions for a country.

        Returns list of triggered alerts.
        """
        new_alerts = []

        # Check rapid risk increase
        if previous_scores:
            for domain, current in domain_scores.items():
                previous = previous_scores.get(domain, current)
                if current - previous > 15:
                    new_alerts.append(self._create_alert(
                        country_code=country_code,
                        level="red",
                        domain=domain,
                        title=f"Rapid risk increase in {domain}",
                        description=f"{domain} risk score increased from {previous:.0f} to {current:.0f} "
                                   f"(+{current-previous:.0f} points)",
                        probability=None,
                    ))

        # Check critical thresholds
        for domain, score in domain_scores.items():
            if score > 85:
                new_alerts.append(self._create_alert(
                    country_code=country_code,
                    level="black",
                    domain=domain,
                    title=f"Critical threshold exceeded in {domain}",
                    description=f"{domain} risk score at {score:.0f} - systemic collapse risk",
                    probability=None,
                ))
            elif score > 70:
                new_alerts.append(self._create_alert(
                    country_code=country_code,
                    level="red",
                    domain=domain,
                    title=f"High risk in {domain}",
                    description=f"{domain} risk score at {score:.0f} - imminent crisis range",
                    probability=None,
                ))

        # Check multi-domain elevation
        elevated = sum(1 for s in domain_scores.values() if s > 60)
        if elevated >= 3:
            new_alerts.append(self._create_alert(
                country_code=country_code,
                level="orange",
                domain=None,
                title="Multi-domain risk elevation",
                description=f"{elevated} domains above 60 threshold - systemic stress detected",
                probability=None,
            ))

        # Check crisis probability
        if crisis_probability_30d > 0.5:
            level = "black" if crisis_probability_30d > 0.8 else "red"
            new_alerts.append(self._create_alert(
                country_code=country_code,
                level=level,
                domain=None,
                title="High crisis probability",
                description=f"30-day crisis probability at {crisis_probability_30d*100:.0f}%",
                probability=crisis_probability_30d,
            ))

        self.active_alerts.extend(new_alerts)
        return new_alerts

    def get_active_alerts(
        self,
        country_code: Optional[str] = None,
        level: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get filtered active alerts."""
        alerts = self.active_alerts

        if country_code:
            alerts = [a for a in alerts if a["country_code"] == country_code]
        if level:
            alerts = [a for a in alerts if a["alert_level"] == level]
        if domain:
            alerts = [a for a in alerts if a.get("domain") == domain]

        return sorted(alerts, key=lambda a: self._level_priority(a["alert_level"]), reverse=True)

    def resolve_alert(self, alert_id: int):
        """Mark an alert as resolved."""
        for alert in self.active_alerts:
            if alert.get("id") == alert_id:
                alert["is_active"] = False
                alert["resolved_at"] = datetime.utcnow().isoformat()
                break

    def _create_alert(
        self,
        country_code: str,
        level: str,
        domain: Optional[str],
        title: str,
        description: str,
        probability: Optional[float],
    ) -> Dict[str, Any]:
        """Create a new alert dict."""
        return {
            "id": len(self.active_alerts) + 1,
            "created_at": datetime.utcnow().isoformat(),
            "country_code": country_code,
            "alert_level": level,
            "domain": domain,
            "title": title,
            "description": description,
            "probability": probability,
            "is_active": True,
            "resolved_at": None,
        }

    def _level_priority(self, level: str) -> int:
        """Convert alert level to numeric priority."""
        priorities = {"green": 0, "yellow": 1, "orange": 2, "red": 3, "black": 4}
        return priorities.get(level, 0)
