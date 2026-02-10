from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, BigInteger, String, Float, Boolean, Text,
    DateTime, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from backend.utils.config import settings


class Base(DeclarativeBase):
    pass


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(3), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    name_es = Column(String(100))
    region = Column(String(50))
    subregion = Column(String(50))
    capital = Column(String(100))
    population = Column(BigInteger)
    gdp_usd = Column(BigInteger)
    metadata_ = Column("metadata", JSONB, default={})

    risk_scores = relationship("RiskScore", back_populates="country")
    indicators = relationship("Indicator", back_populates="country")
    events = relationship("Event", back_populates="country")
    alerts = relationship("Alert", back_populates="country")


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime(timezone=True), nullable=False, index=True)
    country_code = Column(String(3), ForeignKey("countries.code"), nullable=False, index=True)
    domain = Column(String(50), nullable=False, index=True)
    score = Column(Float, nullable=False)
    level = Column(String(20))
    confidence = Column(Float)
    metadata_ = Column("metadata", JSONB, default={})

    country = relationship("Country", back_populates="risk_scores")

    __table_args__ = (
        Index("ix_risk_scores_country_domain_time", "country_code", "domain", "time"),
    )


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime(timezone=True), nullable=False, index=True)
    country_code = Column(String(3), ForeignKey("countries.code"), index=True)
    indicator_type = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    source = Column(String(200))
    metadata_ = Column("metadata", JSONB, default={})

    country = relationship("Country", back_populates="indicators")

    __table_args__ = (
        Index("ix_indicators_country_type_time", "country_code", "indicator_type", "time"),
    )


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    country_code = Column(String(3), ForeignKey("countries.code"), index=True)
    event_type = Column(String(50), nullable=False, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    source = Column(String(200))
    url = Column(Text)
    severity = Column(String(20))
    sentiment = Column(Float)
    entities = Column(JSONB, default={})
    metadata_ = Column("metadata", JSONB, default={})

    country = relationship("Country", back_populates="events")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    country_code = Column(String(3), ForeignKey("countries.code"), nullable=False, index=True)
    alert_level = Column(String(20), nullable=False, index=True)
    domain = Column(String(50), index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    probability = Column(Float)
    time_horizon = Column(Integer)  # days
    triggered_by = Column(JSONB, default={})
    is_active = Column(Boolean, default=True, index=True)
    resolved_at = Column(DateTime(timezone=True))

    country = relationship("Country", back_populates="alerts")


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    country_code = Column(String(3), ForeignKey("countries.code"), nullable=False, index=True)
    scenario_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    probability = Column(Float, nullable=False)
    conditions = Column(JSONB, default={})
    consequences = Column(JSONB, default={})
    timeframe = Column(Integer)  # days

    country = relationship("Country")


class HistoricalCrisis(Base):
    __tablename__ = "historical_crises"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_code = Column(String(3), ForeignKey("countries.code"), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    crisis_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    causes = Column(JSONB, default={})
    outcome = Column(JSONB, default={})
    lessons = Column(JSONB, default={})

    country = relationship("Country")


# Database engine and session setup
def get_async_engine():
    db_url = settings.database_url
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return create_async_engine(db_url, echo=settings.debug)


engine = get_async_engine()
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """Dependency for FastAPI to get a database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
