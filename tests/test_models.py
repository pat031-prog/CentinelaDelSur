"""Tests for ATALAYA modeling and processing modules."""

import pytest
from backend.modeling.risk_scoring import RiskScorer
from backend.modeling.scenario_generator import ScenarioGenerator
from backend.modeling.cascade_simulator import CascadeSimulator
from backend.modeling.predictive_models import CrisisPredictor
from backend.processing.sentiment import SentimentAnalyzer
from backend.processing.anomaly_detection import AnomalyDetector
from backend.processing.time_series import TimeSeriesAnalyzer
from backend.processing.nlp_pipeline import NLPPipeline
from backend.processing.network_analysis import NetworkAnalyzer


class TestRiskScorer:
    def setup_method(self):
        self.scorer = RiskScorer()

    def test_score_to_level(self):
        assert self.scorer.score_to_level(10) == "green"
        assert self.scorer.score_to_level(40) == "yellow"
        assert self.scorer.score_to_level(60) == "orange"
        assert self.scorer.score_to_level(75) == "red"
        assert self.scorer.score_to_level(90) == "black"

    def test_calculate_domain_score(self):
        indicators = {"a": 50, "b": 70, "c": 30}
        score = self.scorer.calculate_domain_score(indicators)
        assert score == 50.0

    def test_calculate_domain_score_empty(self):
        assert self.scorer.calculate_domain_score({}) == 0.0

    def test_composite_score(self):
        domain_scores = {
            "political": 40,
            "economic": 60,
            "supply_chain": 30,
            "geopolitical": 25,
            "climate": 35,
            "technology": 20,
        }
        result = self.scorer.calculate_composite_score(domain_scores)
        assert "score" in result
        assert "level" in result
        assert 0 <= result["score"] <= 100
        assert result["level"] in ["green", "yellow", "orange", "red", "black"]

    def test_composite_interaction_amplifier(self):
        # 3+ domains above 50 should increase score
        high_scores = {
            "political": 65,
            "economic": 70,
            "supply_chain": 55,
            "geopolitical": 60,
        }
        result = self.scorer.calculate_composite_score(high_scores)
        assert result["interaction_multiplier"] > 1.0

    def test_crisis_probability(self):
        prob = self.scorer.estimate_crisis_probability(70, "worsening", 30)
        assert 0 < prob["probability"] < 1
        assert prob["margin"] > 0

    def test_country_risk_full(self):
        scores = {"political": 50, "economic": 70, "supply_chain": 40}
        result = self.scorer.calculate_country_risk(scores, trend="worsening")
        assert "crisis_probability" in result
        assert "30_days" in result["crisis_probability"]
        assert "60_days" in result["crisis_probability"]
        assert "90_days" in result["crisis_probability"]


class TestScenarioGenerator:
    def setup_method(self):
        self.gen = ScenarioGenerator()

    def test_generate_scenarios(self):
        scenarios = self.gen.generate_scenarios(
            country_code="ARG",
            dominant_risk_type="economic",
            composite_score=65,
            domain_scores={"political": 50, "economic": 75},
        )
        assert len(scenarios) == 4
        types = [s["scenario_type"] for s in scenarios]
        assert "optimistic" in types
        assert "base" in types
        assert "pessimistic" in types
        assert "collapse" in types
        # Probabilities should sum to ~1
        total_prob = sum(s["probability"] for s in scenarios)
        assert 0.95 <= total_prob <= 1.05

    def test_high_risk_scenarios(self):
        scenarios = self.gen.generate_scenarios(
            country_code="VEN",
            dominant_risk_type="economic",
            composite_score=90,
            domain_scores={"political": 85, "economic": 90},
        )
        # Collapse should have high probability
        collapse = [s for s in scenarios if s["scenario_type"] == "collapse"][0]
        assert collapse["probability"] >= 0.4


class TestCascadeSimulator:
    def setup_method(self):
        self.sim = CascadeSimulator()

    def test_simulate_basic(self):
        scores = {"political": 40, "economic": 50, "supply_chain": 30, "geopolitical": 25, "climate": 20, "technology": 15}
        result = self.sim.simulate(
            initial_domain="economic",
            shock_magnitude=30,
            current_scores=scores,
            time_horizon_days=90,
        )
        assert result["initial_domain"] == "economic"
        assert result["final_composite_score"] > result["initial_composite_score"]
        assert len(result["timeline"]) > 0
        assert result["timeline"][0]["day"] == 0

    def test_cascade_propagation(self):
        scores = {"political": 50, "economic": 50, "supply_chain": 50, "geopolitical": 50, "climate": 30, "technology": 30}
        result = self.sim.simulate(
            initial_domain="economic",
            shock_magnitude=40,
            current_scores=scores,
        )
        # Should propagate to other domains
        assert result["score_increase"] > 0
        affected = [d for d in result["most_affected_domains"] if d["increase"] > 0]
        assert len(affected) > 1

    def test_intervention_points(self):
        scores = {"political": 40, "economic": 40, "supply_chain": 40, "geopolitical": 40, "climate": 30, "technology": 30}
        result = self.sim.simulate("economic", 40, scores)
        interventions = self.sim.identify_intervention_points(result)
        assert isinstance(interventions, list)


class TestSentimentAnalyzer:
    def setup_method(self):
        self.analyzer = SentimentAnalyzer()

    def test_negative_sentiment(self):
        text = "crisis violence corruption collapse inflation poverty"
        result = self.analyzer.analyze(text)
        assert result["score"] < 0
        assert result["negative_count"] > 0

    def test_positive_sentiment(self):
        text = "agreement cooperation growth recovery stable peace"
        result = self.analyzer.analyze(text)
        assert result["score"] > 0
        assert result["positive_count"] > 0

    def test_neutral_text(self):
        text = "the weather today is moderate with some clouds"
        result = self.analyzer.analyze(text)
        assert abs(result["score"]) < 0.5

    def test_spanish_sentiment(self):
        text = "crisis violencia corrupción inflación pobreza"
        result = self.analyzer.analyze(text)
        assert result["score"] < 0

    def test_aggregate_sentiment(self):
        texts = ["crisis collapse violence", "peace agreement cooperation", "conflict instability"]
        result = self.analyzer.get_aggregate_sentiment(texts)
        assert "mean_score" in result
        assert "count" in result
        assert result["count"] == 3


class TestAnomalyDetector:
    def setup_method(self):
        self.detector = AnomalyDetector()

    def test_zscore_detection(self):
        values = [10, 11, 9, 10, 12, 11, 10, 50, 10, 11]  # 50 is anomaly
        anomalies = self.detector.detect_zscore(values)
        assert len(anomalies) > 0
        assert any(a["index"] == 7 for a in anomalies)

    def test_rate_of_change(self):
        values = [100, 102, 98, 101, 150, 99]  # 150 is a spike
        anomalies = self.detector.detect_rate_of_change(values, threshold_pct=20)
        assert len(anomalies) > 0

    def test_full_analysis(self):
        values = [10, 11, 9, 10, 12, 11, 10, 9, 11, 10]
        result = self.detector.analyze_series(values)
        assert "zscore_anomalies" in result
        assert "summary" in result
        assert result["summary"]["total_points"] == 10


class TestTimeSeriesAnalyzer:
    def setup_method(self):
        self.analyzer = TimeSeriesAnalyzer()

    def test_moving_average(self):
        values = list(range(10))
        ma = self.analyzer.moving_average(values, window=3)
        assert ma[0] is None
        assert ma[1] is None
        assert ma[2] == 1.0  # (0+1+2)/3

    def test_detect_trend_increasing(self):
        values = [10, 12, 14, 16, 18, 20]
        trend = self.analyzer.detect_trend(values)
        assert trend["direction"] == "increasing"
        assert trend["slope"] > 0

    def test_detect_trend_decreasing(self):
        values = [20, 18, 16, 14, 12, 10]
        trend = self.analyzer.detect_trend(values)
        assert trend["direction"] == "decreasing"
        assert trend["slope"] < 0

    def test_volatility(self):
        stable = [10, 10.1, 9.9, 10, 10.1]
        volatile = [10, 15, 5, 20, 2]
        assert self.analyzer.calculate_volatility(stable) < self.analyzer.calculate_volatility(volatile)

    def test_forecast(self):
        values = [10, 12, 14, 16, 18, 20]
        forecast = self.analyzer.forecast_linear(values, periods=3)
        assert len(forecast) == 3
        assert forecast[0] > values[-1]  # Should continue upward


class TestNLPPipeline:
    def setup_method(self):
        self.nlp = NLPPipeline()

    def test_extract_entities(self):
        text = "The president announced emergency measures as the military deployed to control protests"
        entities = self.nlp.extract_entities(text)
        assert "political_actors" in entities
        assert "crisis_events" in entities

    def test_classify_event_political(self):
        assert self.nlp.classify_event_type("Military coup attempt") == "political_crisis"

    def test_classify_event_economic(self):
        assert self.nlp.classify_event_type("Sovereign debt default announced") == "economic_crisis"

    def test_classify_event_natural(self):
        assert self.nlp.classify_event_type("Major earthquake hits coast") == "natural_disaster"

    def test_severity_critical(self):
        assert self.nlp.extract_severity_signals("50 killed in emergency") == "critical"

    def test_severity_low(self):
        assert self.nlp.extract_severity_signals("Quarterly report published") == "low"

    def test_process_article(self):
        article = {"title": "Protests erupt after coup attempt", "description": "Military forces...", "content": ""}
        result = self.nlp.process_article(article)
        assert "entities" in result
        assert "event_type" in result
        assert "severity" in result


class TestNetworkAnalyzer:
    def setup_method(self):
        self.network = NetworkAnalyzer()
        self.network.add_node("A", {"type": "country"})
        self.network.add_node("B", {"type": "country"})
        self.network.add_node("C", {"type": "country"})
        self.network.add_node("D", {"type": "resource"})
        self.network.add_edge("A", "B", weight=0.8)
        self.network.add_edge("B", "C", weight=0.6)
        self.network.add_edge("A", "D", weight=0.9)
        self.network.add_edge("D", "C", weight=0.7)

    def test_centrality(self):
        centrality = self.network.calculate_degree_centrality()
        assert len(centrality) == 4
        # A should have high centrality (most connections)
        assert centrality["A"] > 0

    def test_find_critical_nodes(self):
        critical = self.network.find_critical_nodes(top_n=2)
        assert len(critical) <= 2

    def test_dependencies(self):
        deps = self.network.find_dependencies("C")
        assert "B" in deps["dependencies"]
        assert "D" in deps["dependencies"]

    def test_cascade_simulation(self):
        result = self.network.simulate_cascade("A")
        assert result["initial_failure"] == "A"
        assert result["total_affected"] >= 1

    def test_network_summary(self):
        summary = self.network.get_network_summary()
        assert summary["total_nodes"] == 4
        assert summary["total_edges"] == 4


class TestCrisisPredictor:
    def setup_method(self):
        self.predictor = CrisisPredictor()

    def test_logistic_probability(self):
        # Low risk should give low probability
        low_prob = self.predictor.logistic_crisis_probability(20)
        high_prob = self.predictor.logistic_crisis_probability(80)
        assert low_prob < high_prob
        assert 0 < low_prob < 1
        assert 0 < high_prob < 1

    def test_multi_signal_forecast(self):
        result = self.predictor.multi_signal_forecast(
            domain_scores={"political": 60, "economic": 70},
            trends={"political": "worsening", "economic": "stable"},
            anomaly_counts={"political": 3, "economic": 5},
            sentiment_score=-0.4,
        )
        assert "crisis_probability_30d" in result
        assert "confidence" in result
        assert result["confidence"] in ["high", "medium", "low"]
