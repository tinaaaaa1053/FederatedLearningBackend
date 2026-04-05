"""
Settings related schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ConnectionSettings(BaseModel):
    """Connection settings"""
    adminApiEndpoint: str = "http://localhost:8200"
    port: int = 8200
    protocol: str = "http"
    certificate: Optional[str] = None


class WorkspaceSettings(BaseModel):
    """Workspace settings"""
    secureWorkspacePath: str = "/opt/fedlbe/secure_workspace"
    pocWorkspacePath: str = "/opt/fedlbe/poc_workspace"
    deploymentMode: str = "poc"  # production, poc


class SecuritySettings(BaseModel):
    """Security settings"""
    enableSecureComm: bool = True
    enableSecureAgg: bool = True
    enableDiffPrivacy: bool = False
    noiseLevel: float = 0.5
    clippingNorm: float = 1.0


class UserInfo(BaseModel):
    """User info for settings"""
    id: str
    username: str
    role: str
    status: str
    email: Optional[str] = None
    fullName: Optional[str] = None


class SettingsResponse(BaseModel):
    """Full settings response"""
    connection: ConnectionSettings
    workspace: WorkspaceSettings
    security: SecuritySettings
    users: List[UserInfo] = []


class SettingsSave(BaseModel):
    """Settings save request"""
    connection: Optional[ConnectionSettings] = None
    workspace: Optional[WorkspaceSettings] = None
    security: Optional[SecuritySettings] = None


class TestConnectionRequest(BaseModel):
    """Test connection request"""
    adminApiEndpoint: str
    port: int
    protocol: str


class TestConnectionResponse(BaseModel):
    """Test connection response"""
    status: str
    latency: Optional[float] = None
    version: Optional[str] = None
    error: Optional[str] = None


class UserCreate(BaseModel):
    """User creation request"""
    username: str
    password: str
    email: Optional[str] = None
    fullName: Optional[str] = None
    role: str = "viewer"


class UserUpdate(BaseModel):
    """User update request"""
    email: Optional[str] = None
    fullName: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
