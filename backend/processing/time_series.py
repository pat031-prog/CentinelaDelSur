import math
from typing import Any, Dict, List, Optional, Tuple
from backend.utils.logger import logger


class TimeSeriesAnalyzer:
    """Time series analysis tools for crisis indicators.

    Provides trend detection, moving averages, and basic forecasting
    without heavy dependencies.
    """

    def __init__(self):
        self.logger = logger.getChild("time_series")

    def moving_average(self, values: List[float], window: int = 7) -> List[Optional[float]]:
        """Calculate simple moving average."""
        if len(values) < window:
            return [None] * len(values)

        result = [None] * (window - 1)
        for i in range(window - 1, len(values)):
            window_values = values[i - window + 1:i + 1]
            result.append(round(sum(window_values) / window, 4))

        return result

    def exponential_moving_average(
        self, values: List[float], alpha: float = 0.3
    ) -> List[float]:
        """Calculate exponential moving average."""
        if not values:
            return []

        ema = [values[0]]
        for i in range(1, len(values)):
            ema.append(round(alpha * values[i] + (1 - alpha) * ema[-1], 4))

        return ema

    def detect_trend(self, values: List[float]) -> Dict[str, Any]:
        """Detect trend direction and strength using linear regression."""
        n = len(values)
        if n < 3:
            return {"direction": "insufficient_data", "slope": 0, "r_squared": 0}

        # Simple linear regression
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n

        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return {"direction": "flat", "slope": 0, "r_squared": 0}

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        # R-squared
        ss_res = sum((values[i] - (slope * i + intercept)) ** 2 for i in range(n))
        ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Classify direction
        if abs(slope) < 0.01 * abs(y_mean) if y_mean != 0 else abs(slope) < 0.01:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        # Classify strength
        abs_r = abs(r_squared)
        if abs_r > 0.7:
            strength = "strong"
        elif abs_r > 0.4:
            strength = "moderate"
        else:
            strength = "weak"

        return {
            "direction": direction,
            "slope": round(slope, 4),
            "r_squared": round(r_squared, 4),
            "strength": strength,
            "intercept": round(intercept, 4),
        }

    def forecast_linear(self, values: List[float], periods: int = 7) -> List[float]:
        """Simple linear forecast based on trend."""
        trend = self.detect_trend(values)
        if trend["direction"] == "insufficient_data":
            return []

        n = len(values)
        return [
            round(trend["slope"] * (n + i) + trend["intercept"], 4)
            for i in range(periods)
        ]

    def calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation of returns)."""
        if len(values) < 2:
            return 0.0

        returns = []
        for i in range(1, len(values)):
            if values[i - 1] != 0:
                returns.append((values[i] - values[i - 1]) / abs(values[i - 1]))

        if not returns:
            return 0.0

        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)

        return round(math.sqrt(variance), 4)

    def detect_regime_change(
        self, values: List[float], window: int = 10
    ) -> List[Dict[str, Any]]:
        """Detect potential regime changes (structural breaks) in time series."""
        if len(values) < window * 2:
            return []

        changes = []
        for i in range(window, len(values) - window):
            before = values[i - window:i]
            after = values[i:i + window]

            mean_before = sum(before) / window
            mean_after = sum(after) / window

            std_before = math.sqrt(sum((x - mean_before)**2 for x in before) / window)
            std_after = math.sqrt(sum((x - mean_after)**2 for x in after) / window)

            # Check for significant mean shift
            pooled_std = math.sqrt((std_before**2 + std_after**2) / 2) or 0.001
            mean_shift = abs(mean_after - mean_before) / pooled_std

            if mean_shift > 2.0:
                changes.append({
                    "index": i,
                    "mean_before": round(mean_before, 4),
                    "mean_after": round(mean_after, 4),
                    "shift_magnitude": round(mean_shift, 2),
                    "direction": "up" if mean_after > mean_before else "down",
                })

        return changes

    def full_analysis(self, values: List[float]) -> Dict[str, Any]:
        """Run complete time series analysis."""
        return {
            "trend": self.detect_trend(values),
            "volatility": self.calculate_volatility(values),
            "moving_avg_7": self.moving_average(values, 7),
            "ema": self.exponential_moving_average(values),
            "forecast_7d": self.forecast_linear(values, 7),
            "regime_changes": self.detect_regime_change(values),
            "stats": {
                "count": len(values),
                "mean": round(sum(values) / len(values), 4) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
            },
        }
