"""
User schemas for Supabase integration
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr

from src.schemas.base import BaseSchema, TimestampSchema
from src.core.constants import SubscriptionTier


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    subscription_tier: str = Field(default=SubscriptionTier.FREE_BYOK.value)


class UserCreate(UserBase):
    """Schema for creating a user"""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    subscription_tier: Optional[str] = None


class User(UserBase):
    """Complete user schema with all fields"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class UserAPIKeyBase(BaseModel):
    """Base API key schema"""
    provider: str = Field(..., description="LLM provider (e.g., 'openai', 'anthropic')")
    encrypted_api_key: str
    provider_metadata: Optional[Dict[str, Any]] = None
    validation_status: str = Field(default="pending", description="pending, valid, invalid")
    last_validated_at: Optional[datetime] = None


class UserAPIKeyCreate(UserAPIKeyBase):
    """Schema for creating an API key"""
    user_id: UUID


class UserAPIKeyUpdate(BaseModel):
    """Schema for updating an API key"""
    encrypted_api_key: Optional[str] = None
    provider_metadata: Optional[Dict[str, Any]] = None
    validation_status: Optional[str] = None
    last_validated_at: Optional[datetime] = None


class UserAPIKey(UserAPIKeyBase):
    """Complete API key schema with all fields"""
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


# API request/response schemas
class APIKeyRequest(BaseModel):
    """Request schema for storing API keys"""
    api_key: str = Field(..., description="Raw API key from the provider")
    validate_key: bool = Field(default=True, description="Whether to validate the key")


class APIKeyResponse(BaseModel):
    """Response schema for API key operations"""
    provider: str
    validation_status: str
    last_validated_at: Optional[datetime] = None
    provider_metadata: Optional[Dict[str, Any]] = None
    message: str
