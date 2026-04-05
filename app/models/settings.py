"""
Settings database model
"""
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Settings(Base):
    __tablename__ = "fl_settings"

    id = Column(String(20), primary_key=True, default=lambda: str(uuid.uuid4())[:8])

    # Connection settings (JSON)
    connection = Column(JSON, default=dict)
    # {
    #   "adminApiEndpoint": "https://nvflare-api.example.com",
    #   "port": 8443,
    #   "protocol": "https",
    #   "certificate": null
    # }

    # Workspace settings (JSON)
    workspace = Column(JSON, default=dict)
    # {
    #   "secureWorkspacePath": "/opt/nvflare/secure_workspace",
    #   "pocWorkspacePath": "/opt/nvflare/poc_workspace",
    #   "deploymentMode": "production"
    # }

    # Security settings (JSON)
    security = Column(JSON, default=dict)
    # {
    #   "enableSecureComm": true,
    #   "enableSecureAgg": true,
    #   "enableDiffPrivacy": true,
    #   "noiseLevel": 0.5,
    #   "clippingNorm": 1.0
    # }

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Settings {self.id}>"
