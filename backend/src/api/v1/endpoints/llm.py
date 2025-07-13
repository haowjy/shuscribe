"""
LLM API endpoints for chat completions, provider management, and API key handling
"""
import logging
from typing import Dict, Any, AsyncIterator, Optional, cast
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse

from src.api.dependencies import require_auth, get_current_user_id
from src.core.constants import PROVIDER_ID
from src.database.factory import get_repositories
from src.schemas.llm.models import ChunkType, LLMResponse
from src.services.llm.llm_service import LLMService
from src.core.encryption import encrypt_api_key, decrypt_api_key
from src.schemas.base import ApiResponse
from src.schemas.requests.llm import (
    ChatCompletionRequest,
    ValidateAPIKeyRequest,
    StoreAPIKeyRequest,
    DeleteAPIKeyRequest,
    ListProvidersRequest,
    ListModelsRequest
)
from src.schemas.responses.llm import (
    ChatCompletionResponse,
    ChatCompletionStreamChunk,
    APIKeyValidationResponse,
    StoredAPIKeyResponse,
    ModelCapabilityResponse,
    ProviderResponse,
    ListProvidersResponse,
    ListModelsResponse,
    DeleteAPIKeyResponse,
    ListUserAPIKeysResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================

def _convert_model_to_response(model) -> ModelCapabilityResponse:
    """Convert a HostedModelInstance to ModelCapabilityResponse"""
    return ModelCapabilityResponse(
        modelName=model.model_name,
        provider=model.provider_id,
        displayName=model.model_name,  # Could be enhanced with better display names
        description=None,
        capabilities=LLMService.get_capabilities_for_hosted_model(model.provider_id, model.model_name),
        inputTokenLimit=model.input_token_limit,
        outputTokenLimit=model.output_token_limit,
        defaultTemperature=model.default_temperature,
        supportsThinking=model.thinking_budget_min is not None,
        thinkingBudgetMin=model.thinking_budget_min,
        thinkingBudgetMax=model.thinking_budget_max,
        inputCostPerMillion=model.input_cost_per_million_tokens,
        outputCostPerMillion=model.output_cost_per_million_tokens
    )


def _convert_provider_to_response(provider, include_models: bool = True) -> ProviderResponse:
    """Convert an LLMProvider to ProviderResponse"""
    models = []
    if include_models:
        hosted_models = LLMService.get_hosted_models_for_provider(provider.provider_id)
        models = [_convert_model_to_response(model) for model in hosted_models]
    
    return ProviderResponse(
        providerId=provider.provider_id,
        displayName=provider.display_name,
        apiKeyFormatHint=provider.api_key_format_hint,
        defaultModel=provider.default_model_name,
        models=models
    )


async def _stream_chat_completion(
    llm_service: LLMService,
    request: ChatCompletionRequest,
    user_id: str
) -> AsyncIterator[str]:
    """Stream chat completion responses as Server-Sent Events"""
    try:
        # Get the streaming response
        stream_response = await llm_service.chat_completion(
            provider=request.provider,
            model=request.model,
            messages=request.messages,
            user_id=UUID(user_id) if not request.api_key else None,
            api_key=request.api_key,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            thinking=request.thinking,
            trace_id=request.trace_id,
            metadata=request.metadata,
            stream=True
        )

        stream_response = cast(AsyncIterator[LLMResponse], stream_response)
        
        # Stream the responses
        async for chunk in stream_response:
            chunk_response = ChatCompletionStreamChunk(
                content=chunk.content,
                model=chunk.model,
                chunkType=chunk.chunk_type,
                isFinal=False,  # Will be set to True for the last chunk
                usage=chunk.usage,
                metadata=chunk.metadata or {}
            )
            
            # Send chunk data directly
            yield f"data: {chunk_response.model_dump_json()}\n\n"
        
        # Send final chunk
        final_chunk = ChatCompletionStreamChunk(
            content="",
            model=request.model,
            chunkType=ChunkType.CONTENT,
            isFinal=True,
            usage=None,
            metadata={"stream_complete": True}
        )
        yield f"data: {final_chunk.model_dump_json()}\n\n"
        
    except Exception as e:
        logger.error(f"Error in streaming chat completion: {e}")
        error_response = ApiResponse.create_error(
            error="Stream error",
            message=str(e),
            status=500
        )
        yield f"data: {error_response.model_dump_json()}\n\n"


# ============================================================================
# Chat Completion Endpoints
# ============================================================================

@router.post("/chat", response_model=ChatCompletionResponse)
async def chat_completion(
    request: ChatCompletionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate chat completion using LLM service
    
    Supports both temporary API keys (passed in request) and stored encrypted keys.
    """
    try:
        # Create LLM service with user repository access
        repos = get_repositories()
        llm_service = LLMService(user_repository=repos.user)
        
        # Handle streaming response
        if request.stream:
            return StreamingResponse(
                _stream_chat_completion(llm_service, request, user_id),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        
        # Handle non-streaming response
        response = await llm_service.chat_completion(
            provider=request.provider,
            model=request.model,
            messages=request.messages,
            user_id=UUID(user_id) if not request.api_key else None,
            api_key=request.api_key,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            thinking=request.thinking,
            trace_id=request.trace_id,
            metadata=request.metadata,
            stream=False
        )
        
        response = cast(LLMResponse, response)
        
        chat_response = ChatCompletionResponse(
            content=response.content,
            model=response.model,
            chunkType=response.chunk_type,
            usage=response.usage,
            metadata=response.metadata or {}
        )
        
        return chat_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat completion failed: {str(e)}"
        )


# ============================================================================
# API Key Management Endpoints
# ============================================================================

@router.post("/validate-key", response_model=APIKeyValidationResponse)
async def validate_api_key(
    request: ValidateAPIKeyRequest,
    user_id: str = Depends(get_current_user_id)
) -> APIKeyValidationResponse:
    """
    Validate an API key without storing it
    
    This endpoint tests the API key with a simple request to verify it works.
    """
    try:
        # Create LLM service
        llm_service = LLMService()
        
        # Use test model or get default for provider
        test_model = request.test_model or LLMService.get_default_test_model_name_for_provider(request.provider)
        
        # Test the API key with a simple request
        from src.schemas.llm.models import LLMMessage
        test_messages = [LLMMessage(role="user", content="Hello")]
        
        try:
            response = await llm_service.chat_completion(
                provider=request.provider,
                model=test_model,
                messages=test_messages,
                api_key=request.api_key,
                max_tokens=5,  # Minimal response to test quickly
                stream=False
            )
            
            validation_response = APIKeyValidationResponse(
                provider=request.provider,
                isValid=True,
                validationStatus="valid",
                message="API key is valid and working",
                testedWithModel=test_model
            )
            
        except Exception as validation_error:
            logger.warning(f"API key validation failed: {validation_error}")
            validation_response = APIKeyValidationResponse(
                provider=request.provider,
                isValid=False,
                validationStatus="invalid",
                message="API key validation failed",
                testedWithModel=test_model,
                errorDetails=str(validation_error)
            )
        
        return validation_response
        
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key validation failed"
        )


@router.post("/store-key", response_model=StoredAPIKeyResponse)
async def store_api_key(
    request: StoreAPIKeyRequest,
    user_id: str = Depends(get_current_user_id)
) -> StoredAPIKeyResponse:
    """
    Store an encrypted API key for the user
    
    The API key is encrypted before storage and can optionally be validated.
    """
    try:
        repos = get_repositories()
        
        validation_status = "unknown"
        if request.validate_key:
            # Validate the key before storing
            validation_request = ValidateAPIKeyRequest(
                provider=request.provider,
                apiKey=request.api_key
            )
            validation_result = await validate_api_key(validation_request, user_id)
            validation_status = validation_result.data.validation_status if validation_result.data else "unknown"
        
        # Encrypt the API key
        encrypted_key = encrypt_api_key(request.api_key)
        
        # Store in repository
        stored_key = await repos.user.store_api_key(
            user_id=user_id,
            provider=request.provider,
            encrypted_api_key=encrypted_key,
            validation_status=validation_status,
            provider_metadata=request.provider_metadata
        )
        
        key_response = StoredAPIKeyResponse(
            provider=stored_key.provider,
            validationStatus=stored_key.validation_status,
            lastValidatedAt=stored_key.last_validated_at,
            providerMetadata=stored_key.provider_metadata,
            message="API key stored successfully",
            createdAt=stored_key.created_at,
            updatedAt=stored_key.updated_at
        )
        
        return key_response
        
    except Exception as e:
        logger.error(f"Error storing API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store API key"
        )


@router.delete("/keys/{provider}", response_model=DeleteAPIKeyResponse)
async def delete_api_key(
    provider: PROVIDER_ID,
    user_id: str = Depends(get_current_user_id)
) -> DeleteAPIKeyResponse:
    """Delete a stored API key for the user"""
    try:
        repos = get_repositories()
        
        deleted = await repos.user.delete_api_key(user_id, provider)
        
        delete_response = DeleteAPIKeyResponse(
            provider=provider,
            deleted=deleted,
            message="API key deleted successfully" if deleted else "API key not found"
        )
        
        return delete_response
        
    except Exception as e:
        logger.error(f"Error deleting API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete API key"
        )


@router.get("/keys", response_model=ListUserAPIKeysResponse)
async def list_user_api_keys(
    user_id: str = Depends(get_current_user_id)
) -> ListUserAPIKeysResponse:
    """List all stored API keys for the user (without decrypting them)"""
    try:
        repos = get_repositories()
        
        api_keys = await repos.user.list_user_api_keys(user_id)
        
        key_responses = [
            StoredAPIKeyResponse(
                provider=key.provider,
                validationStatus=key.validation_status,
                lastValidatedAt=key.last_validated_at,
                providerMetadata=key.provider_metadata,
                message="",
                createdAt=key.created_at,
                updatedAt=key.updated_at
            )
            for key in api_keys
        ]
        
        list_response = ListUserAPIKeysResponse(
            apiKeys=key_responses,
            totalKeys=len(key_responses)
        )
        
        return list_response
        
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list API keys"
        )


# ============================================================================
# Provider and Model Discovery Endpoints
# ============================================================================

@router.get("/providers", response_model=ListProvidersResponse)
async def list_providers(
    include_models: bool = True,
    user_context: Dict[str, Any] = Depends(require_auth)
) -> ListProvidersResponse:
    """
    List all available LLM providers and their models
    
    This endpoint is authenticated to prevent abuse but doesn't require specific user data.
    """
    try:
        providers = LLMService.get_all_llm_providers()
        
        provider_responses = [
            _convert_provider_to_response(provider, include_models)
            for provider in providers
        ]
        
        total_models = sum(len(p.models) for p in provider_responses)
        
        list_response = ListProvidersResponse(
            providers=provider_responses,
            totalProviders=len(provider_responses),
            totalModels=total_models
        )
        
        return list_response
        
    except Exception as e:
        logger.error(f"Error listing providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list providers"
        )


@router.get("/models", response_model=ListModelsResponse)
async def list_models(
    provider: Optional[PROVIDER_ID] = None,
    include_capabilities: bool = True,
    user_context: Dict[str, Any] = Depends(require_auth)
) -> ListModelsResponse:
    """
    List available models, optionally filtered by provider
    
    This endpoint is authenticated to prevent abuse but doesn't require specific user data.
    """
    try:
        if provider:
            # Get models for specific provider
            hosted_models = LLMService.get_hosted_models_for_provider(provider)
            model_responses = [_convert_model_to_response(model) for model in hosted_models]
        else:
            # Get all models from all providers
            providers = LLMService.get_all_llm_providers()
            model_responses = []
            for llm_provider in providers:
                hosted_models = LLMService.get_hosted_models_for_provider(llm_provider.provider_id)
                model_responses.extend([_convert_model_to_response(model) for model in hosted_models])
        
        list_response = ListModelsResponse(
            models=model_responses,
            totalModels=len(model_responses),
            providerFilter=provider
        )
        
        return list_response
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list models"
        )