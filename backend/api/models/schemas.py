from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AlertLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"
    BLACK = "black"


class Domain(str, Enum):
    POLITICAL = "political"
    ECONOMIC = "economic"
    SUPPLY_CHAIN = "supply_chain"
    GEOPOLITICAL = "geopolitical"
    CLIMATE = "climate"
    TECHNOLOGY = "technology"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ScenarioType(str, Enum):
    OPTIMISTIC = "optimistic"
    BASE = "base"
    PESSIMISTIC = "pessimistic"
    COLLAPSE = "collapse"


class Trend(str, Enum):
    WORSENING = "worsening"
    STABLE = "stable"
    IMPROVING = "improving"


# --- Country schemas ---

class CountryBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=3)
    name: str
    name_es: Optional[str] = None
    region: Optional[str] = None
    subregion: Optional[str] = None
    capital: Optional[str] = None
    population: Optional[int] = None
    gdp_usd: Optional[int] = None


class CountryResponse(CountryBase):
    id: int
    current_risk_level: Optional[AlertLevel] = None
    current_risk_score: Optional[float] = None

    model_config = {"from_attributes": True}


class CountryOverview(CountryResponse):
    domain_scores: Dict[str, float] = {}
    active_alerts_count: int = 0
    recent_events_count: int = 0
    trend: Optional[Trend] = None


# --- Risk Score schemas ---

class RiskScoreBase(BaseModel):
    country_code: str
    domain: Domain
    score: float = Field(..., ge=0, le=100)
    level: Optional[AlertLevel] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)


class RiskScoreResponse(RiskScoreBase):
    time: datetime
    metadata: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}


class RiskScoreTimeSeries(BaseModel):
    country_code: str
    domain: Domain
    data_points: List[RiskScoreResponse]


# --- Indicator schemas ---

class IndicatorResponse(BaseModel):
    time: datetime
    country_code: Optional[str] = None
    indicator_type: str
    value: float
    unit: Optional[str] = None
    source: Optional[str] = None

    model_config = {"from_attributes": True}


# --- Event schemas ---

class EventResponse(BaseModel):
    id: int
    timestamp: datetime
    country_code: Optional[str] = None
    event_type: str
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    severity: Optional[Severity] = None
    sentiment: Optional[float] = None

    model_config = {"from_attributes": True}


# --- Alert schemas ---

class AlertResponse(BaseModel):
    id: int
    created_at: datetime
    country_code: str
    alert_level: AlertLevel
    domain: Optional[Domain] = None
    title: str
    description: str
    probability: Optional[float] = None
    time_horizon: Optional[int] = None
    is_active: bool = True

    model_config = {"from_attributes": True}


# --- Scenario schemas ---

class ScenarioResponse(BaseModel):
    id: int
    created_at: datetime
    country_code: str
    scenario_type: ScenarioType
    title: str
    description: str
    probability: float
    conditions: Optional[Dict[str, Any]] = None
    consequences: Optional[Dict[str, Any]] = None
    timeframe: Optional[int] = None

    model_config = {"from_attributes": True}


# --- Analysis request/response ---

class AnalysisRequest(BaseModel):
    domains: List[Domain] = list(Domain)
    depth: str = Field("standard", pattern="^(standard|deep|comprehensive)$")
    time_horizon_days: int = Field(90, ge=7, le=365)


class CascadeSimulationRequest(BaseModel):
    country_code: str
    trigger_event: str
    parameters: Dict[str, Any] = {}
    time_horizon_days: int = Field(90, ge=7, le=365)


class DomainScore(BaseModel):
    domain: Domain
    score: float
    level: AlertLevel
    trend: Trend
    key_signals: List[str] = []


class CrisisProbability(BaseModel):
    days_30: float
    days_60: float
    days_90: float
    margin: float
    most_likely_type: str
    confidence: str


class SystemicRiskReport(BaseModel):
    """Full ATALAYA systemic risk report."""
    country_code: str
    country_name: str
    timestamp: datetime
    global_alert_level: AlertLevel
    fragility_index: float
    domain_scores: List[DomainScore]
    crisis_probability: CrisisProbability
    critical_signals: List[Dict[str, Any]]
    interdependencies: str
    feedback_loops: List[Dict[str, str]]
    scenarios: List[ScenarioResponse]
    tipping_points: List[Dict[str, Any]]
    cascade_risks: List[Dict[str, Any]]
    priority_indicators: List[Dict[str, Any]]
    historical_comparison: List[Dict[str, Any]]
    window_of_opportunity: Dict[str, Any]
    confidence: str
    limitations: List[str]


# --- Historical crisis schemas ---

class HistoricalCrisisResponse(BaseModel):
    id: int
    country_code: str
    year: int
    crisis_type: str
    description: str
    causes: Optional[Dict[str, Any]] = None
    outcome: Optional[Dict[str, Any]] = None
    lessons: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}
