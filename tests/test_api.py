"""Tests for ATALAYA API endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app


client = TestClient(app)


class TestRootEndpoints:
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["system"] == "ATALAYA"
        assert data["status"] == "operational"

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestCountryEndpoints:
    def test_list_countries(self):
        response = client.get("/api/v1/countries")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Should be sorted by risk score descending
        scores = [c["current_risk_score"] for c in data]
        assert scores == sorted(scores, reverse=True)

    def test_list_countries_filter_region(self):
        response = client.get("/api/v1/countries?region=Caribbean")
        assert response.status_code == 200
        data = response.json()
        for country in data:
            assert country["region"] == "Caribbean"

    def test_get_country_valid(self):
        response = client.get("/api/v1/countries/ARG")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "ARG"
        assert data["name"] == "Argentina"
        assert "risk_assessment" in data

    def test_get_country_case_insensitive(self):
        response = client.get("/api/v1/countries/arg")
        assert response.status_code == 200
        assert response.json()["code"] == "ARG"

    def test_get_country_not_found(self):
        response = client.get("/api/v1/countries/ZZZ")
        assert response.status_code == 404

    def test_get_country_risk(self):
        response = client.get("/api/v1/countries/VEN/risk")
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "level" in data
        assert "domains" in data
        assert "crisis_probability" in data

    def test_get_country_indicators(self):
        response = client.get("/api/v1/countries/BRA/indicators")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


class TestAnalysisEndpoints:
    def test_deep_analysis(self):
        response = client.post(
            "/api/v1/countries/ARG/analyze",
            json={"depth": "standard", "domains": ["political", "economic"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["country_code"] == "ARG"
        assert "risk_assessment" in data
        assert "scenarios" in data
        assert "report_text" in data

    def test_cascade_simulation(self):
        response = client.post(
            "/api/v1/scenarios/simulate",
            json={
                "country_code": "ARG",
                "trigger_event": "Sovereign debt default",
                "parameters": {"shock_magnitude": 35},
                "time_horizon_days": 90,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "cascade_result" in data
        assert "intervention_points" in data
        assert data["initial_domain"] == "economic"

    def test_regional_overview(self):
        response = client.get("/api/v1/regional/latam")
        assert response.status_code == 200
        data = response.json()
        assert "total_countries" in data
        assert data["total_countries"] == 20
        assert "countries_by_risk" in data
        assert "risk_distribution" in data

    def test_historical_crises(self):
        response = client.get("/api/v1/historical/crises")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_historical_crises_filter(self):
        response = client.get("/api/v1/historical/crises?country_code=ARG")
        assert response.status_code == 200
        data = response.json()
        for crisis in data:
            assert crisis["country_code"] == "ARG"


class TestDomainEndpoints:
    def test_list_domains(self):
        response = client.get("/api/v1/domains")
        assert response.status_code == 200
        data = response.json()
        assert "political" in data
        assert "economic" in data
        assert "supply_chain" in data

    def test_analyze_domain(self):
        response = client.get("/api/v1/domains/economic")
        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == "economic"
        assert "countries" in data
        assert "regional_average" in data


class TestAlertEndpoints:
    def test_get_alerts(self):
        response = client.get("/api/v1/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "alerts" in data

    def test_get_alerts_filter_country(self):
        response = client.get("/api/v1/alerts?country_code=VEN")
        assert response.status_code == 200
        data = response.json()
        for alert in data["alerts"]:
            assert alert["country_code"] == "VEN"

    def test_alert_summary(self):
        response = client.get("/api/v1/alerts/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_active" in data
        assert "by_level" in data
        assert "by_country" in data
