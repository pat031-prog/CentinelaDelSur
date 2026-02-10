from typing import Any, Dict, List, Optional
from backend.utils.logger import logger


# Cross-domain propagation matrix
# How a crisis in domain X affects domain Y (0-1 scale)
PROPAGATION_MATRIX = {
    "political": {
        "economic": 0.7,
        "supply_chain": 0.4,
        "geopolitical": 0.6,
        "climate": 0.1,
        "technology": 0.3,
    },
    "economic": {
        "political": 0.8,
        "supply_chain": 0.6,
        "geopolitical": 0.4,
        "climate": 0.1,
        "technology": 0.3,
    },
    "supply_chain": {
        "political": 0.5,
        "economic": 0.8,
        "geopolitical": 0.3,
        "climate": 0.1,
        "technology": 0.2,
    },
    "geopolitical": {
        "political": 0.7,
        "economic": 0.6,
        "supply_chain": 0.7,
        "climate": 0.1,
        "technology": 0.4,
    },
    "climate": {
        "political": 0.4,
        "economic": 0.6,
        "supply_chain": 0.7,
        "geopolitical": 0.2,
        "technology": 0.2,
    },
    "technology": {
        "political": 0.3,
        "economic": 0.5,
        "supply_chain": 0.6,
        "geopolitical": 0.2,
        "climate": 0.05,
    },
}

# Time delays for cross-domain propagation (in days)
PROPAGATION_DELAYS = {
    "political": {"economic": 7, "supply_chain": 14, "geopolitical": 3, "climate": 90, "technology": 14},
    "economic": {"political": 14, "supply_chain": 7, "geopolitical": 30, "climate": 90, "technology": 14},
    "supply_chain": {"political": 21, "economic": 7, "geopolitical": 30, "climate": 90, "technology": 7},
    "geopolitical": {"political": 3, "economic": 14, "supply_chain": 7, "climate": 90, "technology": 7},
    "climate": {"political": 30, "economic": 14, "supply_chain": 7, "geopolitical": 60, "technology": 30},
    "technology": {"political": 7, "economic": 3, "supply_chain": 3, "geopolitical": 14, "climate": 90},
}


class CascadeSimulator:
    """Simulates crisis cascades across domains.

    Models how a shock in one domain propagates to others,
    considering propagation strengths, delays, and feedback loops.
    """

    def __init__(self):
        self.logger = logger.getChild("cascade_simulator")

    def simulate(
        self,
        initial_domain: str,
        shock_magnitude: float,
        current_scores: Dict[str, float],
        time_horizon_days: int = 90,
        damping_factor: float = 0.8,
    ) -> Dict[str, Any]:
        """Simulate cascade from an initial shock.

        Args:
            initial_domain: Domain where shock originates
            shock_magnitude: Size of initial shock (0-100 additional risk)
            current_scores: Current risk scores per domain
            time_horizon_days: How far to simulate
            damping_factor: How much each propagation step reduces impact
        """
        if initial_domain not in PROPAGATION_MATRIX:
            return {"error": f"Unknown domain: {initial_domain}"}

        # Initialize state
        scores = {d: current_scores.get(d, 25.0) for d in PROPAGATION_MATRIX}
        scores[initial_domain] = min(100, scores[initial_domain] + shock_magnitude)

        timeline = []
        propagation_queue = []

        # Day 0: Initial shock
        timeline.append({
            "day": 0,
            "event": f"Initial shock in {initial_domain}",
            "scores": dict(scores),
            "changes": {initial_domain: shock_magnitude},
        })

        # Queue initial propagations
        for target, strength in PROPAGATION_MATRIX[initial_domain].items():
            delay = PROPAGATION_DELAYS[initial_domain][target]
            impact = shock_magnitude * strength * damping_factor
            if impact > 2.0 and delay <= time_horizon_days:
                propagation_queue.append({
                    "day": delay,
                    "source": initial_domain,
                    "target": target,
                    "impact": impact,
                    "generation": 1,
                })

        # Process propagation queue
        max_generations = 4
        processed_days = set()

        propagation_queue.sort(key=lambda x: x["day"])

        while propagation_queue:
            event = propagation_queue.pop(0)

            if event["day"] > time_horizon_days:
                break
            if event["generation"] > max_generations:
                continue

            # Apply impact
            target = event["target"]
            old_score = scores[target]
            scores[target] = min(100, scores[target] + event["impact"])
            actual_impact = scores[target] - old_score

            if actual_impact > 1.0:
                timeline.append({
                    "day": event["day"],
                    "event": f"{event['source']} crisis propagates to {target} "
                             f"(+{actual_impact:.1f} risk, generation {event['generation']})",
                    "scores": dict(scores),
                    "changes": {target: round(actual_impact, 1)},
                })

                # Queue secondary propagations
                for next_target, strength in PROPAGATION_MATRIX[target].items():
                    if next_target == event["source"]:
                        # Feedback loop - reduced but not eliminated
                        strength *= 0.3

                    delay = PROPAGATION_DELAYS[target][next_target]
                    next_impact = actual_impact * strength * damping_factor
                    next_day = event["day"] + delay

                    if next_impact > 2.0 and next_day <= time_horizon_days:
                        propagation_queue.append({
                            "day": next_day,
                            "source": target,
                            "target": next_target,
                            "impact": next_impact,
                            "generation": event["generation"] + 1,
                        })

                propagation_queue.sort(key=lambda x: x["day"])

        # Calculate final assessment
        initial_composite = sum(current_scores.get(d, 25.0) for d in scores) / len(scores)
        final_composite = sum(scores.values()) / len(scores)

        return {
            "initial_domain": initial_domain,
            "shock_magnitude": shock_magnitude,
            "time_horizon_days": time_horizon_days,
            "initial_composite_score": round(initial_composite, 1),
            "final_composite_score": round(final_composite, 1),
            "score_increase": round(final_composite - initial_composite, 1),
            "final_scores": {d: round(s, 1) for d, s in scores.items()},
            "timeline": timeline,
            "most_affected_domains": sorted(
                [
                    {"domain": d, "increase": round(scores[d] - current_scores.get(d, 25.0), 1)}
                    for d in scores
                ],
                key=lambda x: x["increase"],
                reverse=True,
            ),
            "feedback_loops_detected": self._detect_feedback_loops(timeline),
        }

    def _detect_feedback_loops(self, timeline: List[Dict]) -> List[Dict[str, str]]:
        """Detect feedback loops in cascade timeline."""
        loops = []
        domain_hits = {}

        for event in timeline:
            for domain, change in event.get("changes", {}).items():
                if domain not in domain_hits:
                    domain_hits[domain] = []
                domain_hits[domain].append(event["day"])

        for domain, days in domain_hits.items():
            if len(days) > 1:
                loops.append({
                    "domain": domain,
                    "hits": len(days),
                    "description": f"{domain} affected {len(days)} times - feedback loop active",
                })

        return loops

    def identify_intervention_points(
        self,
        cascade_result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Identify optimal points to intervene and break the cascade."""
        timeline = cascade_result.get("timeline", [])
        interventions = []

        for i, event in enumerate(timeline[1:], 1):  # Skip initial shock
            for domain, change in event.get("changes", {}).items():
                if change > 5.0:
                    interventions.append({
                        "day": event["day"],
                        "domain": domain,
                        "impact_if_blocked": round(change, 1),
                        "priority": "high" if change > 15 else "medium" if change > 8 else "low",
                        "description": f"Intervene in {domain} by day {event['day']} "
                                      f"to prevent +{change:.1f} risk escalation",
                    })

        return sorted(interventions, key=lambda x: x["impact_if_blocked"], reverse=True)
