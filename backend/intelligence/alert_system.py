from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.utils.logger import logger


# Domain name translations
DOMAIN_ES = {
    "political": "Político",
    "economic": "Económico",
    "supply_chain": "Cadena de Suministro",
    "geopolitical": "Geopolítico",
    "climate": "Climático",
    "technology": "Tecnología",
}

# Country name lookup for source URLs  
COUNTRY_NAMES = {
    "ARG": "Argentina", "BOL": "Bolivia", "BRA": "Brasil", "CHL": "Chile",
    "COL": "Colombia", "CRI": "Costa Rica", "CUB": "Cuba", "DOM": "República Dominicana",
    "ECU": "Ecuador", "SLV": "El Salvador", "GTM": "Guatemala", "HTI": "Haití",
    "HND": "Honduras", "MEX": "México", "NIC": "Nicaragua", "PAN": "Panamá",
    "PRY": "Paraguay", "PER": "Perú", "URY": "Uruguay", "VEN": "Venezuela",
}


class AlertSystem:
    """Sistema de alertas de crisis con análisis editorial.

    Evalúa condiciones de riesgo y genera alertas con URLs de fuente
    y micro-análisis editorial en español.
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
        """Evalúa condiciones de alerta para un país."""
        new_alerts = []
        country_name = COUNTRY_NAMES.get(country_code, country_code)

        # Incremento rápido del riesgo
        if previous_scores:
            for domain, current in domain_scores.items():
                previous = previous_scores.get(domain, current)
                if current - previous > 15:
                    domain_es = DOMAIN_ES.get(domain, domain)
                    new_alerts.append(self._create_alert(
                        country_code=country_code,
                        level="red",
                        domain=domain,
                        title=f"Aumento rápido en riesgo {domain_es} — {country_name}",
                        description=f"El índice de riesgo {domain_es.lower()} se incrementó de {previous:.0f} a {current:.0f} "
                                   f"(+{current-previous:.0f} puntos en 7 días)",
                        editorial=f"La aceleración del deterioro en el dominio {domain_es.lower()} de {country_name} "
                                 f"sugiere una dinámica de crisis en formación. Un salto de {current-previous:.0f} puntos "
                                 f"en una semana es inusual y merece atención inmediata.",
                        source_url=self._build_source_url(country_name, domain),
                    ))

        # Umbrales críticos
        for domain, score in domain_scores.items():
            domain_es = DOMAIN_ES.get(domain, domain)
            if score > 85:
                new_alerts.append(self._create_alert(
                    country_code=country_code,
                    level="black",
                    domain=domain,
                    title=f"Umbral crítico superado en {domain_es} — {country_name}",
                    description=f"Índice {domain_es.lower()} en {score:.0f}/100 — riesgo de colapso sistémico",
                    editorial=f"Con un índice de {score:.0f}, {country_name} ha cruzado el umbral de colapso sistémico "
                             f"en el dominio {domain_es.lower()}. Las instituciones de contención han sido superadas. "
                             f"Históricamente, niveles superiores a 85 preceden disrupciones mayores dentro de 30-60 días.",
                    source_url=self._build_source_url(country_name, domain),
                ))
            elif score > 70:
                new_alerts.append(self._create_alert(
                    country_code=country_code,
                    level="red",
                    domain=domain,
                    title=f"Riesgo elevado en {domain_es} — {country_name}",
                    description=f"Índice {domain_es.lower()} en {score:.0f}/100 — zona de crisis inminente",
                    editorial=f"El dominio {domain_es.lower()} de {country_name} se encuentra en la franja de crisis "
                             f"inminente ({score:.0f}/100). La ventana de intervención se cierra progresivamente.",
                    source_url=self._build_source_url(country_name, domain),
                ))

        # Elevación multi-dominio
        elevated = sum(1 for s in domain_scores.values() if s > 60)
        if elevated >= 3:
            elevated_domains = [DOMAIN_ES.get(d, d) for d, s in domain_scores.items() if s > 60]
            new_alerts.append(self._create_alert(
                country_code=country_code,
                level="orange",
                domain=None,
                title=f"Estrés sistémico multi-dominio — {country_name}",
                description=f"{elevated} dominios por encima del umbral 60: {', '.join(elevated_domains)}",
                editorial=f"La convergencia de presiones en {elevated} dominios simultáneos indica un estrés "
                         f"sistémico en {country_name} que trasciende un solo sector. Cuando múltiples dominios "
                         f"se deterioran en paralelo, el riesgo de contagio entre sectores se amplifica exponencialmente.",
                source_url=self._build_source_url(country_name, "crisis"),
            ))

        # Probabilidad de crisis alta
        if crisis_probability_30d > 0.5:
            level = "black" if crisis_probability_30d > 0.8 else "red"
            new_alerts.append(self._create_alert(
                country_code=country_code,
                level=level,
                domain=None,
                title=f"Alta probabilidad de crisis a 30 días — {country_name}",
                description=f"Probabilidad de crisis estimada en {crisis_probability_30d*100:.0f}% para los próximos 30 días",
                editorial=f"Los modelos predictivos de ATALAYA asignan una probabilidad del "
                         f"{crisis_probability_30d*100:.0f}% a una crisis sistémica en {country_name} dentro de 30 días. "
                         f"Este nivel requiere planes de contingencia activos.",
                source_url=self._build_source_url(country_name, "crisis"),
            ))

        self.active_alerts.extend(new_alerts)
        return new_alerts

    def get_active_alerts(
        self,
        country_code: Optional[str] = None,
        level: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Alertas activas con filtros opcionales."""
        alerts = self.active_alerts

        if country_code:
            alerts = [a for a in alerts if a["country_code"] == country_code]
        if level:
            alerts = [a for a in alerts if a["alert_level"] == level]
        if domain:
            alerts = [a for a in alerts if a.get("domain") == domain]

        return sorted(alerts, key=lambda a: self._level_priority(a["alert_level"]), reverse=True)

    def resolve_alert(self, alert_id: int):
        """Marcar alerta como resuelta."""
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
        editorial: str = "",
        source_url: str = "",
    ) -> Dict[str, Any]:
        """Crear nueva alerta con campos editoriales."""
        return {
            "id": len(self.active_alerts) + 1,
            "created_at": datetime.utcnow().isoformat(),
            "country_code": country_code,
            "alert_level": level,
            "domain": domain,
            "title": title,
            "description": description,
            "editorial": editorial,
            "source_url": source_url,
            "probability": None,
            "is_active": True,
            "resolved_at": None,
        }

    def _build_source_url(self, country_name: str, domain: str) -> str:
        """Generar URL de búsqueda de noticias como fuente."""
        from urllib.parse import quote
        domain_keywords = {
            "political": "política gobierno crisis",
            "economic": "economía finanzas deuda",
            "supply_chain": "cadena suministro logística",
            "geopolitical": "geopolítica relaciones internacionales",
            "climate": "clima medio ambiente desastre",
            "technology": "tecnología ciberseguridad",
            "crisis": "crisis riesgo",
        }
        keywords = domain_keywords.get(domain, "crisis riesgo")
        query = quote(f"{country_name} {keywords} 2026")
        return f"https://news.google.com/search?q={query}&hl=es-419&gl=MX&ceid=MX:es-419"

    def _level_priority(self, level: str) -> int:
        """Prioridad numérica del nivel de alerta."""
        priorities = {"green": 0, "yellow": 1, "orange": 2, "red": 3, "black": 4}
        return priorities.get(level, 0)
