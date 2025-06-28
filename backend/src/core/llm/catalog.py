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
        default_model_name="gpt-4.1-mini",
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
        provider_id="anthropic",
        display_name="Anthropic",
        api_key_format_hint="sk-ant-api03-...",
        default_model_name="claude-3-5-haiku-latest",
        hosted_models=[
            HostedModelInstance(
                model_family_id="claude-opus-4", model_name="claude-opus-4-20250514", provider_id="anthropic",
                input_token_limit=200_000, output_token_limit=32_000,
                input_cost_per_million_tokens=15.00, output_cost_per_million_tokens=75.00,
            ),
            HostedModelInstance(
                model_family_id="claude-sonnet-4", model_name="claude-sonnet-4-20250514", provider_id="anthropic",
                input_token_limit=200_000, output_token_limit=64_000,
                input_cost_per_million_tokens=3.00, output_cost_per_million_tokens=15.00,
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
            ),
            HostedModelInstance(
                model_family_id="gemini-2.5-pro", model_name="gemini-2.5-pro-preview-05-06", provider_id="google",
                input_token_limit=1_048_576, output_token_limit=65_536,
                input_cost_per_million_tokens=2.50, output_cost_per_million_tokens=15.00,
            ),
            HostedModelInstance(
                model_family_id="gemini-2.5-flash", model_name="gemini-2.5-flash", provider_id="google",
                input_token_limit=1_048_576, output_token_limit=64_000,
                input_cost_per_million_tokens=0.30, output_cost_per_million_tokens=2.50,
            ),
            HostedModelInstance(
                model_family_id="gemini-2.5-flash-lite", model_name="gemini-2.5-flash-lite-preview-06-17", provider_id="google",
                input_token_limit=1_048_576, output_token_limit=65_536,
                input_cost_per_million_tokens=0.08, output_cost_per_million_tokens=0.40,
            ),
            HostedModelInstance(
                model_family_id="gemini-2.0-flash", model_name="gemini-2.0-flash-001", provider_id="google",
                input_token_limit=1_048_576, output_token_limit=8_192,
                input_cost_per_million_tokens=0.10, output_cost_per_million_tokens=0.40,
            ),
            # Add other hosted models for Google
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

def get_default_test_model_name_for_provider(provider_id: str) -> Optional[str]:
    """
    Gets a default model name for a provider, which can be used for API key validation.
    Prefers the cheapest and fastest models.
    """
    provider = _providers_by_id.get(provider_id)
    return provider.default_model_name if provider else None 