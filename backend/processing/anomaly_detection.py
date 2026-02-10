import math
from typing import Any, Dict, List, Optional, Tuple
from backend.utils.logger import logger


class AnomalyDetector:
    """Statistical anomaly detection for crisis indicators.

    Uses Z-score and IQR methods to detect unusual values
    in time series data without heavy ML dependencies.
    """

    def __init__(self, z_threshold: float = 2.5, iqr_multiplier: float = 1.5):
        self.z_threshold = z_threshold
        self.iqr_multiplier = iqr_multiplier
        self.logger = logger.getChild("anomaly_detection")

    def detect_zscore(self, values: List[float]) -> List[Dict[str, Any]]:
        """Detect anomalies using Z-score method.

        Args:
            values: Time-ordered list of values

        Returns:
            List of anomalies with index, value, z_score, and direction
        """
        if len(values) < 3:
            return []

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance) if variance > 0 else 0.001

        anomalies = []
        for i, value in enumerate(values):
            z_score = (value - mean) / std_dev
            if abs(z_score) > self.z_threshold:
                anomalies.append({
                    "index": i,
                    "value": value,
                    "z_score": round(z_score, 2),
                    "direction": "above" if z_score > 0 else "below",
                    "severity": self._classify_severity(abs(z_score)),
                })

        return anomalies

    def detect_iqr(self, values: List[float]) -> List[Dict[str, Any]]:
        """Detect anomalies using IQR (Interquartile Range) method."""
        if len(values) < 4:
            return []

        sorted_values = sorted(values)
        n = len(sorted_values)
        q1 = sorted_values[n // 4]
        q3 = sorted_values[3 * n // 4]
        iqr = q3 - q1

        lower_bound = q1 - self.iqr_multiplier * iqr
        upper_bound = q3 + self.iqr_multiplier * iqr

        anomalies = []
        for i, value in enumerate(values):
            if value < lower_bound or value > upper_bound:
                deviation = (value - q3) / iqr if value > upper_bound else (q1 - value) / iqr
                anomalies.append({
                    "index": i,
                    "value": value,
                    "bound_exceeded": "upper" if value > upper_bound else "lower",
                    "deviation_iqr": round(deviation, 2),
                    "severity": self._classify_severity(deviation),
                })

        return anomalies

    def detect_rate_of_change(
        self, values: List[float], threshold_pct: float = 20.0
    ) -> List[Dict[str, Any]]:
        """Detect sudden changes in rate (day-over-day or period-over-period).

        Args:
            values: Time-ordered values
            threshold_pct: Percentage change threshold to flag
        """
        if len(values) < 2:
            return []

        anomalies = []
        for i in range(1, len(values)):
            if values[i - 1] == 0:
                continue
            pct_change = ((values[i] - values[i - 1]) / abs(values[i - 1])) * 100
            if abs(pct_change) > threshold_pct:
                anomalies.append({
                    "index": i,
                    "value": values[i],
                    "previous_value": values[i - 1],
                    "pct_change": round(pct_change, 2),
                    "direction": "spike" if pct_change > 0 else "drop",
                    "severity": self._classify_severity(abs(pct_change) / threshold_pct),
                })

        return anomalies

    def analyze_series(self, values: List[float]) -> Dict[str, Any]:
        """Run full anomaly analysis on a time series."""
        return {
            "zscore_anomalies": self.detect_zscore(values),
            "iqr_anomalies": self.detect_iqr(values),
            "rate_changes": self.detect_rate_of_change(values),
            "summary": {
                "total_points": len(values),
                "mean": round(sum(values) / len(values), 2) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
            },
        }

    def _classify_severity(self, magnitude: float) -> str:
        """Classify anomaly severity based on magnitude."""
        if magnitude > 4.0:
            return "critical"
        elif magnitude > 3.0:
            return "high"
        elif magnitude > 2.0:
            return "medium"
        return "low"
