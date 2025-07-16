"""
LLM API endpoints for chat completions, provider management, and API key handling
"""
import logging
from typing import Dict, Any, AsyncIterator, Optional, cast
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse

from src.api.dependencies import require_auth, get_current_user_id
from src.core.constants import PROVIDER_ID
from src.database.factory import get_repositories
from src.schemas.llm.models import ChunkType, LLMResponse, LLMMessage
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
        model_name=model.model_name,
        provider=model.provider_id,
        display_name=model.model_name,  # Could be enhanced with better display names
        description=None,
        capabilities=LLMService.get_capabilities_for_hosted_model(model.provider_id, model.model_name),
        input_token_limit=model.input_token_limit,
        output_token_limit=model.output_token_limit,
        default_temperature=model.default_temperature,
        supports_thinking=model.thinking_budget_min is not None,
        thinking_budget_min=model.thinking_budget_min,
        thinking_budget_max=model.thinking_budget_max,
        input_cost_per_million=model.input_cost_per_million_tokens,
        output_cost_per_million=model.output_cost_per_million_tokens
    )


def _convert_provider_to_response(provider, include_models: bool = True) -> ProviderResponse:
    """Convert an LLMProvider to ProviderResponse"""
    models = []
    if include_models:
        hosted_models = LLMService.get_hosted_models_for_provider(provider.provider_id)
        models = [_convert_model_to_response(model) for model in hosted_models]
    
    return ProviderResponse(
        provider_id=provider.provider_id,
        display_name=provider.display_name,
        api_key_format_hint=provider.api_key_format_hint,
        default_model=provider.default_model_name,
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
                chunk_type=chunk.chunk_type,
                is_final=False,  # Will be set to True for the last chunk
                usage=chunk.usage,
                metadata=chunk.metadata or {}
            )
            
            # Send chunk data directly
            yield f"data: {chunk_response.model_dump_json()}\n\n"
        
        # Send final chunk
        final_chunk = ChatCompletionStreamChunk(
            content="",
            model=request.model,
            chunk_type=ChunkType.CONTENT,
            is_final=True,
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
            chunk_type=response.chunk_type,
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
                is_valid=True,
                validation_status="valid",
                message="API key is valid and working",
                tested_with_model=test_model
            )
            return validation_response
            
        except Exception as e:
            logger.warning(f"API key validation failed for provider {request.provider}: {e}")
            validation_response = APIKeyValidationResponse(
                provider=request.provider,
                is_valid=False,
                validation_status="invalid",
                message=f"API key validation failed: {str(e)}",
                tested_with_model=test_model,
                error_details=str(e)
            )
            return validation_response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during key validation"
        )


@router.post("/store-key", response_model=StoredAPIKeyResponse)
async def store_api_key(
    request: StoreAPIKeyRequest,
    user_id: str = Depends(get_current_user_id)
) -> StoredAPIKeyResponse:
    """
    Store an encrypted API key for a user
    """
    try:
        repos = get_repositories()
        llm_service = LLMService(user_repository=repos.user)
        
        # Optional: Validate the key before storing
        if request.validate_key:
            test_model = LLMService.get_default_test_model_name_for_provider(request.provider)
            try:
                await llm_service.chat_completion(
                    provider=request.provider,
                    model=test_model,
                    messages=[LLMMessage(role="user", content="Hello")],
                    api_key=request.api_key,
                    max_tokens=5,
                    stream=False
                )
                validation_status = "valid"
                message = "API key stored and validated successfully"
            except Exception as e:
                validation_status = "invalid"
                message = f"API key stored but validation failed: {str(e)}"
                logger.warning(f"Stored API key validation failed for user {user_id}, provider {request.provider}: {e}")
        else:
            validation_status = "not_validated"
            message = "API key stored without validation"
            
        # Encrypt the API key before storing
        encrypted_key = encrypt_api_key(request.api_key)
        
        # Store the API key in the database
        stored_key_data = {
            "user_id": user_id, # Changed from UUID(user_id) to user_id (str)
            "provider": request.provider,
            "encrypted_api_key": encrypted_key,
            "validation_status": validation_status,
            "last_validated_at": datetime.utcnow(),
            "provider_metadata": request.provider_metadata
        }
        stored_key = await repos.user.store_api_key( # Changed from upsert_api_key to store_api_key
            user_id=stored_key_data["user_id"],
            provider=stored_key_data["provider"],
            encrypted_api_key=stored_key_data["encrypted_api_key"],
            validation_status=stored_key_data["validation_status"],
            provider_metadata=stored_key_data["provider_metadata"]
        )
        
        response_data = StoredAPIKeyResponse(
            provider=stored_key.provider,
            validation_status=stored_key.validation_status,
            last_validated_at=stored_key.last_validated_at,
            provider_metadata=stored_key.provider_metadata,
            message=message,
            created_at=stored_key.created_at,
            updated_at=stored_key.updated_at
        )
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error storing API key for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during key storage"
        )


@router.delete("/keys/{provider}", response_model=DeleteAPIKeyResponse)
async def delete_api_key(
    provider: PROVIDER_ID,
    user_id: str = Depends(get_current_user_id)
) -> DeleteAPIKeyResponse:
    """
    Delete a stored API key for a user by provider
    """
    try:
        repos = get_repositories()
        deleted_count = await repos.user.delete_api_key(user_id, provider) # Changed from UUID(user_id) to user_id (str)
        
        if deleted_count > 0:
            message = f"API key for provider {provider} deleted successfully."
            deleted = True
        else:
            message = f"API key for provider {provider} not found or already deleted."
            deleted = False
            
        return DeleteAPIKeyResponse(
            provider=provider,
            deleted=deleted,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting API key for user {user_id}, provider {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during key deletion"
        )


@router.get("/keys", response_model=ListUserAPIKeysResponse)
async def list_user_api_keys(
    user_id: str = Depends(get_current_user_id)
) -> ListUserAPIKeysResponse:
    """
    List a user's stored API keys
    """
    try:
        repos = get_repositories()
        stored_keys = await repos.user.list_user_api_keys(user_id) # Changed from get_api_keys_by_user_id(UUID(user_id)) to list_user_api_keys(user_id)
        
        api_keys_response = []
        for key in stored_keys:
            api_keys_response.append(StoredAPIKeyResponse(
                provider=key.provider,
                validation_status=key.validation_status,
                last_validated_at=key.last_validated_at,
                provider_metadata=key.provider_metadata,
                message="", # Message is not stored in DB for list response
                created_at=key.created_at,
                updated_at=key.updated_at
            ))
            
        return ListUserAPIKeysResponse(
            api_keys=api_keys_response,
            total_keys=len(api_keys_response)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing API keys for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during key listing"
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
    List all supported LLM providers and their models
    """
    try:
        providers = LLMService.get_all_llm_providers() # Changed from get_all_providers to get_all_llm_providers
        provider_responses = [_convert_provider_to_response(p, include_models) for p in providers]
        
        total_models = sum(len(p.models) for p in provider_responses)
        
        return ListProvidersResponse(
            providers=provider_responses,
            total_providers=len(provider_responses),
            total_models=total_models
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while listing providers"
        )


@router.get("/models", response_model=ListModelsResponse)
async def list_models(
    provider: Optional[PROVIDER_ID] = None,
    include_capabilities: bool = True,
    user_context: Dict[str, Any] = Depends(require_auth)
) -> ListModelsResponse:
    """
    List all supported LLM models, optionally filtered by provider
    """
    try:
        if provider:
            models = LLMService.get_hosted_models_for_provider(provider)
        else:
            all_providers = LLMService.get_all_llm_providers()
            models = []
            for p in all_providers:
                models.extend(LLMService.get_hosted_models_for_provider(p.provider_id))
            
        model_responses = [
            _convert_model_to_response(m)
            for m in models
        ]

        if not include_capabilities:
            # Filter out capabilities if not requested (though for now, they are always included by _convert_model_to_response)
            for model_res in model_responses:
                model_res.capabilities = []

        total_models = len(model_responses)
        
        return ListModelsResponse(
            models=model_responses,
            total_models=total_models,
            provider_filter=provider
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while listing models"
        )