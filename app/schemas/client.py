"""
Client related schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.schemas.common import PaginatedResponse, PaginationRequest


class DeviceInfo(BaseModel):
    """Device information"""
    type: Optional[str] = None
    ipAddress: Optional[str] = None
    port: Optional[int] = None
    os: Optional[str] = None
    cpu: Optional[str] = None
    memory: Optional[str] = None
    gpu: Optional[str] = None


class ResourceUsage(BaseModel):
    """Resource usage"""
    cpuUsage: float = 0.0
    memoryUsage: float = 0.0
    diskUsage: float = 0.0
    networkIO: float = 0.0


class ParticipatedJob(BaseModel):
    """Participated job info"""
    jobId: str
    jobName: str
    status: str
    accuracy: Optional[float] = None
    completedAt: Optional[str] = None


class PerformanceMetrics(BaseModel):
    """Performance metrics"""
    days: int = 0
    trainingTime: float = 0.0
    dataTransfer: float = 0.0


class ClientResponse(BaseModel):
    """Client response"""
    id: str
    name: str
    status: str
    connectedAt: Optional[datetime] = None
    jobCount: int = 0
    gpu: Optional[str] = None
    cpu: Optional[str] = None
    memory: Optional[str] = None
    os: Optional[str] = None
    ipAddress: Optional[str] = None
    port: Optional[int] = None
    deviceType: Optional[str] = None

    class Config:
        from_attributes = True


class ClientDetailResponse(BaseModel):
    """Detailed client response"""
    id: str
    name: str
    status: str
    deviceType: Optional[str] = None
    connectedAt: Optional[datetime] = None
    lastHeartbeat: Optional[datetime] = None
    jobCount: int = 0
    gpu: Optional[str] = None
    cpu: Optional[str] = None
    memory: Optional[str] = None
    os: Optional[str] = None
    ipAddress: Optional[str] = None
    port: Optional[int] = None
    deviceInfo: Optional[DeviceInfo] = None
    resourceUsage: Optional[ResourceUsage] = None
    participatedJobs: List[ParticipatedJob] = []
    performanceMetrics: Optional[PerformanceMetrics] = None

    class Config:
        from_attributes = True


class ClientListRequest(PaginationRequest):
    """Client list request with filters"""
    status: Optional[str] = None
    keyword: Optional[str] = None


class ClientCreate(BaseModel):
    """Client creation request"""
    name: str
    deviceType: str = "Edge Server"
    ipAddress: Optional[str] = None
    port: Optional[int] = None
    fedlbePort: Optional[int] = None
    gpu: Optional[str] = None
    cpu: Optional[str] = None
    memory: Optional[str] = None
    os: Optional[str] = None


class ClientUpdate(BaseModel):
    """Client update request"""
    name: Optional[str] = None
    deviceType: Optional[str] = None
    ipAddress: Optional[str] = None
    port: Optional[int] = None
    fedlbePort: Optional[int] = None
    gpu: Optional[str] = None
    cpu: Optional[str] = None
    memory: Optional[str] = None
    os: Optional[str] = None
