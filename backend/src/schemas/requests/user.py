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
    api_key: str = Field(..., description="Raw API key from the provider", alias="apiKey")
    validate_key: bool = Field(
        default=True, description="Whether to validate the key", alias="validateKey"
    )
    provider_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Provider-specific settings (model, max_tokens, etc.)",
        alias="providerMetadata"
    )


class APIKeyResponse(BaseModel):
    """Response schema for API key operations"""
    provider: str
    validation_status: str = Field(alias="validationStatus")
    last_validated_at: Optional[datetime] = Field(None, alias="lastValidatedAt")
    provider_metadata: Optional[Dict[str, Any]] = Field(None, alias="providerMetadata")
    message: str
