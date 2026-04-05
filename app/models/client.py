"""
Client (edge device) database model
"""
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Enum, Text
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid
from datetime import datetime


class ClientStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"


class DeviceType(str, enum.Enum):
    EDGE_SERVER = "Edge Server"
    CLOUD_SERVER = "Cloud Server"
    DESKTOP = "Desktop"
    IOT_GATEWAY = "IoT Gateway"


def generate_client_id():
    """Generate client ID"""
    random_suffix = str(uuid.uuid4().int % 1000).zfill(3)
    return f"FL-CLIENT-{random_suffix}"


class Client(Base):
    __tablename__ = "fl_clients"

    id = Column(String(20), primary_key=True, default=generate_client_id)
    name = Column(String(255), nullable=False)
    status = Column(Enum(ClientStatus), default=ClientStatus.OFFLINE)
    device_type = Column(Enum(DeviceType), default=DeviceType.EDGE_SERVER)

    # Connection info
    ip_address = Column(String(50), nullable=True)
    port = Column(Integer, nullable=True)
    connected_at = Column(DateTime, nullable=True)
    last_heartbeat = Column(DateTime, nullable=True)

    # Hardware info
    gpu = Column(String(100), nullable=True)
    cpu = Column(String(100), nullable=True)
    memory = Column(String(20), nullable=True)
    os = Column(String(50), nullable=True)

    # Device info (JSON)
    device_info = Column(JSON, default=dict)
    # {
    #   "type": "Edge Server",
    #   "ipAddress": "192.168.1.105",
    #   "port": 50051,
    #   "os": "Ubuntu 20.04 LTS",
    #   "cpu": "Intel Core i7-8700K",
    #   "memory": "32 GB",
    #   "gpu": "NVIDIA RTX A6000"
    # }

    # Resource usage (JSON)
    resource_usage = Column(JSON, default=dict)
    # {
    #   "cpuUsage": 45.5,
    #   "memoryUsage": 62.3,
    #   "diskUsage": 30.1,
    #   "networkIO": 125.6
    # }

    # Statistics
    job_count = Column(Integer, default=0)
    participated_jobs = Column(JSON, default=list)
    # [
    #   {
    #     "jobId": "FL-2023-001",
    #     "jobName": "Medical Image Segmentation",
    #     "status": "completed",
    #     "accuracy": 92.4,
    #     "completedAt": "2023-06-15T10:30:00"
    #   }
    # ]

    # Performance metrics (JSON)
    performance_metrics = Column(JSON, default=dict)
    # {
    #   "days": 30,
    #   "trainingTime": 120.5,
    #   "dataTransfer": 15.3
    # }

    # FedLBE port
    fedlbe_port = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Client {self.id}: {self.name} ({self.status})>"
