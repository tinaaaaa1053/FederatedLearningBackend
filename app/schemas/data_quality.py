"""
Data quality related schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.common import PaginatedResponse, PaginationRequest


class QualityStats(BaseModel):
    """Data quality statistics"""
    totalSamples: int
    missingRate: float
    imbalanceScore: float
    noiseLevel: float
    criticalWarnings: int
    warnings: int
    infoAlerts: int


class QualityDistribution(BaseModel):
    """Data quality distribution"""
    highQuality: int
    mediumQuality: int
    lowQuality: int


class NodeQuality(BaseModel):
    """Node quality data"""
    nodeId: str
    name: str
    quality: float
    samples: int
    missingRate: float
    noiseLevel: float
    x: float
    y: float
    z: float
    category: str


class Warning(BaseModel):
    """Warning/alert"""
    id: str
    type: str  # critical, warning, info
    nodeId: str
    title: str
    message: str
    timestamp: str


class WarningListRequest(PaginationRequest):
    """Warning list request with filters"""
    type: Optional[str] = None
