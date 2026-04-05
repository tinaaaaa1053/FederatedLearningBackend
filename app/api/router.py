"""
Main API router aggregating all route modules
"""
from fastapi import APIRouter
from app.api import dashboard, job, model, client, data_quality, settings as settings_api
from app.utils import is_mock_mode
from app.services import (
    JobService, ModelService, ClientService,
    DataQualityService, SettingsService,
    MockJobService, MockModelService, MockClientService,
    MockDataQualityService, MockSettingsService
)

# Create service instances based on mode
if is_mock_mode():
    job_service = MockJobService()
    model_service = MockModelService()
    client_service = MockClientService()
    data_quality_service = MockDataQualityService()
    settings_service = MockSettingsService()
else:
    job_service = JobService()
    model_service = ModelService()
    client_service = ClientService()
    data_quality_service = DataQualityService()
    settings_service = SettingsService()

api_router = APIRouter()

# Include all API routes with appropriate service instances
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(lambda: job_service)]
)
api_router.include_router(
    job.router,
    prefix="/job",
    tags=["Job Management"],
    dependencies=[Depends(lambda: job_service)]
)
api_router.include_router(
    model.router,
    prefix="/model",
    tags=["Model Management"],
    dependencies=[Depends(lambda: model_service)]
)
api_router.include_router(
    client.router,
    prefix="/client",
    tags=["Client Management"],
    dependencies=[Depends(lambda: client_service)]
)
api_router.include_router(
    data_quality.router,
    prefix="/dataQuality",
    tags=["Data Quality"],
    dependencies=[Depends(lambda: data_quality_service)]
)
api_router.include_router(
    settings_api.router,
    prefix="/settings",
    tags=["Settings"],
    dependencies=[Depends(lambda: settings_service)]
)
