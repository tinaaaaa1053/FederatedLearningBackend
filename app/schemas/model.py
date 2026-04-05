"""
Model related schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.schemas.common import PaginatedResponse, PaginationRequest


class ModelMetrics(BaseModel):
    """Model metrics history"""
    accuracy: List[float] = []
    loss: List[float] = []
    precision: List[float] = []
    recall: List[float] = []


class ModelResponse(BaseModel):
    """Model response"""
    id: str
    name: str
    jobId: Optional[str] = None
    accuracy: float
    loss: float
    createdAt: Optional[datetime] = None
    framework: Optional[str] = None
    parameters: Optional[str] = None
    size: Optional[str] = None
    architecture: Optional[str] = None
    dataset: Optional[str] = None
    rounds: int = 0
    clients: int = 0
    metrics: Optional[ModelMetrics] = None

    class Config:
        from_attributes = True


class ModelDetailResponse(BaseModel):
    """Detailed model response"""
    id: str
    name: str
    jobId: Optional[str] = None
    accuracy: float
    loss: float
    createdAt: Optional[datetime] = None
    framework: Optional[str] = None
    parameters: Optional[str] = None
    size: Optional[str] = None
    architecture: Optional[str] = None
    dataset: Optional[str] = None
    rounds: int = 0
    clients: int = 0
    metrics: Optional[ModelMetrics] = None

    class Config:
        from_attributes = True


class ModelListRequest(PaginationRequest):
    """Model list request with filters"""
    keyword: Optional[str] = None
    jobId: Optional[str] = None


class ModelUpload(BaseModel):
    """Model upload request"""
    name: str
    jobId: Optional[str] = None
    framework: Optional[str] = "PyTorch"
    architecture: Optional[str] = None


class ModelComparison(BaseModel):
    """Model comparison result"""
    modelIds: List[str]
    comparisonData: Dict[str, Any]


class ModelComparisonRequest(BaseModel):
    """Model comparison request"""
    modelIds: List[str] = Field(..., min_length=2, max_length=2)
