import re
from typing import Any, Dict, List, Optional
from backend.utils.logger import logger


# Crisis-related entity categories
ENTITY_CATEGORIES = {
    "political_actors": [
        "president", "minister", "congress", "parliament", "military",
        "opposition", "judiciary", "supreme court", "electoral",
        "presidente", "ministro", "congreso", "parlamento", "militar",
        "oposición", "poder judicial", "corte suprema",
    ],
    "economic_entities": [
        "central bank", "imf", "world bank", "treasury", "debt",
        "bonds", "currency", "inflation", "deficit", "reserves",
        "banco central", "fmi", "banco mundial", "deuda", "bonos",
        "moneda", "inflación", "déficit", "reservas",
    ],
    "crisis_events": [
        "protest", "riot", "coup", "impeachment", "default", "sanctions",
        "embargo", "blackout", "earthquake", "hurricane", "drought",
        "protesta", "disturbio", "golpe", "destitución", "apagón",
        "terremoto", "huracán", "sequía",
    ],
    "organizations": [
        "oas", "mercosur", "unasur", "celac", "brics", "nato", "un",
        "oea", "alba", "alianza del pacífico",
    ],
}


class NLPPipeline:
    """NLP processing pipeline for crisis-related text analysis.

    Provides entity extraction, keyword detection, and text classification
    without heavy ML dependencies. Designed for speed and accuracy on
    crisis-related content.
    """

    def __init__(self):
        self.logger = logger.getChild("nlp_pipeline")

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract crisis-relevant entities from text using pattern matching."""
        text_lower = text.lower()
        found = {}

        for category, keywords in ENTITY_CATEGORIES.items():
            matches = []
            for keyword in keywords:
                if keyword in text_lower:
                    matches.append(keyword)
            if matches:
                found[category] = matches

        return found

    def classify_event_type(self, text: str) -> str:
        """Classify text into crisis event categories."""
        text_lower = text.lower()

        classifications = {
            "political_crisis": [
                "coup", "golpe", "impeach", "destitución", "resign",
                "renuncia", "constitutional crisis", "crisis constitucional",
            ],
            "economic_crisis": [
                "default", "devaluation", "devaluación", "hyperinflation",
                "hiperinflación", "bank run", "corrida bancaria", "recession",
            ],
            "social_unrest": [
                "protest", "protesta", "riot", "disturbio", "strike",
                "huelga", "demonstration", "manifestación", "looting", "saqueo",
            ],
            "security_threat": [
                "attack", "ataque", "terrorism", "terrorismo", "cartel",
                "assassination", "asesinato", "kidnapping", "secuestro",
            ],
            "natural_disaster": [
                "earthquake", "terremoto", "hurricane", "huracán", "flood",
                "inundación", "drought", "sequía", "wildfire", "incendio",
            ],
            "supply_chain_disruption": [
                "shortage", "escasez", "port", "puerto", "blockade",
                "bloqueo", "shipping", "supply chain", "cadena de suministro",
            ],
            "cyber_incident": [
                "hack", "cyber", "ransomware", "data breach", "outage",
                "ciberataque", "interrupción",
            ],
        }

        scores = {}
        for category, keywords in classifications.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score

        if scores:
            return max(scores, key=scores.get)
        return "general"

    def extract_severity_signals(self, text: str) -> str:
        """Estimate severity from text content."""
        text_lower = text.lower()

        critical_signals = [
            "dead", "killed", "muertos", "collapse", "colapso",
            "emergency", "emergencia", "martial law", "estado de sitio",
            "war", "guerra",
        ]
        high_signals = [
            "injured", "heridos", "violence", "violencia",
            "crisis", "urgent", "urgente", "critical", "crítico",
        ]
        medium_signals = [
            "concern", "preocupación", "tension", "tensión",
            "warning", "advertencia", "risk", "riesgo",
        ]

        if any(signal in text_lower for signal in critical_signals):
            return "critical"
        elif any(signal in text_lower for signal in high_signals):
            return "high"
        elif any(signal in text_lower for signal in medium_signals):
            return "medium"
        return "low"

    def process_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single news article through the full NLP pipeline."""
        text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"

        return {
            **article,
            "entities": self.extract_entities(text),
            "event_type": self.classify_event_type(text),
            "severity": self.extract_severity_signals(text),
        }

    def process_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of articles."""
        return [self.process_article(a) for a in articles]
