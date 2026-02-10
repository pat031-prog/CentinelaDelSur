from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.modeling.risk_scoring import RiskScorer
from backend.modeling.scenario_generator import ScenarioGenerator
from backend.modeling.cascade_simulator import CascadeSimulator
from backend.utils.logger import logger


LEVEL_LABELS = {
    "green": "Estable",
    "yellow": "Vigilancia",
    "orange": "Elevado",
    "red": "Crítico",
    "black": "Colapso",
}

DOMAIN_NAMES = {
    "political": "Político",
    "economic": "Económico",
    "supply_chain": "Cadena de Suministro",
    "geopolitical": "Geopolítico",
    "climate": "Climático",
    "technology": "Tecnología",
}


class ReportGenerator:
    """Generates formatted ATALAYA risk reports as Spanish markdown articles.
    
    This is the FALLBACK generator used when the AI analyst is unavailable.
    It produces a structured editorial-style report using template data.
    """

    def __init__(self):
        self.scorer = RiskScorer()
        self.scenario_gen = ScenarioGenerator()
        self.cascade_sim = CascadeSimulator()
        self.logger = logger.getChild("report_generator")

    def generate_text_report(
        self,
        country_code: str,
        country_name: str,
        domain_scores: Dict[str, float],
        trends: Dict[str, str],
        signals: List[Dict[str, Any]],
        indicators: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Generate a Spanish markdown editorial report (fallback template)."""

        risk = self.scorer.calculate_country_risk(domain_scores,
            trend=self._dominant_trend(trends))

        dominant_domain = max(domain_scores, key=domain_scores.get) if domain_scores else "political"
        scenarios = self.scenario_gen.generate_scenarios(
            country_code, dominant_domain, risk["score"], domain_scores
        )

        now = datetime.utcnow()
        months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        date_str = f"{now.day} de {months[now.month - 1]} {now.year}"
        level = LEVEL_LABELS.get(risk["level"], risk["level"])
        score = risk["score"]

        # Build the markdown article
        report = f"""# {country_name}: Evaluación de Riesgo Soberano — Nivel {level}

*Por ATALAYA Intelligence | {date_str} | Informe Automatizado*

## Resumen Ejecutivo

{country_name} ({country_code}) presenta actualmente un índice de fragilidad sistémica de **{score:.1f}/100**, clasificado como **{level}**. {self._interpret_score_es(score)}

El análisis cubre {len(domain_scores)} dominios de riesgo monitoreados. {self._dominant_insight(domain_scores, dominant_domain)} Este informe fue generado automáticamente por el sistema ATALAYA ante la indisponibilidad temporal del motor de inteligencia artificial.

## Anatomía del Riesgo

El índice compuesto de fragilidad integra múltiples dominios que, en conjunto, definen la estabilidad estructural del país. A continuación se presenta el desglose por cada dominio monitoreado:

"""
        # Domain breakdown
        for domain, score_val in sorted(domain_scores.items(), key=lambda x: x[1], reverse=True):
            domain_info = risk.get("domains", {}).get(domain, {})
            domain_level = LEVEL_LABELS.get(domain_info.get("level", "green"), "Estable")
            domain_name = DOMAIN_NAMES.get(domain, domain.replace("_", " ").title())
            trend = "Empeorando" if trends.get(domain) == "worsening" else "Estable" if trends.get(domain) == "stable" else "Mejorando"

            report += f"**{domain_name}** — {score_val:.1f}/100 ({domain_level}, {trend})\n\n"

        # Crisis probability
        cp = risk.get("crisis_probability", {})
        report += """## Probabilidad de Crisis

Las proyecciones probabilísticas del sistema indican los siguientes niveles de riesgo de crisis sistémica en los próximos meses:

"""
        for period, data in cp.items():
            period_labels = {
                "30_days": "30 días",
                "60_days": "60 días",
                "90_days": "90 días",
            }
            label = period_labels.get(period, period.replace("_", " "))
            prob = data.get("probability", 0) * 100
            margin = data.get("margin", 0) * 100
            report += f"- **{label}**: {prob:.1f}% (±{margin:.1f}%)\n"

        # Signals
        if signals:
            report += "\n## Señales de Alerta\n\n"
            report += "El sistema ha detectado las siguientes señales de riesgo elevado que requieren atención:\n\n"
            for s in signals[:5]:
                domain_name = DOMAIN_NAMES.get(s.get("domain", ""), s.get("domain", "General"))
                severity = "Alta" if s.get("severity") == "high" else "Media"
                report += f"- **{domain_name}**: {s.get('title', 'Señal detectada')} — Severidad: {severity}\n"

        # Scenarios
        report += "\n## Escenarios Proyectados\n\n"
        scenario_labels = {
            "optimistic": "Escenario Optimista",
            "base": "Escenario Base",
            "pessimistic": "Escenario Pesimista",
            "collapse": "Escenario de Colapso",
        }
        for sc in scenarios:
            label = scenario_labels.get(sc["scenario_type"], sc["scenario_type"])
            prob = sc["probability"] * 100
            report += f"### {label} (Probabilidad: {prob:.0f}%)\n\n"
            report += f"{sc['description']}\n\n"

        report += """## Nota sobre este Informe

Este informe fue generado utilizando el motor de análisis programático de ATALAYA. Para obtener un artículo editorial completo con contexto geopolítico, fuentes en tiempo real y análisis narrativo profundo, asegúrese de que el servicio de inteligencia artificial esté configurado correctamente.

---

*Las evaluaciones presentadas se basan en modelos cuantitativos y no constituyen asesoramiento financiero o político. ATALAYA Intelligence.*
"""
        return report

    def _interpret_score_es(self, score: float) -> str:
        if score < 30:
            return "Las instituciones del país muestran resiliencia estructural con bajo riesgo sistémico. No se identifican amenazas inminentes a la estabilidad."
        elif score < 50:
            return "Se detectan tensiones sistémicas que requieren monitoreo continuo. Existen factores de presión en múltiples dominios que podrían escalar si no se atienden."
        elif score < 70:
            return "El país se encuentra en un estado pre-crisis con la ventana de intervención cerrándose progresivamente. Factores estructurales de inestabilidad están convergiendo."
        elif score < 85:
            return "Crisis inminente. Se requieren acciones urgentes de mitigación. Los indicadores muestran deterioro acelerado en dominios críticos con alto riesgo de contagio entre sectores."
        return "Colapso sistémico en curso. Los mecanismos institucionales de contención han sido superados. Se observa deterioro simultáneo en múltiples dominios con retroalimentación negativa."

    def _dominant_insight(self, domain_scores: Dict[str, float], dominant: str) -> str:
        domain_name = DOMAIN_NAMES.get(dominant, dominant.replace("_", " ").title())
        score = domain_scores.get(dominant, 0)
        if score >= 70:
            return f"El dominio más comprometido es **{domain_name}** con un índice de {score:.1f}, lo que sugiere una fragilidad estructural profunda en este sector."
        elif score >= 50:
            return f"El dominio con mayor presión es **{domain_name}** ({score:.1f}), indicando tensiones significativas que requieren vigilancia."
        return f"El dominio de mayor actividad es **{domain_name}** ({score:.1f}), aunque dentro de parámetros manejables."

    def _dominant_trend(self, trends: Dict[str, str]) -> str:
        if not trends:
            return "stable"
        trend_counts = {}
        for t in trends.values():
            trend_counts[t] = trend_counts.get(t, 0) + 1
        return max(trend_counts, key=trend_counts.get)

    def _version(self) -> str:
        return "0.1.0"
