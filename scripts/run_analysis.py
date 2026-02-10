"""Run a batch analysis for all monitored countries.

Usage: python -m scripts.run_analysis [--country ARG] [--domains political,economic]
"""

import argparse
import asyncio
import json

from backend.modeling.risk_scoring import RiskScorer
from backend.modeling.scenario_generator import ScenarioGenerator
from backend.modeling.cascade_simulator import CascadeSimulator
from backend.intelligence.report_generator import ReportGenerator
from backend.utils.logger import logger


# Sample domain scores for batch analysis
SAMPLE_SCORES = {
    "ARG": {"political": 55, "economic": 75, "supply_chain": 40, "geopolitical": 30, "climate": 35, "technology": 25},
    "BRA": {"political": 45, "economic": 40, "supply_chain": 30, "geopolitical": 35, "climate": 55, "technology": 30},
    "CHL": {"political": 35, "economic": 30, "supply_chain": 25, "geopolitical": 20, "climate": 40, "technology": 20},
    "COL": {"political": 50, "economic": 45, "supply_chain": 35, "geopolitical": 45, "climate": 35, "technology": 25},
    "MEX": {"political": 50, "economic": 40, "supply_chain": 35, "geopolitical": 45, "climate": 45, "technology": 30},
    "PER": {"political": 60, "economic": 45, "supply_chain": 30, "geopolitical": 25, "climate": 45, "technology": 25},
    "VEN": {"political": 85, "economic": 90, "supply_chain": 70, "geopolitical": 65, "climate": 35, "technology": 55},
}

COUNTRY_NAMES = {
    "ARG": "Argentina", "BRA": "Brazil", "CHL": "Chile",
    "COL": "Colombia", "MEX": "Mexico", "PER": "Peru", "VEN": "Venezuela",
}


def run_batch_analysis(country_code: str = None):
    """Run analysis for one or all countries."""
    scorer = RiskScorer()
    report_gen = ReportGenerator()

    targets = {country_code: SAMPLE_SCORES[country_code]} if country_code else SAMPLE_SCORES

    for code, scores in targets.items():
        name = COUNTRY_NAMES.get(code, code)
        logger.info(f"\n{'='*60}")
        logger.info(f"Analyzing {name} ({code})")
        logger.info(f"{'='*60}")

        trends = {d: "worsening" if s > 50 else "stable" for d, s in scores.items()}
        signals = [
            {"domain": d, "title": f"Elevated risk in {d}", "severity": "high" if s > 60 else "medium", "trend": trends[d]}
            for d, s in scores.items() if s > 40
        ]

        report = report_gen.generate_text_report(
            country_code=code,
            country_name=name,
            domain_scores=scores,
            trends=trends,
            signals=signals,
        )
        print(report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ATALAYA Batch Analysis")
    parser.add_argument("--country", type=str, help="Country code (e.g., ARG, BRA, VEN)")
    args = parser.parse_args()

    if args.country and args.country.upper() not in SAMPLE_SCORES:
        print(f"Country {args.country} not found. Available: {list(SAMPLE_SCORES.keys())}")
    else:
        run_batch_analysis(args.country.upper() if args.country else None)
