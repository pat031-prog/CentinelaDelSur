# ATALAYA - Sistema Integrado de Deteccion Temprana de Crisis Sistemicas

Early Warning System for Systemic Crises in Latin America and the Global South.

ATALAYA operates as a strategic watchtower that simultaneously monitors multiple critical domains to anticipate inflection points where gradual changes accelerate toward systemic ruptures.

## Monitored Domains

| Domain | Description |
|--------|-------------|
| Political-Institutional | Democratic erosion, governance failures, institutional collapse |
| Economic-Financial | Sovereign debt, inflation, currency stability, banking health |
| Supply Chain | Port congestion, shipping disruptions, critical resource availability |
| Geopolitical-Strategic | Territorial disputes, great power competition, military buildups |
| Climate-Environmental | Extreme weather, drought, deforestation, environmental tipping points |
| Technology-Digital | Cyber threats, digital infrastructure, information warfare |

## Alert Levels

- **GREEN** (0-30): Resilient institutions
- **YELLOW** (30-50): Systemic tension
- **ORANGE** (50-70): Pre-crisis, window closing
- **RED** (70-85): Imminent crisis (30-60 days)
- **BLACK** (>85): Collapse in progress

## Architecture

```
Backend:  Python 3.11+ / FastAPI / PostgreSQL+TimescaleDB / Redis
Frontend: React + TypeScript / Recharts / Vite
AI:       Anthropic Claude API for deep analysis
Infra:    Docker Compose
```

## Quick Start

### With Docker (recommended)

```bash
cp .env.example .env
# Edit .env with your API keys
docker compose up -d
```

- Backend API: http://localhost:8000
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

### Local Development

```bash
# Backend
pip install -r requirements.txt
uvicorn backend.api.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Run Tests

```bash
pytest tests/ -v
```

### Run Batch Analysis

```bash
python -m scripts.run_analysis
python -m scripts.run_analysis --country VEN
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/countries` | List monitored countries |
| GET | `/api/v1/countries/{code}` | Country overview |
| GET | `/api/v1/countries/{code}/risk` | Risk scores by domain |
| POST | `/api/v1/countries/{code}/analyze` | Deep analysis |
| GET | `/api/v1/regional/latam` | Regional overview |
| GET | `/api/v1/alerts` | Active alerts |
| GET | `/api/v1/alerts/summary` | Alert summary |
| GET | `/api/v1/domains/{domain}` | Cross-country domain analysis |
| POST | `/api/v1/scenarios/simulate` | Cascade simulation |
| GET | `/api/v1/historical/crises` | Historical crisis database |

## Project Structure

```
atalaya/
├── backend/
│   ├── api/           # FastAPI app and routes
│   ├── ingestion/     # Data collection modules
│   ├── processing/    # NLP, sentiment, anomaly detection
│   ├── modeling/      # Risk scoring, scenarios, cascade simulation
│   ├── intelligence/  # Claude analyst, report generation, alerts
│   └── utils/         # Config, logging, caching
├── frontend/          # React + TypeScript dashboard
├── scripts/           # Database setup and batch scripts
├── tests/             # Test suite
├── prompts/           # AI system prompts
└── data/              # Raw/processed data storage
```

## Configuration

Set these environment variables (or use `.env` file):

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | For DB features |
| `REDIS_URL` | Redis connection string | For caching |
| `ANTHROPIC_API_KEY` | Claude API key | For AI analysis |
| `NEWS_API_KEY` | NewsAPI key | For news ingestion |
| `FRED_API_KEY` | FRED API key | For economic data |
