# backend/src/api/v1/endpoints/llm.py
"""
Endpoints for LLM configurations and capabilities
"""
from fastapi import APIRouter
from typing import Dict, List

# Import your structured catalog data and Pydantic schemas for the API response
from src.services.llm.llm_catalog import AI_MODEL_FAMILIES, LLM_PROVIDERS
from src.schemas.llm import ( # NEW: Updated schemas
    AIModelFamilySchema,
    LLMProviderSchema,
    HostedModelInstanceSchema
)


router = APIRouter()

@router.get(
    "/families",
    response_model=List[AIModelFamilySchema],
    summary="Get all abstract AI model families and their capabilities",
    description="Returns a list of all defined AI model families (e.g., GPT-4o, Claude 3 Haiku) "
                "along with their inherent capabilities (e.g., Thinking, Vision), independent of specific providers."
)
async def get_all_ai_model_families_api() -> List[AIModelFamilySchema]:
    """
    Returns the comprehensive list of all AI model families.
    """
    return AI_MODEL_FAMILIES

@router.get(
    "/providers",
    response_model=List[LLMProviderSchema],
    summary="Get all LLM providers and their specific hosted model instances",
    description="Returns a list of all configured LLM providers, including details "
                "about the exact model instances they host (e.g., 'gpt-4o' via OpenAI) "
                "with associated metadata like pricing hints."
)
async def get_all_llm_providers_api() -> List[LLMProviderSchema]:
    """
    Returns a list of all configured LLM providers with their hosted model instances.
    """
    return LLM_PROVIDERS

@router.get(
    "/providers/{provider_id}/models",
    response_model=List[HostedModelInstanceSchema],
    summary="Get hosted model instances for a specific LLM provider",
    description="Returns a list of all concrete model instances (e.g., 'gpt-4o') "
                "offered by a given LLM provider, including their specific names and metadata."
)
async def get_hosted_models_by_provider_id(provider_id: str) -> List[HostedModelInstanceSchema]:
    """
    Returns a list of hosted model instances for a specified provider.
    """
    from src.services.llm.llm_catalog import get_hosted_models_for_provider # Local import to avoid circularity
    return get_hosted_models_for_provider(provider_id)