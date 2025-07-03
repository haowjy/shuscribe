# backend/src/api/v1/endpoints/llm.py
"""
Endpoints for LLM configurations and capabilities
"""
from fastapi import APIRouter, Query
from typing import List, Optional

# Import your structured catalog data and Pydantic schemas for the API response
from src.utils.catalog import AI_MODEL_FAMILIES, LLM_PROVIDERS
from src.schemas.llm.config import ( # NEW: Updated schemas
    AIModelFamily,
    LLMProvider,
    HostedModelInstance
)


# /api/v1/llm/
router = APIRouter()

@router.get(
    "/families",
    response_model=List[AIModelFamily],
    summary="Get all abstract AI model families and their capabilities",
    description="Returns a list of all defined AI model families (e.g., GPT-4o, Claude 3 Haiku) "
                "along with their inherent capabilities (e.g., Thinking, Vision), independent of specific providers."
)
async def get_all_ai_model_families_api() -> List[AIModelFamily]:
    """
    Returns the comprehensive list of all AI model families.
    """
    return AI_MODEL_FAMILIES

@router.get(
    "/providers",
    response_model=List[LLMProvider],
    summary="Get all LLM providers and their specific hosted model instances",
    description="Returns a list of all configured LLM providers, including details "
                "about the exact model instances they host (e.g., 'gpt-4o' via OpenAI) "
                "with associated metadata like pricing hints."
)
async def get_all_llm_providers_api() -> List[LLMProvider]:
    """
    Returns a list of all configured LLM providers with their hosted model instances.
    """
    return LLM_PROVIDERS

@router.get(
    "/models",
    response_model=List[HostedModelInstance],
    summary="Get all hosted model instances",
    description="Returns a flat list of all concrete model instances (e.g., 'gpt-4o') "
                "from all providers. Can be filtered by `provider_id`.",
)
async def get_all_hosted_models(
    provider_id: Optional[str] = Query(
        None, description="Filter models by a specific provider ID (e.g., 'openai')."
    ),
) -> List[HostedModelInstance]:
    """
    Returns a list of all hosted model instances across all providers.
    Can be filtered by provider.
    """
    all_models = [
        model for provider in LLM_PROVIDERS for model in provider.hosted_models
    ]

    if provider_id:
        return [model for model in all_models if model.provider_id == provider_id]

    return all_models