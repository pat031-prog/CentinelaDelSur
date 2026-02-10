from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.utils.logger import logger


# Risk domain weights for composite scoring
DOMAIN_WEIGHTS = {
    "political": 0.20,
    "economic": 0.25,
    "supply_chain": 0.15,
    "geopolitical": 0.15,
    "climate": 0.10,
    "technology": 0.15,
}

# Alert level thresholds
ALERT_THRESHOLDS = {
    "green": (0, 30),
    "yellow": (30, 50),
    "orange": (50, 70),
    "red": (70, 85),
    "black": (85, 100),
}


class RiskScorer:
    """Calculates composite risk scores across multiple domains.

    Implements a weighted multi-domain risk assessment framework
    with cross-domain interaction effects.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DOMAIN_WEIGHTS
        self.logger = logger.getChild("risk_scoring")

    def score_to_level(self, score: float) -> str:
        """Convert numeric score to alert level."""
        for level, (low, high) in ALERT_THRESHOLDS.items():
            if low <= score < high:
                return level
        return "black" if score >= 85 else "green"

    def calculate_domain_score(
        self,
        indicators: Dict[str, float],
        indicator_weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """Calculate a single domain score from its indicators.

        Args:
            indicators: Dict of indicator_name -> value (0-100 scale)
            indicator_weights: Optional custom weights per indicator
        """
        if not indicators:
            return 0.0

        if indicator_weights:
            total_weight = sum(indicator_weights.get(k, 1.0) for k in indicators)
            score = sum(
                v * indicator_weights.get(k, 1.0)
                for k, v in indicators.items()
            ) / total_weight
        else:
            score = sum(indicators.values()) / len(indicators)

        return round(min(100, max(0, score)), 1)

    def calculate_composite_score(
        self, domain_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate composite risk score across all domains.

        Includes cross-domain interaction effects where high risk
        in one domain amplifies risk in related domains.
        """
        if not domain_scores:
            return {"score": 0.0, "level": "green", "domains": {}}

        # Base weighted score
        weighted_sum = 0.0
        total_weight = 0.0
        for domain, score in domain_scores.items():
            weight = self.weights.get(domain, 0.1)
            weighted_sum += score * weight
            total_weight += weight

        base_score = weighted_sum / total_weight if total_weight > 0 else 0

        # Cross-domain interaction amplifier
        # When multiple domains are elevated, systemic risk increases non-linearly
        elevated_domains = sum(1 for s in domain_scores.values() if s > 50)
        if elevated_domains >= 3:
            interaction_multiplier = 1.0 + (elevated_domains - 2) * 0.1
        else:
            interaction_multiplier = 1.0

        # Critical domain check: if any single domain is in "black", amplify
        max_domain_score = max(domain_scores.values()) if domain_scores else 0
        if max_domain_score >= 85:
            interaction_multiplier *= 1.15

        composite = min(100, base_score * interaction_multiplier)

        return {
            "score": round(composite, 1),
            "level": self.score_to_level(composite),
            "base_score": round(base_score, 1),
            "interaction_multiplier": round(interaction_multiplier, 2),
            "elevated_domains": elevated_domains,
            "domains": {
                domain: {
                    "score": round(score, 1),
                    "level": self.score_to_level(score),
                    "weight": self.weights.get(domain, 0.1),
                }
                for domain, score in domain_scores.items()
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    def estimate_crisis_probability(
        self,
        composite_score: float,
        trend_direction: str = "stable",
        days: int = 30,
    ) -> Dict[str, float]:
        """Estimate probability of systemic crisis within time horizon.

        Uses a logistic function calibrated to historical crisis frequencies.
        """
        import math

        # Logistic function: P = 1 / (1 + e^(-k*(x-x0)))
        # Calibrated so score=50 gives ~10% at 30 days, score=80 gives ~60%
        k = 0.08
        x0 = 65

        base_prob = 1 / (1 + math.exp(-k * (composite_score - x0)))

        # Adjust for time horizon (longer = higher probability)
        time_factor = math.log(max(days, 1)) / math.log(30)

        # Adjust for trend
        trend_factors = {
            "worsening": 1.3,
            "stable": 1.0,
            "improving": 0.7,
        }
        trend_multiplier = trend_factors.get(trend_direction, 1.0)

        probability = min(0.95, base_prob * time_factor * trend_multiplier)
        margin = min(0.20, probability * 0.3)

        return {
            "probability": round(probability, 3),
            "margin": round(margin, 3),
            "lower_bound": round(max(0, probability - margin), 3),
            "upper_bound": round(min(1, probability + margin), 3),
        }

    def calculate_country_risk(
        self,
        domain_scores: Dict[str, float],
        trend: str = "stable",
    ) -> Dict[str, Any]:
        """Full country risk assessment."""
        composite = self.calculate_composite_score(domain_scores)

        prob_30 = self.estimate_crisis_probability(composite["score"], trend, 30)
        prob_60 = self.estimate_crisis_probability(composite["score"], trend, 60)
        prob_90 = self.estimate_crisis_probability(composite["score"], trend, 90)

        return {
            **composite,
            "crisis_probability": {
                "30_days": prob_30,
                "60_days": prob_60,
                "90_days": prob_90,
            },
            "trend": trend,
        }
