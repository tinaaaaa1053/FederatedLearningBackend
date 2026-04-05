"""
Job related schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.schemas.common import PaginatedResponse, PaginationRequest


class JobConfig(BaseModel):
    """Job configuration"""
    modelArchitecture: Optional[str] = None
    framework: Optional[str] = "PyTorch"
    dataset: Optional[str] = None
    batchSize: int = 32
    learningRate: float = 0.001
    optimizer: str = "Adam"
    lossFunction: str = "CrossEntropy"
    clients: int = 8
    minClients: int = 5
    maxClients: int = 8
    secureComm: bool = True
    secureAgg: bool = True
    differentialPrivacy: bool = False
    # FedLBE specific
    clientFraction: float = 1.0
    localEpochs: int = 5
    scheduler: str = "random"  # random, round_robin, full, latency
    compression: Optional[str] = None  # quantization, topk, random


class JobMetrics(BaseModel):
    """Job metrics history"""
    accuracy: List[float] = []
    loss: List[float] = []
    precision: List[float] = []
    recall: List[float] = []
    f1Score: List[float] = []
    train_loss: List[float] = []
    test_loss: List[float] = []
    round_time: List[float] = []


class JobClient(BaseModel):
    """Client participating in job"""
    id: str
    name: str
    status: str
    gpu: Optional[str] = None


class JobCreate(BaseModel):
    """Job creation request"""
    name: str
    description: Optional[str] = None
    jobType: str = "custom"
    algorithm: str = "FedAvg算法"
    totalRounds: int = 10
    config: JobConfig
    clientIds: List[str] = []
    modelFileContent: Optional[str] = None  # Base64 encoded model file


class JobUpdate(BaseModel):
    """Job update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class JobResponse(BaseModel):
    """Full job response"""
    id: str
    name: str
    description: Optional[str] = None
    status: str
    jobType: str
    algorithm: str
    currentRound: int
    totalRounds: int
    accuracy: float
    loss: float
    createdAt: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None
    clients: List[JobClient] = []
    metrics: Optional[JobMetrics] = None

    class Config:
        from_attributes = True


class JobListRequest(PaginationRequest):
    """Job list request with filters"""
    status: Optional[str] = None
    keyword: Optional[str] = None


class JobDetailResponse(BaseModel):
    """Detailed job response with all info"""
    id: str
    name: str
    description: Optional[str] = None
    status: str
    jobType: str
    algorithm: str
    currentRound: int
    totalRounds: int
    accuracy: float
    loss: float
    createdAt: Optional[datetime] = None
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None
    clients: List[JobClient] = []
    metrics: Optional[JobMetrics] = None

    class Config:
        from_attributes = True


class JobMetricsResponse(BaseModel):
    """Job metrics response"""
    rounds: List[int]
    accuracy: List[float]
    loss: List[float]
    precision: List[float]
    recall: List[float]
    f1Score: List[float]
    trainingTime: float
