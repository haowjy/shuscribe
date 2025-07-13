"""
Response schemas for LLM API endpoints
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema
from src.core.constants import PROVIDER_ID, MODEL_NAME
from src.schemas.llm.models import ChunkType
from src.schemas.llm.config import LLMCapability, HostedModelInstance, LLMProvider


class ChatCompletionResponse(BaseSchema):
    """Response for LLM chat completion (non-streaming)"""
    model_config = {"populate_by_name": True}
    
    content: str
    model: str
    chunk_type: ChunkType
    usage: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatCompletionStreamChunk(BaseSchema):
    """Response chunk for streaming LLM chat completion"""
    model_config = {"populate_by_name": True}
    
    content: str
    model: str
    chunk_type: ChunkType
    is_final: bool = Field(default=False)
    usage: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class APIKeyValidationResponse(BaseSchema):
    """Response for API key validation"""
    model_config = {"populate_by_name": True}
    
    provider: PROVIDER_ID
    is_valid: bool
    validation_status: str  # 'valid' | 'invalid' | 'error'
    message: str
    tested_with_model: Optional[MODEL_NAME] = None
    error_details: Optional[str] = None


class StoredAPIKeyResponse(BaseSchema):
    """Response for stored API key operations"""
    model_config = {"populate_by_name": True}
    
    provider: PROVIDER_ID
    validation_status: str
    last_validated_at: Optional[datetime] = None
    provider_metadata: Optional[Dict[str, Any]] = None
    message: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ModelCapabilityResponse(BaseSchema):
    """Model with its capabilities"""
    model_config = {"populate_by_name": True}
    
    model_name: MODEL_NAME
    provider: PROVIDER_ID
    display_name: str
    description: Optional[str] = None
    capabilities: List[LLMCapability] = Field(default_factory=list)
    
    # Model specifications
    input_token_limit: Optional[int] = None
    output_token_limit: Optional[int] = None
    default_temperature: float = Field(default=0.7)
    
    # Thinking capabilities
    supports_thinking: bool = Field(default=False)
    thinking_budget_min: Optional[int] = None
    thinking_budget_max: Optional[int] = None
    
    # Cost information
    input_cost_per_million: Optional[float] = None
    output_cost_per_million: Optional[float] = None


class ProviderResponse(BaseSchema):
    """LLM provider information"""
    model_config = {"populate_by_name": True}
    
    provider_id: PROVIDER_ID
    display_name: str
    api_key_format_hint: Optional[str] = None
    default_model: Optional[MODEL_NAME] = None
    models: List[ModelCapabilityResponse] = Field(default_factory=list)


class ListProvidersResponse(BaseSchema):
    """Response for listing LLM providers"""
    model_config = {"populate_by_name": True}
    
    providers: List[ProviderResponse] = Field(default_factory=list)
    total_providers: int
    total_models: int


class ListModelsResponse(BaseSchema):
    """Response for listing LLM models"""
    model_config = {"populate_by_name": True}
    
    models: List[ModelCapabilityResponse] = Field(default_factory=list)
    total_models: int
    provider_filter: Optional[PROVIDER_ID] = None


class DeleteAPIKeyResponse(BaseSchema):
    """Response for deleting an API key"""
    model_config = {"populate_by_name": True}
    
    provider: PROVIDER_ID
    deleted: bool
    message: str


class ListUserAPIKeysResponse(BaseSchema):
    """Response for listing user's stored API keys"""
    model_config = {"populate_by_name": True}
    
    api_keys: List[StoredAPIKeyResponse] = Field(default_factory=list)
    total_keys: int


class LLMUsageStatsResponse(BaseSchema):
    """Response for LLM usage statistics"""
    model_config = {"populate_by_name": True}
    
    total_requests: int
    total_tokens_used: int
    tokens_by_provider: Dict[str, int] = Field(default_factory=dict)
    requests_by_model: Dict[str, int]
    cost_estimate: Optional[float] = None
    period_start: datetime
    period_end: datetime