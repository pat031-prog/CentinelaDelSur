from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://atalaya:atalaya@localhost:5432/atalaya_db"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # API Keys
    anthropic_api_key: Optional[str] = None
    news_api_key: Optional[str] = None
    fred_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None

    # App config
    app_name: str = "ATALAYA"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    # Analysis defaults
    default_time_horizon_days: int = 90
    risk_score_cache_ttl: int = 3600  # seconds
    max_events_per_query: int = 100

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
