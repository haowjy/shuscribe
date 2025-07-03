"""
Pydantic models for LLM configuration, capabilities, and provider offerings.
"""
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.core.constants import MODEL_NAME, PROVIDER_ID


class LLMConfig(BaseModel):
    """Configuration for LLM requests (internal use by LLMService)"""
    provider: PROVIDER_ID  # The ID of the provider (e.g., 'openai', 'anthropic', 'groq')
    model: MODEL_NAME     # The exact model name used by that provider (e.g., 'gpt-4o', 'claude-3-haiku-20240307')
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    additional_params: Dict[str, Any] = Field(default_factory=dict)


class LLMCapability(str, Enum):
    """Enumeration of distinct LLM capabilities."""
    REASONING = "reasoning"       # Models capable of complex reasoning, CoT, planning
    SEARCH = "search"             # Models with built-in search/RAG abilities or strong web search query generation
    VISION = "vision"             # Models that can process image inputs
    TOOL_USE = "tool_use"         # Models capable of using external tools/functions (function calling)
    STRUCTURED_OUTPUT = "structured_output" # Models that can output structured data


class AIModelFamily(BaseModel):
    """Defines an abstract AI model type and its inherent capabilities, independent of provider."""
    family_id: str = Field(..., description="Unique identifier for the model family (e.g., 'gpt-4o', 'claude-3-haiku', 'llama-3-8b'). This is a conceptual ID.")
    display_name: str = Field(..., description="Human-readable name of the model family (e.g., 'GPT-4o', 'Llama 3 8B Instruct').")
    description: Optional[str] = Field(default=None, description="A brief description of the model family's general strengths and ideal use cases.")
    capabilities: List[LLMCapability] = Field(default_factory=list, description="List of core capabilities this model family possesses.")
    # Add other common parameters relevant to the abstract model, e.g., typical_context_window: int


class HostedModelInstance(BaseModel):
    """
    Represents a specific instance of an AI Model Family hosted by a particular provider.
    This is what your backend actually uses when making calls.
    """
    # The `name` is the exact string passed to the LLM API for this provider.
    model_name: MODEL_NAME = Field(..., description="The exact model string used by this provider for this instance (e.g., 'gpt-4o', 'claude-3-haiku-20240307', 'llama-3-8b-instruct').")
    
    # Reference to the abstract model family it belongs to
    model_family_id: str = Field(..., description="The ID of the abstract AI Model Family this instance belongs to (e.g., 'gpt-4o').")
    
    # Reference to the provider hosting this instance
    provider_id: PROVIDER_ID = Field(..., description="The ID of the provider hosting this instance (e.g., 'openai', 'anthropic', 'groq').")
    
    # Provider-specific metadata for this instance (defaults can be overridden from family/general)
    default_temperature: float = Field(default=0.7, description="Default temperature for this specific hosted model instance.")
    default_max_tokens: Optional[int] = Field(default=None, description="Default max tokens to generate for this instance.")
    
    input_token_limit: Optional[int] = Field(default=None, description="The maximum number of input tokens for this instance.")
    output_token_limit: Optional[int] = Field(default=None, description="The maximum number of output tokens for this instance.")
    
    # Thinking/Reasoning budget configuration for models that support it
    thinking_budget_min: Optional[int] = Field(default=None, description="Minimum thinking budget tokens for reasoning models (None if not supported).")
    thinking_budget_max: Optional[int] = Field(default=None, description="Maximum thinking budget tokens for reasoning models (None if not supported).")
    thinking_budget_default: Optional[int] = Field(default=None, description="Default thinking budget (-1 for dynamic, 0 for disabled, specific count, or None if not supported).")
    
    # Optional: Pricing information (can be useful for frontend or internal cost tracking)
    input_cost_per_million_tokens: Optional[float] = Field(default=None, description="Estimated input cost in USD per 1M tokens for this instance.")
    output_cost_per_million_tokens: Optional[float] = Field(default=None, description="Estimated output cost in USD per 1M tokens for this instance.")
    
    # Optional: Expected latency / throughput or other provider-specific custom properties
    avg_latency_ms: Optional[int] = Field(default=None, description="Average latency in milliseconds for this instance.")
    custom_properties: Dict[str, Any] = Field(default_factory=dict, description="Additional provider-specific properties or metadata.")


class LLMProvider(BaseModel):
    """Defines a specific LLM provider, and lists the hosted model instances it offers."""
    provider_id: PROVIDER_ID = Field(..., description="Unique identifier for the provider (e.g., 'openai', 'anthropic', 'google', 'groq').")
    display_name: str = Field(..., description="Human-readable name of the provider.")
    api_key_format_hint: Optional[str] = Field(default=None, description="Hint for the format of the API key for this provider, useful for UI validation.")
    
    # List of hosted model instances this provider offers.
    # These instances are concrete offerings of abstract AIModelFamilies.
    default_model_name: Optional[MODEL_NAME] = Field(default=None, description="The default model name to use for this provider.")
    hosted_models: List[HostedModelInstance] = Field(default_factory=list, description="List of specific model instances hosted by this provider.") 