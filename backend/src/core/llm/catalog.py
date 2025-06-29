"""
Centralized, comprehensive catalog of abstract AI models, concrete hosted model instances,
and LLM providers. This acts as the single source of truth for LLM configurations.
"""
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# Import the new Pydantic models for LLM configuration
from src.schemas.llm.config import (
    AIModelFamily,
    HostedModelInstance,
    LLMProvider,
    LLMCapability,
)
# Import settings for configurable thinking budget percentages
from src.config import settings


# --- 1. Define AI Model Families (Abstract Models) ---
# These describe the general capabilities of a model, independent of who hosts it.
AI_MODEL_FAMILIES: List[AIModelFamily] = [
    # OPENAI
    AIModelFamily(
        family_id="gpt-4.1",
        display_name="GPT-4.1",
        # Flagship GPT model for complex tasks
        description="OpenAI's flagship model for complex tasks. It is well suited for problem solving across domains.",
        capabilities=[
            LLMCapability.SEARCH,
            LLMCapability.VISION,
            LLMCapability.TOOL_USE,
            LLMCapability.STRUCTURED_OUTPUT,
        ],
    ),
    AIModelFamily(
        family_id="gpt-4.1-mini",
        display_name="GPT-4.1 mini",
        description="Provides a balance between intelligence, speed, and cost that makes it an attractive model for many use cases.",
        capabilities=[
            LLMCapability.SEARCH,
            LLMCapability.VISION,
            LLMCapability.TOOL_USE,
            LLMCapability.STRUCTURED_OUTPUT,
        ],
    ),
    AIModelFamily(
        family_id="gpt-4.1-nano",
        display_name="GPT-4.1 nano",
        description="The fastest, most cost-effective GPT-4.1 model. It is well suited for quick tasks and low-latency applications.",
        capabilities=[
            LLMCapability.SEARCH,
            LLMCapability.VISION,
            LLMCapability.TOOL_USE,
            LLMCapability.STRUCTURED_OUTPUT,
        ],
    ),
    AIModelFamily(
        family_id="o3",
        display_name="o3",
        description="Well-rounded and powerful model across domains. It sets a new standard for math, science, coding, and visual reasoning tasks. It also excels at technical writing and instruction-following. Use it to think through multi-step problems that involve analysis across text, code, and images.",
        capabilities=[
            LLMCapability.REASONING,
            LLMCapability.VISION,
            LLMCapability.TOOL_USE,
            LLMCapability.STRUCTURED_OUTPUT,
        ],
    ),
    AIModelFamily(
        family_id="o4-mini",
        display_name="o4 mini",
        description="OpenAI's latest small reasoning model. It's optimized for fast, effective reasoning with exceptionally efficient performance in coding and visual tasks.",
        capabilities=[
            LLMCapability.REASONING,
            LLMCapability.VISION,
            LLMCapability.TOOL_USE,
            LLMCapability.STRUCTURED_OUTPUT,
        ],
    ),
    
    # ANTHROPIC
    AIModelFamily(
        family_id="claude-opus-4",
        display_name="Claude Opus 4",
        description="Anthropic's most capable model. Highest level of intelligence and capability.",
        capabilities=[
            LLMCapability.REASONING,
            LLMCapability.SEARCH,
            LLMCapability.VISION,
            LLMCapability.TOOL_USE,
        ],
    ),
    AIModelFamily(
        family_id="claude-sonnet-4",
        display_name="Claude Sonnet 4",
        description="High-performance model. High intelligence and balanced performance.",
        capabilities=[
            LLMCapability.REASONING,
            LLMCapability.SEARCH,
            LLMCapability.VISION,
            LLMCapability.TOOL_USE,
        ],
    ),
    AIModelFamily(
        family_id="claude-3-5-sonnet",
        display_name="Claude Sonnet 3.5",
        description="Anthropic's previous intelligent model. High level of intelligence and capability.",
        capabilities=[
            LLMCapability.SEARCH,
            LLMCapability.VISION,
            LLMCapability.TOOL_USE,
        ],
    ),
    AIModelFamily(
        family_id="claude-3-5-haiku",
        display_name="Claude Haiku 3.5",
        description="Anthropic's fastest model. Intelligence at blazing speeds.",
        capabilities=[
            LLMCapability.SEARCH,
            LLMCapability.VISION,
            LLMCapability.TOOL_USE,
        ],
    ),
    
    # GOOGLE
    AIModelFamily(
        family_id="gemini-2.0-flash",
        display_name="Gemini 2.0 Flash",
        description="Gemini 2.0 Flash is Google's experimental preview model with significant speed improvements, native image generation, controllable text-to-speech, and enhanced agentic capabilities. Features improved multimodal understanding, coding, and function calling.",
        capabilities=[
            LLMCapability.SEARCH,
            LLMCapability.VISION,
            LLMCapability.TOOL_USE,
            LLMCapability.STRUCTURED_OUTPUT,
        ],
    ),
    AIModelFamily(
        family_id="gemini-2.5-pro",
        display_name="Gemini 2.5 Pro",
        description="Gemini 2.5 Pro is designed to tackle increasingly complex problems.",
        capabilities=[
            LLMCapability.REASONING,
            LLMCapability.SEARCH,
            LLMCapability.VISION,
            LLMCapability.TOOL_USE,
            LLMCapability.STRUCTURED_OUTPUT,
        ],
    ),
    AIModelFamily(
        family_id="gemini-2.5-flash",
        display_name="Gemini 2.5 Flash",
        description="Gemini 2.5 Flash is a thinking model, designed to tackle increasingly complex problems.",
        capabilities=[
            LLMCapability.REASONING,
            LLMCapability.SEARCH,
            LLMCapability.VISION,
            LLMCapability.TOOL_USE,
            LLMCapability.STRUCTURED_OUTPUT,
        ],
    ),
    AIModelFamily(
        family_id="gemini-2.5-flash-lite",
        display_name="Gemini 2.5 Flash-Lite",
        description="Gemini 2.5 Flash Lite is Google's fastest model. It is currently in preview.",
        capabilities=[
            LLMCapability.REASONING,
            LLMCapability.SEARCH,
            LLMCapability.VISION,
            LLMCapability.TOOL_USE,
            LLMCapability.STRUCTURED_OUTPUT,
        ],
    ),
    # Add other model families (e.g., Mistral, Cohere, specialized models)
]


# --- 2. Define LLM Providers and their Hosted Instances ---
# These specify concrete model offerings by each provider, linking back to AIModelFamilies.
LLM_PROVIDERS: List[LLMProvider] = [
    LLMProvider(
        provider_id="openai",
        display_name="OpenAI",
        api_key_format_hint="sk-...",
        default_model_name="gpt-4.1-nano",
        hosted_models=[
            HostedModelInstance(
                model_family_id="gpt-4.1", model_name="gpt-4.1", provider_id="openai",
                input_token_limit=1_047_576, output_token_limit=32_768,
                input_cost_per_million_tokens=2.00, output_cost_per_million_tokens=8.00,
            ),
            HostedModelInstance(
                model_family_id="gpt-4.1-mini", model_name="gpt-4.1-mini", provider_id="openai",
                input_token_limit=1_047_576, output_token_limit=32_768,
                input_cost_per_million_tokens=0.40, output_cost_per_million_tokens=1.60,
            ),
            HostedModelInstance(
                model_family_id="gpt-4.1-nano", model_name="gpt-4.1-nano", provider_id="openai",
                input_token_limit=1_047_576, output_token_limit=32_768,
                input_cost_per_million_tokens=0.10, output_cost_per_million_tokens=0.40,
            ),
            HostedModelInstance(
                model_family_id="o3", model_name="o3", provider_id="openai",
                input_token_limit=200_000, output_token_limit=100_000,
                input_cost_per_million_tokens=2.00, output_cost_per_million_tokens=8.00,
            ),
            HostedModelInstance(
                model_family_id="o4-mini", model_name="o4-mini", provider_id="openai",
                input_token_limit=200_000, output_token_limit=100_000,
                input_cost_per_million_tokens=1.10, output_cost_per_million_tokens=4.40,
            ),
        ],
    ),
    LLMProvider(
        provider_id="google",
        display_name="Google",
        api_key_format_hint="AIza...",
        default_model_name="gemini-2.0-flash-001",
        hosted_models=[
            HostedModelInstance(
                model_family_id="gemini-2.5-pro", model_name="gemini-2.5-pro", provider_id="google",
                input_token_limit=1_048_576, output_token_limit=65_536,
                input_cost_per_million_tokens=2.50, output_cost_per_million_tokens=15.00,
                thinking_budget_min=128, thinking_budget_max=32768, thinking_budget_default=-1,
            ),
            HostedModelInstance(
                model_family_id="gemini-2.5-pro", model_name="gemini-2.5-pro-preview-05-06", provider_id="google",
                input_token_limit=1_048_576, output_token_limit=65_536,
                input_cost_per_million_tokens=2.50, output_cost_per_million_tokens=15.00,
                thinking_budget_min=128, thinking_budget_max=32768, thinking_budget_default=-1,
            ),
            HostedModelInstance(
                model_family_id="gemini-2.5-flash", model_name="gemini-2.5-flash", provider_id="google",
                input_token_limit=1_048_576, output_token_limit=64_000,
                input_cost_per_million_tokens=0.30, output_cost_per_million_tokens=2.50,
                thinking_budget_min=0, thinking_budget_max=24576, thinking_budget_default=-1,
            ),
            HostedModelInstance(
                model_family_id="gemini-2.5-flash-lite", model_name="gemini-2.5-flash-lite-preview-06-17", provider_id="google",
                input_token_limit=1_048_576, output_token_limit=65_536,
                input_cost_per_million_tokens=0.10, output_cost_per_million_tokens=0.40,
                thinking_budget_min=512, thinking_budget_max=24576, thinking_budget_default=0,
            ),
            HostedModelInstance(
                model_family_id="gemini-2.0-flash", model_name="gemini-2.0-flash-001", provider_id="google",
                input_token_limit=1_048_576, output_token_limit=8_192,
                input_cost_per_million_tokens=0.10, output_cost_per_million_tokens=0.40,
            ),
            # Add other hosted models for Google
        ],
    ),
    LLMProvider(
        provider_id="anthropic",
        display_name="Anthropic",
        api_key_format_hint="sk-ant-api03-...",
        default_model_name="claude-3-5-haiku-latest",
        hosted_models=[
            HostedModelInstance(
                model_family_id="claude-opus-4", model_name="claude-opus-4-20250514", provider_id="anthropic",
                input_token_limit=200_000, output_token_limit=32_000,
                input_cost_per_million_tokens=15.00, output_cost_per_million_tokens=75.00,
                # Claude Opus 4: Extended thinking with 1024 min, ~32k practical max
                thinking_budget_min=1024, thinking_budget_max=32000, thinking_budget_default=-1,
            ),
            HostedModelInstance(
                model_family_id="claude-sonnet-4", model_name="claude-sonnet-4-20250514", provider_id="anthropic",
                input_token_limit=200_000, output_token_limit=64_000,
                input_cost_per_million_tokens=3.00, output_cost_per_million_tokens=15.00,
                # Claude Sonnet 4: Extended thinking with 1024 min, ~32k practical max  
                thinking_budget_min=1024, thinking_budget_max=32000, thinking_budget_default=-1,
            ),
            HostedModelInstance(
                model_family_id="claude-3-5-sonnet", model_name="claude-3-5-sonnet-20241022", provider_id="anthropic",
                input_token_limit=200_000, output_token_limit=8192,
                input_cost_per_million_tokens=3.00, output_cost_per_million_tokens=15.00,
            ),
            HostedModelInstance(
                model_family_id="claude-3-5-haiku", model_name="claude-3-5-haiku-latest", provider_id="anthropic",
                input_token_limit=200_000, output_token_limit=8192,
                input_cost_per_million_tokens=0.08, output_cost_per_million_tokens=4.00,
            ),
        ],
    ),
    # Add other providers (e.g., Groq, Mistral, Cohere)
]


# --- 3. Utility Functions to Query the Catalog ---

# Pre-computed lookups for faster access
_model_families_by_id: Dict[str, AIModelFamily] = {
    family.family_id: family for family in AI_MODEL_FAMILIES
}
_providers_by_id: Dict[str, LLMProvider] = {
    provider.provider_id: provider for provider in LLM_PROVIDERS
}
_hosted_models_by_provider_and_name: Dict[Tuple[str, str], HostedModelInstance] = {
    (provider.provider_id, model.model_name): model
    for provider in LLM_PROVIDERS
    for model in provider.hosted_models
}
_hosted_models_by_family: Dict[str, List[HostedModelInstance]] = defaultdict(list)
for provider in LLM_PROVIDERS:
    for model in provider.hosted_models:
        _hosted_models_by_family[model.model_family_id].append(model)


def get_all_ai_model_families() -> List[AIModelFamily]:
    """Returns a list of all defined AI Model Families."""
    return AI_MODEL_FAMILIES

def get_all_llm_providers() -> List[LLMProvider]:
    """Returns a list of all defined LLM Providers."""
    return LLM_PROVIDERS

def get_hosted_models_for_provider(provider_id: str) -> List[HostedModelInstance]:
    """Returns all hosted model instances for a specific provider."""
    provider = _providers_by_id.get(provider_id)
    return provider.hosted_models if provider else []

def get_hosted_model_instance(provider_id: str, model_name: str) -> Optional[HostedModelInstance]:
    """Retrieves a specific hosted model instance by its provider and name."""
    return _hosted_models_by_provider_and_name.get((provider_id, model_name))

def get_model_family_by_id(model_family_id: str) -> Optional[AIModelFamily]:
    """Retrieves an AI Model Family by its unique ID."""
    return _model_families_by_id.get(model_family_id)

def get_capabilities_for_hosted_model(provider_id: str, model_name: str) -> List[LLMCapability]:
    """
    Retrieves the list of capabilities for a specific hosted model by looking up its family.
    """
    instance = get_hosted_model_instance(provider_id, model_name)
    if not instance:
        return []
    
    family = get_model_family_by_id(instance.model_family_id)
    return family.capabilities if family else []

def get_hosted_instances_for_family(model_family_id: str) -> List[HostedModelInstance]:
    """Returns all hosted model instances that belong to a specific AI Model Family."""
    return _hosted_models_by_family.get(model_family_id, [])

def get_default_test_model_name_for_provider(provider_id: str) -> str:
    """
    Gets a default model name for a provider, which can be used for API key validation.
    Prefers the cheapest and fastest models.
    """
    provider = _providers_by_id.get(provider_id)
    if not provider:
        raise ValueError(f"Provider {provider_id} not found in catalog")
    # else the first model in the provider's hosted models
    return provider.default_model_name if provider.default_model_name else provider.hosted_models[0].model_name


def get_thinking_budget_config(provider_id: str, model_name: str) -> Optional[Tuple[int, int, int]]:
    """
    Gets thinking budget configuration for a specific model.
    
    Note: This is for Google/Anthropic models that use token budgets. 
    OpenAI models use reasoning_effort (low/medium/high) instead.
    
    Args:
        provider_id: Provider ID (e.g., 'google', 'anthropic') 
        model_name: Model name (e.g., 'gemini-2.5-pro')
        
    Returns:
        Tuple of (min_budget, max_budget, default_budget) or None if model doesn't support thinking budgets
        default_budget meanings:
        - -1: Dynamic thinking (model decides)
        - 0: Thinking disabled by default
        - >0: Specific default token count
    """
    instance = get_hosted_model_instance(provider_id, model_name)
    if not instance or not all([
        instance.thinking_budget_min is not None,
        instance.thinking_budget_max is not None,
        instance.thinking_budget_default is not None
    ]):
        return None
    
    # These are guaranteed to be int after the None check above
    assert instance.thinking_budget_min is not None
    assert instance.thinking_budget_max is not None
    assert instance.thinking_budget_default is not None
    
    return (
        instance.thinking_budget_min, 
        instance.thinking_budget_max, 
        instance.thinking_budget_default
    )


def calculate_thinking_budget_tokens(
    provider_id: str, 
    model_name: str, 
    thinking_level: str
) -> Optional[int]:
    """
    Calculates thinking budget tokens based on model's range and thinking level.
    Uses configurable percentages from settings.
    
    Note: This is for Google/Anthropic models that use token budgets.
    OpenAI models use reasoning_effort parameter instead.
    
    Args:
        provider_id: Provider ID 
        model_name: Model name
        thinking_level: "low", "medium", or "high"
        
    Returns:
        Token count for the thinking budget, or None if model doesn't support thinking budgets
        
    Calculation:
        - low: THINKING_BUDGET_LOW_PERCENT of max budget (or min budget if calculated < min)
        - medium: THINKING_BUDGET_MEDIUM_PERCENT of max budget  
        - high: THINKING_BUDGET_HIGH_PERCENT of max budget
    """
    budget_config = get_thinking_budget_config(provider_id, model_name)
    if not budget_config:
        return None
    
    min_budget, max_budget, default_budget = budget_config
    
    # Calculate percentage-based budget using configurable values from settings
    if thinking_level == "low":
        calculated = int(max_budget * (settings.THINKING_BUDGET_LOW_PERCENT / 100))
    elif thinking_level == "medium":
        calculated = int(max_budget * (settings.THINKING_BUDGET_MEDIUM_PERCENT / 100))
    elif thinking_level == "high":
        calculated = int(max_budget * (settings.THINKING_BUDGET_HIGH_PERCENT / 100))
    else:
        raise ValueError(f"Invalid thinking level: {thinking_level}. Must be 'low', 'medium', or 'high'")
    
    # Ensure calculated value is within model's supported range
    return max(min_budget, min(calculated, max_budget))


def model_supports_thinking(provider_id: str, model_name: str) -> bool:
    """
    Checks if a model supports thinking/reasoning mode.
    
    Args:
        provider_id: Provider ID
        model_name: Model name
        
    Returns:
        True if model supports thinking mode, False otherwise
    """
    model_capabilities = get_capabilities_for_hosted_model(provider_id, model_name)
    return LLMCapability.REASONING in model_capabilities


def model_supports_temperature(provider_id: str, model_name: str, is_thinking: bool = False) -> bool:
    """
    Checks if a model supports custom temperature parameter.
    
    Args:
        provider_id: Provider ID (e.g., 'openai', 'anthropic', 'google')
        model_name: Model name
        is_thinking: Whether thinking/reasoning mode is enabled
        
    Returns:
        True if model supports custom temperature, False otherwise
    """
    # Get model capabilities to determine if it's a reasoning model
    model_capabilities = get_capabilities_for_hosted_model(provider_id, model_name)
    is_reasoning_model = LLMCapability.REASONING in model_capabilities
    
    # OpenAI reasoning models never support custom temperature
    if provider_id.lower() == "openai" and is_reasoning_model:
        return False
    
    # Anthropic reasoning models only support temperature when thinking is disabled
    if provider_id.lower() == "anthropic" and is_reasoning_model and is_thinking:
        return False
    
    # All other models support temperature
    return True


def get_temperature_restriction_message(provider_id: str, model_name: str, is_thinking: bool, temperature: float) -> Optional[str]:
    """
    Gets a warning message if temperature will be ignored for a model.
    
    Args:
        provider_id: Provider ID
        model_name: Model name  
        is_thinking: Whether thinking/reasoning mode is enabled
        temperature: Requested temperature value
        
    Returns:
        Warning message if temperature will be ignored, None if temperature is supported
    """
    if model_supports_temperature(provider_id, model_name, is_thinking):
        return None
    
    # Get model capabilities to provide specific messages
    model_capabilities = get_capabilities_for_hosted_model(provider_id, model_name)
    is_reasoning_model = LLMCapability.REASONING in model_capabilities
    
    if provider_id.lower() == "openai" and is_reasoning_model:
        if temperature != 1.0:
            return f"OpenAI reasoning model {model_name} always uses fixed temperature=1.0. Custom temperature={temperature} will be ignored."
    
    elif provider_id.lower() == "anthropic" and is_reasoning_model and is_thinking:
        if temperature != 1.0:
            return f"Anthropic reasoning model {model_name} doesn't support custom temperature in thinking mode. Temperature={temperature} will be ignored."
    
    return None


def should_use_completion_tokens_param(provider_id: str, model_name: str) -> bool:
    """
    Checks if a model should use max_completion_tokens instead of max_tokens.
    
    Args:
        provider_id: Provider ID
        model_name: Model name
        
    Returns:
        True if should use max_completion_tokens, False if should use max_tokens
    """
    # OpenAI reasoning models use max_completion_tokens
    model_capabilities = get_capabilities_for_hosted_model(provider_id, model_name)
    is_reasoning_model = LLMCapability.REASONING in model_capabilities
    
    return provider_id.lower() == "openai" and is_reasoning_model