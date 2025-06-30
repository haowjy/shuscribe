"""
User Domain Models

Handles user profiles, authentication, and BYOK API key management.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class SubscriptionTier(str, Enum):
    """User subscription tiers"""
    LOCAL = "local"              # Desktop-only usage
    FREE_BYOK = "free_byok"      # Web free tier with BYOK
    PREMIUM = "premium"          # Premium features
    ENTERPRISE = "enterprise"    # Enterprise features


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    display_name: Optional[str] = None
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE_BYOK
    preferences: Dict[str, Any] = Field(default_factory=dict)


class UserCreate(UserBase):
    """Schema for creating new users"""
    # Inherits all fields from UserBase
    # For local usage, email can be optional/fake
    pass


class UserUpdate(BaseModel):
    """Schema for updating users (all fields optional)"""
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    subscription_tier: Optional[SubscriptionTier] = None
    preferences: Optional[Dict[str, Any]] = None


class User(UserBase):
    """Complete user model with all fields"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserAPIKeyCreate(BaseModel):
    """Schema for creating/updating API keys"""
    provider: str = Field(..., description="LLM provider (e.g., 'openai', 'anthropic')")
    api_key: str = Field(..., description="The actual API key")
    provider_metadata: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific settings")


class UserAPIKey(BaseModel):
    """User's API key for a specific LLM provider"""
    user_id: UUID
    provider: str
    encrypted_api_key: str = Field(..., description="Encrypted API key for storage")
    provider_metadata: Dict[str, Any] = Field(default_factory=dict)
    validation_status: str = Field(default="pending", description="pending, valid, invalid")
    last_validated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @property
    def composite_key(self) -> str:
        """Unique key combining user_id and provider"""
        return f"{self.user_id}::{self.provider}"
    
    model_config = ConfigDict(from_attributes=True) 