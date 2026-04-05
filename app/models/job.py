"""
Job database model
"""
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Enum, Text
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid
from datetime import datetime


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class JobType(str, enum.Enum):
    MEDICAL = "medical"
    NLP = "nlp"
    FINANCE = "finance"
    AUTONOMOUS = "autonomous"
    RETAIL = "retail"
    CUSTOM = "custom"


class Algorithm(str, enum.Enum):
    FEDAVG = "FedAvg算法"
    FEDPROX = "FedProx算法"
    FEDOPT = "FedOpt算法"
    FEDSGD = "FedSGD算法"


def generate_job_id():
    """Generate job ID like FL-2023-001"""
    year = datetime.now().year
    random_suffix = str(uuid.uuid4().int % 1000).zfill(3)
    return f"FL-{year}-{random_suffix}"


class Job(Base):
    __tablename__ = "fl_jobs"

    id = Column(String(20), primary_key=True, default=generate_job_id)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    job_type = Column(Enum(JobType), default=JobType.CUSTOM)
    algorithm = Column(Enum(Algorithm), default=Algorithm.FEDAVG)

    # Progress
    current_round = Column(Integer, default=0)
    total_rounds = Column(Integer, nullable=False)

    # Metrics
    accuracy = Column(Float, default=0.0)
    loss = Column(Float, default=0.0)

    # Configuration (JSON)
    config = Column(JSON, default=dict)
    # {
    #   "modelArchitecture": "ResNet-50",
    #   "framework": "PyTorch",
    #   "dataset": "MNIST",
    #   "batchSize": 32,
    #   "learningRate": 0.001,
    #   "optimizer": "Adam",
    #   "lossFunction": "CrossEntropy",
    #   "clients": 8,
    #   "minClients": 5,
    #   "maxClients": 8,
    #   "secureComm": true,
    #   "secureAgg": true,
    #   "differentialPrivacy": false
    # }

    # Metrics history (JSON)
    metrics = Column(JSON, default=dict)
    # {
    #   "accuracy": [0.68, 0.72, ...],
    #   "loss": [1.245, 1.082, ...],
    #   "round_time": [10.5, 12.3, ...],
    #   "train_loss": [...],
    #   "test_loss": [...]
    # }

    # Client IDs participating in this job
    client_ids = Column(JSON, default=list)

    # FedLBE specific
    fedlbe_job_id = Column(String(50), nullable=True)  # Reference to FedLBE job
    model_file_path = Column(String(500), nullable=True)  # Path to uploaded model file

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Owner
    user_id = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<Job {self.id}: {self.name} ({self.status})>"
