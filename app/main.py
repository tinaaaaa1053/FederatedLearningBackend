"""
FederatedLearningBackend - FastAPI Application Entry Point

This is the main entry point for the Federated Learning Backend API.
It provides REST endpoints for the Vue3 frontend and integrates with
the FedLBE federated learning engine.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.config import settings
from app.api.router import api_router
from app.database import init_db
from app.utils import is_mock_mode
from app.services import (
    JobService, ModelService, ClientService,
    DataQualityService, SettingsService,
    MockJobService, MockModelService, MockClientService,
    MockDataQualityService, MockSettingsService
)


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting FederatedLearningBackend...")

    # Initialize database (only if not in mock mode)
    if not is_mock_mode():
        init_db()
        logger.info("Database initialized")

    # Start FedLBE integration only in non-mock mode
    app.state.job_manager = None
    app.state.client_registry = None
    if not is_mock_mode():
        from app.fedlbe.job_manager import job_manager
        from app.fedlbe.client_registry import client_registry

        await job_manager.start()
        await client_registry.start()
        app.state.job_manager = job_manager
        app.state.client_registry = client_registry
        logger.info("FedLBE integration started")
    else:
        logger.info("Mock mode enabled, skipping FedLBE integration startup")

    yield

    # Shutdown
    logger.info("Shutting down FederatedLearningBackend...")

    if app.state.job_manager is not None:
        await app.state.job_manager.stop()
    if app.state.client_registry is not None:
        await app.state.client_registry.stop()
    if app.state.job_manager is not None or app.state.client_registry is not None:
        logger.info("FedLBE integration stopped")


# Create FastAPI application
app = FastAPI(
    title="Federated Learning Backend",
    description="""
    REST API backend for the Federated Learning Platform.

    This backend provides:
    - **Dashboard**: Real-time overview of federated learning status
    - **Job Management**: Create, monitor, and manage FL jobs
    - **Model Management**: Store, retrieve, and compare trained models
    - **Client Management**: Register and monitor edge devices
    - **Data Quality**: Analyze data quality across clients
    - **Settings**: Platform configuration

    The backend integrates with FedLBE for actual federated learning orchestration.
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(api_router, prefix="/api")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    manager = getattr(app.state, "job_manager", None)
    fedlbe_connected = False
    if manager is not None:
        fedlbe_connected = bool(getattr(manager, "is_running", False))

    return {
        "status": "healthy",
        "version": "0.1.0",
        "fedlbe_connected": fedlbe_connected
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "name": "FederatedLearningBackend",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
