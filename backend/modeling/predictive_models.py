import math
from typing import Any, Dict, List, Optional, Tuple
from backend.utils.logger import logger


class CrisisPredictor:
    """Predictive models for crisis forecasting.

    Combines multiple signals into crisis probability estimates
    using ensemble methods.
    """

    def __init__(self):
        self.logger = logger.getChild("predictive_models")

    def logistic_crisis_probability(
        self,
        risk_score: float,
        trend_velocity: float = 0.0,
        historical_frequency: float = 0.1,
    ) -> float:
        """Estimate crisis probability using logistic model.

        Args:
            risk_score: Current composite risk score (0-100)
            trend_velocity: Rate of change in risk score (points/day)
            historical_frequency: Base rate of crises for this country type
        """
        # Logistic function
        k = 0.08
        x0 = 60 - (trend_velocity * 5)  # Faster deterioration shifts threshold left

        base_prob = 1 / (1 + math.exp(-k * (risk_score - x0)))

        # Bayesian update with historical prior
        prior = historical_frequency
        likelihood = base_prob
        posterior = (likelihood * prior) / (
            likelihood * prior + (1 - likelihood) * (1 - prior)
        )

        return round(min(0.95, max(0.01, posterior)), 3)

    def multi_signal_forecast(
        self,
        domain_scores: Dict[str, float],
        trends: Dict[str, str],
        anomaly_counts: Dict[str, int],
        sentiment_score: float = 0.0,
    ) -> Dict[str, Any]:
        """Combine multiple signals for crisis forecast.

        Args:
            domain_scores: Risk scores per domain
            trends: Trend direction per domain
            anomaly_counts: Number of anomalies detected per domain
            sentiment_score: Aggregate sentiment (-1 to 1)
        """
        # Score component
        composite_score = sum(domain_scores.values()) / len(domain_scores) if domain_scores else 0

        # Trend component (worsening trends increase risk)
        trend_values = {"worsening": 1.0, "stable": 0.0, "improving": -0.5}
        trend_score = sum(
            trend_values.get(t, 0) for t in trends.values()
        ) / max(len(trends), 1)

        # Anomaly component
        total_anomalies = sum(anomaly_counts.values())
        anomaly_score = min(1.0, total_anomalies / 20)

        # Sentiment component (negative sentiment increases risk)
        sentiment_risk = max(0, -sentiment_score)

        # Weighted combination
        combined = (
            composite_score * 0.4 +
            (trend_score * 30) * 0.2 +
            (anomaly_score * 100) * 0.2 +
            (sentiment_risk * 100) * 0.2
        )

        probability = self.logistic_crisis_probability(combined, trend_score * 2)

        return {
            "composite_risk_score": round(combined, 1),
            "crisis_probability_30d": probability,
            "crisis_probability_60d": round(min(0.95, probability * 1.3), 3),
            "crisis_probability_90d": round(min(0.95, probability * 1.5), 3),
            "components": {
                "base_risk": round(composite_score, 1),
                "trend_effect": round(trend_score * 30, 1),
                "anomaly_effect": round(anomaly_score * 100, 1),
                "sentiment_effect": round(sentiment_risk * 100, 1),
            },
            "confidence": self._estimate_confidence(domain_scores, anomaly_counts),
        }

    def _estimate_confidence(
        self,
        domain_scores: Dict[str, float],
        anomaly_counts: Dict[str, int],
    ) -> str:
        """Estimate confidence level of the prediction."""
        # More data domains = higher confidence
        coverage = len(domain_scores) / 6  # 6 total domains

        # Consistent signals = higher confidence
        if domain_scores:
            score_variance = sum(
                (s - sum(domain_scores.values()) / len(domain_scores)) ** 2
                for s in domain_scores.values()
            ) / len(domain_scores)
        else:
            score_variance = 0

        consistency = 1.0 - min(1.0, score_variance / 1000)

        confidence_score = coverage * 0.5 + consistency * 0.5

        if confidence_score > 0.7:
            return "high"
        elif confidence_score > 0.4:
            return "medium"
        return "low"

    def find_historical_analogs(
        self,
        current_profile: Dict[str, float],
        historical_profiles: List[Dict[str, Any]],
        top_n: int = 3,
    ) -> List[Dict[str, Any]]:
        """Find historical crises most similar to current situation.

        Uses cosine similarity on domain score profiles.
        """
        if not historical_profiles:
            return []

        results = []
        for historical in historical_profiles:
            hist_scores = historical.get("domain_scores", {})
            similarity = self._cosine_similarity(current_profile, hist_scores)
            results.append({
                **historical,
                "similarity": round(similarity, 3),
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_n]

    def _cosine_similarity(self, a: Dict[str, float], b: Dict[str, float]) -> float:
        """Calculate cosine similarity between two domain score profiles."""
        common_keys = set(a.keys()) & set(b.keys())
        if not common_keys:
            return 0.0

        dot_product = sum(a[k] * b[k] for k in common_keys)
        magnitude_a = math.sqrt(sum(a[k] ** 2 for k in common_keys))
        magnitude_b = math.sqrt(sum(b[k] ** 2 for k in common_keys))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)
