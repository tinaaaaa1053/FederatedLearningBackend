"""
Dashboard related schemas
"""
from pydantic import BaseModel
from typing import List, Optional


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    activeJobs: int
    completedJobs: int
    totalClients: int
    onlineClients: int


class ClientInfo(BaseModel):
    """Brief client info for dashboard"""
    id: str
    name: str
    gpu: Optional[str] = None
    status: str


class CurrentJob(BaseModel):
    """Current running job info"""
    jobId: str
    jobName: str
    progress: float
    currentRound: int
    totalRounds: int
    accuracy: float
    loss: float
    activeClients: int
    totalClients: int
    estimatedTimeRemaining: Optional[str] = None


class ChartData(BaseModel):
    """Chart data for accuracy/loss visualization"""
    rounds: List[str]
    accuracy: Optional[List[float]] = None
    loss: Optional[List[float]] = None
