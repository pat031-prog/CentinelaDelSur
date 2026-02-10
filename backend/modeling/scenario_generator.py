from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.utils.logger import logger


# Plantillas de escenarios basadas en patrones históricos
SCENARIO_TEMPLATES = {
    "economic_default": {
        "optimistic": "Acuerdo de reestructuración de deuda con acreedores. Programa del FMI estabiliza la economía. Retorno gradual a mercados internacionales.",
        "base": "Default parcial con pagos selectivos. Negociaciones extendidas con acreedores. Contracción del PIB del 3-5%. Presión cambiaria sostenida.",
        "pessimistic": "Default soberano total. Controles de capital. Estrés del sistema bancario. Contracción del PIB >10%. Fuga de inversión extranjera.",
        "collapse": "Colapso total del sistema financiero. Hiperinflación. Reemplazo de moneda. Descomposición social y saqueos generalizados.",
    },
    "political_crisis": {
        "optimistic": "Resolución constitucional. Nuevas elecciones programadas. Recuperación institucional gradual y diálogo nacional.",
        "base": "Inestabilidad política prolongada. Gobierno interino. Incertidumbre económica y parálisis legislativa.",
        "pessimistic": "Consolidación autoritaria. Retroceso democrático. Aislamiento internacional y sanciones económicas.",
        "collapse": "Fracaso estatal. Colapso institucional. Migración masiva. Contagio regional y posible intervención externa.",
    },
    "supply_chain_disruption": {
        "optimistic": "Rutas alternativas activadas. Interrupción temporal (2-4 semanas). Impacto económico mínimo.",
        "base": "Interrupción extendida (1-3 meses). Pico inflacionario. Escasez sectorial de insumos críticos.",
        "pessimistic": "Crisis prolongada (3-6 meses). Escasez crítica de bienes esenciales. Desaceleración industrial severa.",
        "collapse": "Fallo sistémico de cadena de suministro. Múltiples puntos de estrangulamiento bloqueados. Racionamiento obligatorio.",
    },
    "climate_disaster": {
        "optimistic": "Respuesta de emergencia rápida. Ayuda internacional movilizada. Infraestructura reconstruida en plazos razonables.",
        "base": "Daños significativos. Recuperación lenta. Pérdidas agrícolas considerables. Desplazamiento poblacional moderado.",
        "pessimistic": "Fallas en cascada. Colapso de infraestructura. Inseguridad alimentaria. Desplazamiento masivo de población.",
        "collapse": "Cambio de régimen ambiental permanente. Zonas inhabitables. Crisis de migración climática a nivel regional.",
    },
    "social_unrest": {
        "optimistic": "Concesiones gubernamentales. Proceso de diálogo. Desescalamiento gradual de tensiones.",
        "base": "Protestas sostenidas. Disrupciones económicas. Respuesta gubernamental parcial e insuficiente.",
        "pessimistic": "Represión violenta. Condena internacional. Parálisis económica y éxodo de capital.",
        "collapse": "Situación revolucionaria. Violencia estatal. Conflicto civil. Desestabilización regional.",
    },
}


class ScenarioGenerator:
    """Generates projected scenarios based on current risk state.

    Combines template-based scenarios with dynamic probability
    estimation from current indicators.
    """

    def __init__(self):
        self.logger = logger.getChild("scenario_generator")

    def generate_scenarios(
        self,
        country_code: str,
        dominant_risk_type: str,
        composite_score: float,
        domain_scores: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """Generate four scenarios (optimistic, base, pessimistic, collapse).

        Args:
            country_code: ISO country code
            dominant_risk_type: The most pressing risk type
            composite_score: Overall risk score (0-100)
            domain_scores: Per-domain risk scores
        """
        template_key = self._match_template(dominant_risk_type)
        template = SCENARIO_TEMPLATES.get(template_key, SCENARIO_TEMPLATES["political_crisis"])

        # Calculate scenario probabilities based on composite score
        probs = self._calculate_probabilities(composite_score)

        scenarios = []
        for scenario_type, prob in probs.items():
            scenarios.append({
                "country_code": country_code,
                "scenario_type": scenario_type,
                "title": f"{scenario_type.title()} Scenario - {dominant_risk_type.replace('_', ' ').title()}",
                "description": template[scenario_type],
                "probability": prob,
                "conditions": self._generate_conditions(scenario_type, domain_scores),
                "consequences": self._generate_consequences(scenario_type, composite_score),
                "timeframe": self._estimate_timeframe(scenario_type, composite_score),
                "created_at": datetime.utcnow().isoformat(),
            })

        return scenarios

    def _match_template(self, risk_type: str) -> str:
        """Match risk type to closest scenario template."""
        mappings = {
            "political": "political_crisis",
            "political_crisis": "political_crisis",
            "economic": "economic_default",
            "economic_crisis": "economic_default",
            "supply_chain": "supply_chain_disruption",
            "supply_chain_disruption": "supply_chain_disruption",
            "climate": "climate_disaster",
            "natural_disaster": "climate_disaster",
            "social_unrest": "social_unrest",
            "security_threat": "social_unrest",
            "geopolitical": "political_crisis",
            "technology": "supply_chain_disruption",
        }
        return mappings.get(risk_type, "political_crisis")

    def _calculate_probabilities(self, composite_score: float) -> Dict[str, float]:
        """Calculate scenario probabilities based on risk score."""
        if composite_score < 30:
            return {"optimistic": 0.60, "base": 0.30, "pessimistic": 0.08, "collapse": 0.02}
        elif composite_score < 50:
            return {"optimistic": 0.35, "base": 0.40, "pessimistic": 0.20, "collapse": 0.05}
        elif composite_score < 70:
            return {"optimistic": 0.15, "base": 0.35, "pessimistic": 0.35, "collapse": 0.15}
        elif composite_score < 85:
            return {"optimistic": 0.05, "base": 0.20, "pessimistic": 0.45, "collapse": 0.30}
        else:
            return {"optimistic": 0.02, "base": 0.10, "pessimistic": 0.38, "collapse": 0.50}

    def _generate_conditions(
        self, scenario_type: str, domain_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate conditions necessary for each scenario."""
        conditions = {
            "optimistic": {
                "requires": [
                    "Political will for reform",
                    "International support / cooperation",
                    "Key risk indicators must stabilize within 30 days",
                ],
                "critical_domains_must_improve": [
                    d for d, s in domain_scores.items() if s > 60
                ],
            },
            "base": {
                "requires": [
                    "Current trajectory continues",
                    "No major external shocks",
                    "Partial policy response",
                ],
                "assumes_stable": [
                    d for d, s in domain_scores.items() if 30 < s < 60
                ],
            },
            "pessimistic": {
                "requires": [
                    "Policy paralysis or wrong response",
                    "External shock amplifies internal weakness",
                    "Social trust continues eroding",
                ],
                "critical_domains": [
                    d for d, s in domain_scores.items() if s > 50
                ],
            },
            "collapse": {
                "requires": [
                    "Multiple simultaneous shocks",
                    "Complete institutional failure",
                    "Regional contagion effects",
                ],
                "all_domains_critical": [
                    d for d, s in domain_scores.items() if s > 70
                ],
            },
        }
        return conditions.get(scenario_type, {})

    def _generate_consequences(
        self, scenario_type: str, composite_score: float
    ) -> Dict[str, Any]:
        """Generate expected consequences for each scenario."""
        severity_map = {
            "optimistic": {"gdp_impact": "0 to -2%", "displacement": "minimal", "regional_contagion": "none"},
            "base": {"gdp_impact": "-2 to -5%", "displacement": "moderate", "regional_contagion": "limited"},
            "pessimistic": {"gdp_impact": "-5 to -15%", "displacement": "significant", "regional_contagion": "moderate"},
            "collapse": {"gdp_impact": ">-15%", "displacement": "mass", "regional_contagion": "severe"},
        }
        return severity_map.get(scenario_type, {})

    def _estimate_timeframe(self, scenario_type: str, composite_score: float) -> int:
        """Estimate timeframe in days for scenario to materialize."""
        base_timeframes = {
            "optimistic": 180,
            "base": 90,
            "pessimistic": 60,
            "collapse": 30,
        }
        base = base_timeframes.get(scenario_type, 90)

        # Higher risk scores compress timeframes
        if composite_score > 70:
            return max(7, int(base * 0.5))
        elif composite_score > 50:
            return max(14, int(base * 0.75))
        return base
