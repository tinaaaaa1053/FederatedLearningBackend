"""Services module"""
from app.services.mock_service import (
    MockJobService, MockModelService, MockClientService,
    MockDataQualityService, MockSettingsService
)
# 导入真实服务（如果不需要数据库，可以注释掉）
# from app.services.job_service import JobService
# from app.services.model_service import ModelService
# from app.services.client_service import ClientService
# from app.services.data_quality_service import DataQualityService
# from app.services.settings_service import SettingsService

# 使用 Mock 服务替代真实服务
JobService = MockJobService
ModelService = MockModelService
ClientService = MockClientService
DataQualityService = MockDataQualityService
SettingsService = MockSettingsService

__all__ = [
    "MockJobService", "MockModelService", "MockClientService",
    "MockDataQualityService", "MockSettingsService",
    "JobService", "ModelService", "ClientService",
    "DataQualityService", "SettingsService"
]