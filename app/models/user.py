"""
User database model
"""
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    RESEARCHER = "researcher"
    VIEWER = "viewer"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


def generate_user_id():
    """Generate user ID"""
    random_suffix = str(uuid.uuid4().int % 10000).zfill(4)
    return f"user-{random_suffix}"


class User(Base):
    __tablename__ = "fl_users"

    id = Column(String(20), primary_key=True, default=generate_user_id)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User {self.id}: {self.username} ({self.role})>"
