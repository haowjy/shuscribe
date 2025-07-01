"""
HTTP API Schemas for User Endpoints

This file contains only HTTP request/response schemas for user-related API endpoints.
Domain models are in src.database.models.user
"""
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


# API request/response schemas
class APIKeyRequest(BaseModel):
    """Request schema for storing API keys"""
    api_key: str = Field(..., description="Raw API key from the provider")
    validate_key: bool = Field(
        default=True, description="Whether to validate the key"
    )
    provider_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Provider-specific settings (model, max_tokens, etc.)"
    )


class APIKeyResponse(BaseModel):
    """Response schema for API key operations"""
    provider: str
    validation_status: str
    last_validated_at: Optional[datetime] = None
    provider_metadata: Optional[Dict[str, Any]] = None
    message: str
