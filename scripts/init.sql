-- ATALAYA Database Initialization
-- PostgreSQL + TimescaleDB schema

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Countries table
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    code VARCHAR(3) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_es VARCHAR(100),
    region VARCHAR(50),
    subregion VARCHAR(50),
    capital VARCHAR(100),
    population BIGINT,
    gdp_usd BIGINT,
    metadata JSONB DEFAULT '{}'
);

-- Risk scores (time-series optimized)
CREATE TABLE IF NOT EXISTS risk_scores (
    id SERIAL,
    time TIMESTAMPTZ NOT NULL,
    country_code VARCHAR(3) NOT NULL REFERENCES countries(code),
    domain VARCHAR(50) NOT NULL,
    score FLOAT NOT NULL CHECK (score >= 0 AND score <= 100),
    level VARCHAR(20),
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    metadata JSONB DEFAULT '{}'
);

SELECT create_hypertable('risk_scores', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS ix_risk_scores_country_domain ON risk_scores (country_code, domain, time DESC);

-- Indicators (time-series optimized)
CREATE TABLE IF NOT EXISTS indicators (
    id SERIAL,
    time TIMESTAMPTZ NOT NULL,
    country_code VARCHAR(3) REFERENCES countries(code),
    indicator_type VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(50),
    source VARCHAR(200),
    metadata JSONB DEFAULT '{}'
);

SELECT create_hypertable('indicators', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS ix_indicators_country_type ON indicators (country_code, indicator_type, time DESC);

-- Events
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    country_code VARCHAR(3) REFERENCES countries(code),
    event_type VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    source VARCHAR(200),
    url TEXT,
    severity VARCHAR(20),
    sentiment FLOAT,
    entities JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS ix_events_country_time ON events (country_code, timestamp DESC);
CREATE INDEX IF NOT EXISTS ix_events_type ON events (event_type);

-- Alerts
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    country_code VARCHAR(3) NOT NULL REFERENCES countries(code),
    alert_level VARCHAR(20) NOT NULL,
    domain VARCHAR(50),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    probability FLOAT,
    time_horizon INT,
    triggered_by JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_alerts_country ON alerts (country_code, is_active);
CREATE INDEX IF NOT EXISTS ix_alerts_level ON alerts (alert_level);

-- Scenarios
CREATE TABLE IF NOT EXISTS scenarios (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    country_code VARCHAR(3) NOT NULL REFERENCES countries(code),
    scenario_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    probability FLOAT NOT NULL,
    conditions JSONB DEFAULT '{}',
    consequences JSONB DEFAULT '{}',
    timeframe INT
);

CREATE INDEX IF NOT EXISTS ix_scenarios_country ON scenarios (country_code);

-- Historical crises (for pattern matching)
CREATE TABLE IF NOT EXISTS historical_crises (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(3) NOT NULL REFERENCES countries(code),
    year INT NOT NULL,
    crisis_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    causes JSONB DEFAULT '{}',
    outcome JSONB DEFAULT '{}',
    lessons JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS ix_historical_country ON historical_crises (country_code);
CREATE INDEX IF NOT EXISTS ix_historical_type ON historical_crises (crisis_type);

-- Seed Latin American countries
INSERT INTO countries (code, name, name_es, region, subregion, capital, population, gdp_usd) VALUES
    ('ARG', 'Argentina', 'Argentina', 'South America', 'Southern Cone', 'Buenos Aires', 46010000, 641000000000),
    ('BOL', 'Bolivia', 'Bolivia', 'South America', 'Andean', 'La Paz', 12080000, 44000000000),
    ('BRA', 'Brazil', 'Brasil', 'South America', 'Atlantic', 'Brasilia', 214300000, 1920000000000),
    ('CHL', 'Chile', 'Chile', 'South America', 'Southern Cone', 'Santiago', 19490000, 301000000000),
    ('COL', 'Colombia', 'Colombia', 'South America', 'Andean', 'Bogota', 51870000, 343000000000),
    ('CRI', 'Costa Rica', 'Costa Rica', 'Central America', 'Central America', 'San Jose', 5150000, 68400000000),
    ('CUB', 'Cuba', 'Cuba', 'Caribbean', 'Caribbean', 'Havana', 11260000, 107000000000),
    ('DOM', 'Dominican Republic', 'Republica Dominicana', 'Caribbean', 'Caribbean', 'Santo Domingo', 11120000, 113000000000),
    ('ECU', 'Ecuador', 'Ecuador', 'South America', 'Andean', 'Quito', 18000000, 115000000000),
    ('SLV', 'El Salvador', 'El Salvador', 'Central America', 'Central America', 'San Salvador', 6520000, 32490000000),
    ('GTM', 'Guatemala', 'Guatemala', 'Central America', 'Central America', 'Guatemala City', 17610000, 95000000000),
    ('GUY', 'Guyana', 'Guyana', 'South America', 'Caribbean', 'Georgetown', 805000, 14720000000),
    ('HND', 'Honduras', 'Honduras', 'Central America', 'Central America', 'Tegucigalpa', 10280000, 31720000000),
    ('MEX', 'Mexico', 'Mexico', 'North America', 'North America', 'Mexico City', 128900000, 1322000000000),
    ('NIC', 'Nicaragua', 'Nicaragua', 'Central America', 'Central America', 'Managua', 6950000, 15670000000),
    ('PAN', 'Panama', 'Panama', 'Central America', 'Central America', 'Panama City', 4380000, 76520000000),
    ('PRY', 'Paraguay', 'Paraguay', 'South America', 'Southern Cone', 'Asuncion', 7220000, 42960000000),
    ('PER', 'Peru', 'Peru', 'South America', 'Andean', 'Lima', 33720000, 242630000000),
    ('URY', 'Uruguay', 'Uruguay', 'South America', 'Southern Cone', 'Montevideo', 3490000, 71180000000),
    ('VEN', 'Venezuela', 'Venezuela', 'South America', 'Andean', 'Caracas', 28440000, 92200000000),
    ('SUR', 'Suriname', 'Surinam', 'South America', 'Caribbean', 'Paramaribo', 620000, 3620000000)
ON CONFLICT (code) DO NOTHING;

-- Seed historical crises
INSERT INTO historical_crises (country_code, year, crisis_type, description, causes, outcome, lessons) VALUES
    ('ARG', 2001, 'economic_default', 'Sovereign debt default, banking crisis, corralito, currency devaluation, social unrest',
     '{"primary": ["unsustainable_debt", "currency_peg_collapse", "capital_flight"], "secondary": ["political_instability", "imf_policies"]}',
     '{"recovery_years": 3, "gdp_loss_pct": -11, "presidents_in_2_weeks": 5, "migration": "significant"}',
     '{"key": ["currency_pegs_are_fragile", "imf_austerity_can_backfire", "social_contract_matters"]}'),
    ('VEN', 2014, 'economic_collapse', 'Oil price crash triggers economic collapse, hyperinflation, mass migration',
     '{"primary": ["oil_dependency", "price_controls", "currency_controls"], "secondary": ["institutional_decay", "sanctions"]}',
     '{"recovery_years": null, "gdp_loss_pct": -75, "migration": "7_million_plus", "hyperinflation": true}',
     '{"key": ["resource_curse", "institutional_destruction_is_hard_to_reverse", "migration_affects_entire_region"]}'),
    ('PER', 2020, 'political_crisis', 'Rapid succession of presidents, institutional vacuum, social protests',
     '{"primary": ["corruption", "weak_parties", "congressional_fragmentation"], "secondary": ["pandemic_stress", "inequality"]}',
     '{"recovery_years": 2, "gdp_loss_pct": -11, "presidents_in_5_years": 6}',
     '{"key": ["institutional_design_matters", "anti_corruption_backlash", "pandemic_amplifies_fragility"]}'),
    ('CHL', 2019, 'social_unrest', 'Mass protests against inequality, constitutional process initiated',
     '{"primary": ["inequality", "pension_crisis", "healthcare_costs"], "secondary": ["metro_fare_increase_trigger", "generational_frustration"]}',
     '{"recovery_years": 2, "gdp_loss_pct": -6, "constitutional_process": true}',
     '{"key": ["inequality_is_combustible", "small_triggers_big_explosions", "institutional_channels_help"]}'),
    ('BRA', 2015, 'political_economic', 'Impeachment crisis combined with deep recession and Lava Jato corruption scandal',
     '{"primary": ["corruption_scandal", "fiscal_mismanagement", "commodity_bust"], "secondary": ["political_polarization", "institutional_crisis"]}',
     '{"recovery_years": 3, "gdp_loss_pct": -7, "impeachment": true}',
     '{"key": ["corruption_investigations_destabilize", "commodity_dependency", "polarization_feeds_on_crisis"]}'),
    ('MEX', 1994, 'currency_crisis', 'Tequila crisis - peso devaluation, capital flight, banking crisis',
     '{"primary": ["current_account_deficit", "political_instability", "overvalued_peso"], "secondary": ["zapatista_uprising", "assassinations"]}',
     '{"recovery_years": 2, "gdp_loss_pct": -6, "us_bailout": true}',
     '{"key": ["sudden_stops_are_devastating", "political_risk_matters", "external_support_helps_recovery"]}'),
    ('ECU', 2019, 'social_unrest', 'Fuel subsidy removal triggers indigenous-led protests, state of emergency',
     '{"primary": ["imf_austerity", "fuel_subsidy_removal"], "secondary": ["indigenous_organization", "inequality"]}',
     '{"recovery_years": 1, "gdp_loss_pct": -1, "subsidy_partially_restored": true}',
     '{"key": ["subsidy_removal_needs_compensation", "indigenous_movements_powerful", "dialogue_resolves"]}'),
    ('URY', 2002, 'banking_crisis', 'Banking system collapse triggered by Argentine contagion',
     '{"primary": ["argentine_contagion", "dollar_deposits", "bank_runs"], "secondary": ["regional_integration_risk"]}',
     '{"recovery_years": 2, "gdp_loss_pct": -11, "institutional_resilience": "high"}',
     '{"key": ["contagion_is_real", "strong_institutions_help_recover", "dollarization_risk"]}')
ON CONFLICT DO NOTHING;
