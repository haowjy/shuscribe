"""
Request schemas for LLM API endpoints
"""
from typing import List, Optional, Dict, Any, Type
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema
from src.core.constants import PROVIDER_ID, MODEL_NAME
from src.schemas.llm.models import LLMMessage, ThinkingEffort


class ChatCompletionRequest(BaseSchema):
    """Request for LLM chat completion"""
    model_config = {"populate_by_name": True}
    
    provider: PROVIDER_ID
    model: MODEL_NAME
    messages: List[LLMMessage]
    
    # Optional parameters
    api_key: Optional[str] = None  # Temporary API key (not stored)
    temperature: float = Field(default=0.7)
    max_tokens: Optional[int] = None
    thinking: Optional[ThinkingEffort] = None
    stream: bool = Field(default=False)
    
    # Metadata
    trace_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ValidateAPIKeyRequest(BaseSchema):
    """Request to validate an API key without storing it"""
    model_config = {"populate_by_name": True}
    
    provider: PROVIDER_ID
    api_key: str
    test_model: Optional[MODEL_NAME] = None  # Model to test with


class StoreAPIKeyRequest(BaseSchema):
    """Request to store an encrypted API key for a user"""
    model_config = {"populate_by_name": True}
    
    provider: PROVIDER_ID
    api_key: str
    validate_key: bool = Field(default=True)
    provider_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DeleteAPIKeyRequest(BaseSchema):
    """Request to delete a stored API key"""
    model_config = {"populate_by_name": True}
    
    provider: PROVIDER_ID


class ListProvidersRequest(BaseSchema):
    """Request to list available LLM providers (usually no parameters)"""
    model_config = {"populate_by_name": True}
    
    include_models: bool = Field(default=True)


class ListModelsRequest(BaseSchema):
    """Request to list models for a specific provider"""
    model_config = {"populate_by_name": True}
    
    provider: Optional[PROVIDER_ID] = None  # If None, return models for all providers
    include_capabilities: bool = Field(default=True)