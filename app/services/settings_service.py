"""
Settings Service
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import SessionLocal
from app.models.settings import Settings
from app.models.user import User, UserRole, UserStatus
from app.schemas.settings import (
    SettingsResponse, SettingsSave, ConnectionSettings,
    WorkspaceSettings, SecuritySettings, TestConnectionRequest,
    TestConnectionResponse, UserCreate, UserUpdate
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SettingsService:
    """Service for settings management"""

    def __init__(self):
        self.db: Session = SessionLocal()

    async def get_settings(self) -> SettingsResponse:
        """Get all settings"""
        settings = self.db.query(Settings).first()

        if not settings:
            # Create default settings
            settings = Settings(
                connection={
                    "adminApiEndpoint": "http://localhost:8200",
                    "port": 8200,
                    "protocol": "http",
                    "certificate": None
                },
                workspace={
                    "secureWorkspacePath": "/opt/fedlbe/secure_workspace",
                    "pocWorkspacePath": "/opt/fedlbe/poc_workspace",
                    "deploymentMode": "poc"
                },
                security={
                    "enableSecureComm": True,
                    "enableSecureAgg": True,
                    "enableDiffPrivacy": False,
                    "noiseLevel": 0.5,
                    "clippingNorm": 1.0
                }
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)

        users = self.db.query(User).all()

        return SettingsResponse(
            connection=ConnectionSettings(**settings.connection),
            workspace=WorkspaceSettings(**settings.workspace),
            security=SecuritySettings(**settings.security),
            users=[
                {
                    "id": u.id,
                    "username": u.username,
                    "role": u.role.value,
                    "status": u.status.value,
                    "email": u.email,
                    "fullName": u.full_name
                }
                for u in users
            ]
        )

    async def save_settings(self, settings_data: SettingsSave) -> None:
        """Save settings"""
        settings = self.db.query(Settings).first()

        if not settings:
            settings = Settings()
            self.db.add(settings)

        if settings_data.connection:
            settings.connection = settings_data.connection.model_dump()
        if settings_data.workspace:
            settings.workspace = settings_data.workspace.model_dump()
        if settings_data.security:
            settings.security = settings_data.security.model_dump()

        self.db.commit()

    async def test_connection(self, request: TestConnectionRequest) -> TestConnectionResponse:
        """Test backend connection"""
        import httpx

        url = f"{request.protocol}://{request.adminApiEndpoint}:{request.port}"

        try:
            start_time = datetime.utcnow()
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
            end_time = datetime.utcnow()

            latency = (end_time - start_time).total_seconds() * 1000

            return TestConnectionResponse(
                status="connected" if response.status_code == 200 else "error",
                latency=latency,
                version="1.0.0"  # TODO: Get actual version from FedLBE
            )
        except Exception as e:
            return TestConnectionResponse(
                status="failed",
                error=str(e)
            )

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = pwd_context.hash(user_data.password)

        user = User(
            username=user_data.username,
            password_hash=hashed_password,
            email=user_data.email,
            full_name=user_data.fullName,
            role=UserRole(user_data.role.lower()),
            status=UserStatus.ACTIVE
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "role" and value:
                user.role = UserRole(value.lower())
            elif field == "status" and value:
                user.status = UserStatus(value.lower())
            elif hasattr(user, field):
                setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)

        return user

    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    async def reset_settings(self) -> None:
        """Reset settings to defaults"""
        settings = self.db.query(Settings).first()

        if settings:
            settings.connection = {
                "adminApiEndpoint": "http://localhost:8200",
                "port": 8200,
                "protocol": "http",
                "certificate": None
            }
            settings.workspace = {
                "secureWorkspacePath": "/opt/fedlbe/secure_workspace",
                "pocWorkspacePath": "/opt/fedlbe/poc_workspace",
                "deploymentMode": "poc"
            }
            settings.security = {
                "enableSecureComm": True,
                "enableSecureAgg": True,
                "enableDiffPrivacy": False,
                "noiseLevel": 0.5,
                "clippingNorm": 1.0
            }
            self.db.commit()
