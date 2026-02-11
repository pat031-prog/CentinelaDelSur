from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import analysis, countries, domains, alerts, market
from backend.api.models.database import init_db
from backend.utils.cache import cache
from backend.utils.config import settings
from backend.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Startup
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")

    try:
        await cache.connect()
        logger.info("Redis cache connected")
    except Exception as e:
        logger.warning(f"Redis connection skipped: {e}")

    yield

    # Shutdown
    await cache.disconnect()
    logger.info(f"{settings.app_name} shutting down")


app = FastAPI(
    title=settings.app_name,
    description="Early Warning System for Systemic Crises in Latin America",
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(countries.router, prefix="/api/v1", tags=["Countries"])
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(domains.router, prefix="/api/v1", tags=["Domains"])
app.include_router(alerts.router, prefix="/api/v1", tags=["Alerts"])
app.include_router(market.router, prefix="/api/v1", tags=["Market"])


@app.get("/")
async def root():
    """Root endpoint with system info."""
    return {
        "system": settings.app_name,
        "version": settings.app_version,
        "description": "Early Warning System for Systemic Crises",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "countries": "/api/v1/countries",
            "analysis": "/api/v1/analysis",
            "domains": "/api/v1/domains",
            "alerts": "/api/v1/alerts",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "system": settings.app_name}
