import re
from typing import Dict, List, Tuple
from backend.utils.logger import logger


# Bilingual sentiment lexicon for crisis analysis
POSITIVE_WORDS = {
    "en": [
        "agreement", "cooperation", "growth", "recovery", "stable",
        "peace", "reform", "progress", "investment", "improvement",
        "democratic", "transparent", "resolution", "aid", "support",
    ],
    "es": [
        "acuerdo", "cooperación", "crecimiento", "recuperación", "estable",
        "paz", "reforma", "progreso", "inversión", "mejora",
        "democrático", "transparente", "resolución", "ayuda", "apoyo",
    ],
}

NEGATIVE_WORDS = {
    "en": [
        "crisis", "collapse", "violence", "corruption", "default",
        "protest", "war", "sanctions", "inflation", "poverty",
        "instability", "authoritarian", "repression", "shortage", "conflict",
        "coup", "assassination", "emergency", "disaster", "failure",
        "debt", "recession", "unemployment", "fraud", "impunity",
    ],
    "es": [
        "crisis", "colapso", "violencia", "corrupción", "default",
        "protesta", "guerra", "sanciones", "inflación", "pobreza",
        "inestabilidad", "autoritario", "represión", "escasez", "conflicto",
        "golpe", "asesinato", "emergencia", "desastre", "fracaso",
        "deuda", "recesión", "desempleo", "fraude", "impunidad",
    ],
}

# Intensity modifiers
INTENSIFIERS = ["very", "extremely", "severe", "unprecedented", "massive", "total",
                "muy", "extremadamente", "severo", "sin precedentes", "masivo", "total"]
DIMINISHERS = ["slightly", "minor", "small", "limited", "ligeramente", "menor", "pequeño", "limitado"]


class SentimentAnalyzer:
    """Bilingual sentiment analyzer optimized for crisis-related content.

    Uses a lexicon-based approach with crisis-specific vocabulary
    for both English and Spanish text.
    """

    def __init__(self):
        self.logger = logger.getChild("sentiment")
        self._all_positive = set()
        self._all_negative = set()
        for words in POSITIVE_WORDS.values():
            self._all_positive.update(words)
        for words in NEGATIVE_WORDS.values():
            self._all_negative.update(words)

    def analyze(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text. Returns score from -1 (very negative) to 1 (very positive).

        Returns:
            Dict with keys: score, positive_count, negative_count, intensity
        """
        words = re.findall(r'\b\w+\b', text.lower())

        if not words:
            return {"score": 0.0, "positive_count": 0, "negative_count": 0, "intensity": 0.0}

        positive_count = sum(1 for w in words if w in self._all_positive)
        negative_count = sum(1 for w in words if w in self._all_negative)

        # Calculate intensity modifier
        intensifier_count = sum(1 for w in words if w in INTENSIFIERS)
        diminisher_count = sum(1 for w in words if w in DIMINISHERS)
        intensity = 1.0 + (intensifier_count * 0.3) - (diminisher_count * 0.2)
        intensity = max(0.1, min(2.0, intensity))

        # Calculate raw score
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            raw_score = 0.0
        else:
            raw_score = (positive_count - negative_count) / total_sentiment_words

        # Apply intensity
        score = raw_score * intensity
        score = max(-1.0, min(1.0, score))

        return {
            "score": round(score, 3),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "intensity": round(intensity, 2),
        }

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """Analyze sentiment for a batch of texts."""
        return [self.analyze(text) for text in texts]

    def get_aggregate_sentiment(self, texts: List[str]) -> Dict[str, float]:
        """Get aggregate sentiment across multiple texts."""
        if not texts:
            return {"mean_score": 0.0, "std_dev": 0.0, "count": 0, "trend": "neutral"}

        results = self.analyze_batch(texts)
        scores = [r["score"] for r in results]

        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5

        # Determine trend
        if len(scores) >= 4:
            first_half = sum(scores[:len(scores)//2]) / (len(scores)//2)
            second_half = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
            diff = second_half - first_half
            if diff < -0.1:
                trend = "worsening"
            elif diff > 0.1:
                trend = "improving"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "mean_score": round(mean_score, 3),
            "std_dev": round(std_dev, 3),
            "count": len(scores),
            "trend": trend,
        }
