# backend/src/schemas/llm.py
"""
Pydantic schemas for LLM-related API responses (e.g., LLM catalog data).
"""
from typing import List, Optional, Dict, Any
from pydantic import Field

from src.schemas.base import BaseSchema # Assuming BaseSchema from src/schemas/base.py
from src.services.llm.base import ( # Import the underlying models
    LLMCapability,
    AIModelFamily,
    HostedModelInstance,
    LLMProvider
)


class AIModelFamilySchema(BaseSchema):
    """API Schema for an abstract AI model family."""
    id: str = Field(alias="family_id")
    display_name: str
    description: Optional[str] = None
    capabilities: List[LLMCapability]


class HostedModelInstanceSchema(BaseSchema):
    """API Schema for a specific hosted LLM model instance."""
    name: str = Field(alias="model_name")
    model_family_id: str
    provider_id: str
    default_temperature: float
    default_max_tokens: Optional[int] = None
    input_cost_per_million_tokens: Optional[float] = None
    output_cost_per_million_tokens: Optional[float] = None
    avg_latency_ms: Optional[int] = None
    custom_properties: Dict[str, Any] = {}


class LLMProviderSchema(BaseSchema):
    """API Schema for an LLM provider, including its hosted model instances."""
    id: str = Field(alias="provider_id")
    display_name: str
    api_key_format_hint: Optional[str] = None
    hosted_models: List[HostedModelInstanceSchema]