# backend/src/database/sqlalchemy/models/user.py
"""
SQLAlchemy models for User and UserAPIKey
"""
from datetime import datetime, UTC
from typing import Optional, Dict, Any
import uuid

from sqlalchemy import String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, TABLE_PREFIX


class User(Base):
    """SQLAlchemy User model for backend user data storage"""
    __tablename__ = f"{TABLE_PREFIX}users"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identity
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    # Profile
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata from Supabase
    user_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))
    
    # Indexes
    __table_args__ = (
        Index(f"ix_{TABLE_PREFIX}users_email", "email"),
    )
    
    # Relationships
    api_keys: Mapped[list["UserAPIKey"]] = relationship("UserAPIKey", back_populates="user", cascade="all, delete-orphan")


class UserAPIKey(Base):
    """SQLAlchemy UserAPIKey model for encrypted API key storage"""
    __tablename__ = f"{TABLE_PREFIX}user_api_keys"
    
    # Composite primary key (user_id + provider)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey(f"{TABLE_PREFIX}users.id"), primary_key=True)
    provider: Mapped[str] = mapped_column(String(50), primary_key=True)  # PROVIDER_ID
    
    # Encrypted API key
    encrypted_api_key: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Validation
    validation_status: Mapped[str] = mapped_column(String(20), nullable=False, default="unknown")
    last_validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Provider metadata
    provider_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))
    
    # Indexes
    __table_args__ = (
        Index(f"ix_{TABLE_PREFIX}user_api_keys_user_id", "user_id"),
        Index(f"ix_{TABLE_PREFIX}user_api_keys_provider", "provider"),
        Index(f"ix_{TABLE_PREFIX}user_api_keys_validation_status", "validation_status"),
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="api_keys")