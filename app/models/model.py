"""
Model (trained model) database model
"""
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base
import uuid
from datetime import datetime


def generate_model_id():
    """Generate model ID"""
    random_suffix = str(uuid.uuid4().int % 10000).zfill(4)
    return f"model-{random_suffix}"


class Model(Base):
    __tablename__ = "fl_models"

    id = Column(String(20), primary_key=True, default=generate_model_id)
    name = Column(String(255), nullable=False)

    # Associated job
    job_id = Column(String(20), nullable=True)

    # Model info
    framework = Column(String(50), default="PyTorch")
    architecture = Column(String(100), nullable=True)
    dataset = Column(String(100), nullable=True)
    parameters = Column(String(20), nullable=True)  # e.g., "25.6M"
    size = Column(String(20), nullable=True)  # e.g., "98.2 MB"

    # Training info
    rounds = Column(Integer, default=0)
    clients = Column(Integer, default=0)

    # Metrics
    accuracy = Column(Float, default=0.0)
    loss = Column(Float, default=0.0)

    # Metrics history (JSON)
    metrics = Column(JSON, default=dict)
    # {
    #   "accuracy": [72, 78, 82, ...],
    #   "loss": [0.85, 0.72, 0.63, ...],
    #   "precision": [...],
    #   "recall": [...]
    # }

    # File storage
    file_path = Column(String(500), nullable=True)  # Path to model weights file

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Owner
    user_id = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<Model {self.id}: {self.name}>"
