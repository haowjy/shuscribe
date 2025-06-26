# backend/src/database/models.py
"""
SQLAlchemy database models
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, String, Text, Boolean, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from src.database.base import Base # Import our new Base
from src.core.constants import ProcessingStatus, SubscriptionTier # Use our enums


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


class User(Base, TimestampMixin):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    subscription_tier = Column(String, default=SubscriptionTier.FREE_BYOK.value, nullable=False)
    
    # Relationships
    stories = relationship("Story", back_populates="owner")
    progress = relationship("UserProgress", back_populates="user")
    api_keys = relationship("UserAPIKey", back_populates="user") # One user can have many keys for different providers


class UserAPIKey(Base, TimestampMixin):
    """
    User API keys for BYOK model.
    Uses a composite primary key to allow one key per provider per user.
    """
    __tablename__ = "user_api_keys"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    provider = Column(String, primary_key=True, nullable=False)  # e.g., 'openai', 'anthropic'
    encrypted_api_key = Column(Text, nullable=False)
    
    # Optional: store provider-specific metadata (e.g., limits, available models)
    provider_metadata = Column(JSON, nullable=True)
    
    # Validation status and timestamp
    last_validated_at = Column(DateTime(timezone=True), nullable=True)
    validation_status = Column(String, default="pending", nullable=False) # pending, valid, invalid
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

