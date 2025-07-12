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
    chunk_type: ChunkType = Field(alias="chunkType")
    usage: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatCompletionStreamChunk(BaseSchema):
    """Response chunk for streaming LLM chat completion"""
    model_config = {"populate_by_name": True}
    
    content: str
    model: str
    chunk_type: ChunkType = Field(alias="chunkType") 
    is_final: bool = Field(default=False, alias="isFinal")
    usage: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class APIKeyValidationResponse(BaseSchema):
    """Response for API key validation"""
    model_config = {"populate_by_name": True}
    
    provider: PROVIDER_ID
    is_valid: bool = Field(alias="isValid")
    validation_status: str = Field(alias="validationStatus")  # 'valid' | 'invalid' | 'error'
    message: str
    tested_with_model: Optional[MODEL_NAME] = Field(default=None, alias="testedWithModel")
    error_details: Optional[str] = Field(default=None, alias="errorDetails")


class StoredAPIKeyResponse(BaseSchema):
    """Response for stored API key operations"""
    model_config = {"populate_by_name": True}
    
    provider: PROVIDER_ID
    validation_status: str = Field(alias="validationStatus")
    last_validated_at: Optional[datetime] = Field(default=None, alias="lastValidatedAt")
    provider_metadata: Optional[Dict[str, Any]] = Field(default=None, alias="providerMetadata")
    message: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")


class ModelCapabilityResponse(BaseSchema):
    """Model with its capabilities"""
    model_config = {"populate_by_name": True}
    
    model_name: MODEL_NAME = Field(alias="modelName")
    provider: PROVIDER_ID
    display_name: str = Field(alias="displayName")
    description: Optional[str] = None
    capabilities: List[LLMCapability] = Field(default_factory=list)
    
    # Model specifications
    input_token_limit: Optional[int] = Field(default=None, alias="inputTokenLimit")
    output_token_limit: Optional[int] = Field(default=None, alias="outputTokenLimit")
    default_temperature: float = Field(default=0.7, alias="defaultTemperature")
    
    # Thinking capabilities
    supports_thinking: bool = Field(default=False, alias="supportsThinking")
    thinking_budget_min: Optional[int] = Field(default=None, alias="thinkingBudgetMin")
    thinking_budget_max: Optional[int] = Field(default=None, alias="thinkingBudgetMax")
    
    # Cost information
    input_cost_per_million: Optional[float] = Field(default=None, alias="inputCostPerMillion")
    output_cost_per_million: Optional[float] = Field(default=None, alias="outputCostPerMillion")


class ProviderResponse(BaseSchema):
    """LLM provider information"""
    model_config = {"populate_by_name": True}
    
    provider_id: PROVIDER_ID = Field(alias="providerId")
    display_name: str = Field(alias="displayName")
    api_key_format_hint: Optional[str] = Field(default=None, alias="apiKeyFormatHint")
    default_model: Optional[MODEL_NAME] = Field(default=None, alias="defaultModel")
    models: List[ModelCapabilityResponse] = Field(default_factory=list)


class ListProvidersResponse(BaseSchema):
    """Response for listing LLM providers"""
    model_config = {"populate_by_name": True}
    
    providers: List[ProviderResponse] = Field(default_factory=list)
    total_providers: int = Field(alias="totalProviders")
    total_models: int = Field(alias="totalModels")


class ListModelsResponse(BaseSchema):
    """Response for listing LLM models"""
    model_config = {"populate_by_name": True}
    
    models: List[ModelCapabilityResponse] = Field(default_factory=list)
    total_models: int = Field(alias="totalModels")
    provider_filter: Optional[PROVIDER_ID] = Field(default=None, alias="providerFilter")


class DeleteAPIKeyResponse(BaseSchema):
    """Response for deleting an API key"""
    model_config = {"populate_by_name": True}
    
    provider: PROVIDER_ID
    deleted: bool
    message: str


class ListUserAPIKeysResponse(BaseSchema):
    """Response for listing user's stored API keys"""
    model_config = {"populate_by_name": True}
    
    api_keys: List[StoredAPIKeyResponse] = Field(default_factory=list, alias="apiKeys")
    total_keys: int = Field(alias="totalKeys")


class LLMUsageStatsResponse(BaseSchema):
    """Response for LLM usage statistics"""
    model_config = {"populate_by_name": True}
    
    total_requests: int = Field(alias="totalRequests")
    total_tokens_used: int = Field(alias="totalTokensUsed")
    tokens_by_provider: Dict[str, int] = Field(default_factory=dict, alias="tokensByProvider")
    requests_by_model: Dict[str, int] = Field(default_factory=dict, alias="requestsByModel")
    cost_estimate: Optional[float] = Field(default=None, alias="costEstimate")
    period_start: datetime = Field(alias="periodStart")
    period_end: datetime = Field(alias="periodEnd")