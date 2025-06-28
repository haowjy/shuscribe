# backend/src/services/llm/llm_service.py
"""
LLM Service - handles secure per-request LLM operations with self-hosted Portkey Gateway
"""
import logging
from typing import Dict, List, Optional, Any, AsyncIterator
from uuid import UUID

from portkey_ai import AsyncPortkey
# from portkey_ai.types.chat import ChatCompletion, ChatCompletionChunk # Removed problematic import

from src.config import settings
# CHANGED: Import all LLM configuration details from the new core catalog module
from src.core.llm.catalog import (
    get_hosted_model_instance,
    get_capabilities_for_hosted_model,
    get_all_llm_providers, # For listing providers
    get_hosted_models_for_provider, # For getting models of a specific provider
    get_default_test_model_name_for_provider, # For validation endpoint
    get_all_ai_model_families, # For getting all AI model families
)
from src.core.exceptions import LLMError, ValidationError
from src.database.repositories.user.user_abc import AbstractUserRepository
# NEW: Import Pydantic models from their new schema locations
from src.schemas.llm.models import LLMMessage, LLMResponse
from src.schemas.llm.config import LLMCapability, HostedModelInstance, LLMProvider, AIModelFamily
from src.core.encryption import decrypt_api_key


logger = logging.getLogger(__name__)


class LLMService:
    """
    Secure LLM service using BYOK model with self-hosted Portkey Gateway
    
    Creates fresh Portkey client instances per request for security.
    Never stores decrypted keys persistently or exposes them.
    """
    
    def __init__(self, user_repository: Optional[AbstractUserRepository] = None):
        self.user_repository = user_repository
        
        # Validate self-hosted Portkey Gateway is configured
        if not settings.PORTKEY_BASE_URL:
            raise ValidationError("PORTKEY_BASE_URL not configured in environment. Please ensure your self-hosted Portkey Gateway is running.")
    
    async def chat_completion(
        self,
        provider: str, # The provider ID (e.g., 'openai')
        model: str,    # The exact hosted model name (e.g., 'gpt-4o', 'claude-3-opus-20240229')
        messages: List[LLMMessage],
        user_id: Optional[UUID] = None,  # Optional when using direct API key
        api_key: Optional[str] = None,   # Optional direct API key (bypasses database)
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse | AsyncIterator[LLMResponse]:
        """
        Generate chat completion using user's API key through self-hosted Portkey Gateway
        
        Args:
            provider: LLM provider ID (e.g., 'openai', 'anthropic')
            model: Exact hosted model name to use (e.g., 'gpt-4o')
            messages: List of messages for the conversation
            user_id: UUID of the user making the request (required if using database)
            api_key: Direct API key (bypasses database lookup if provided)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            trace_id: Optional trace ID for debugging
            metadata: Optional metadata for the request
            stream: Whether to return a stream of responses
            **kwargs: Additional parameters for the LLM
            
        Returns:
            LLMResponse with the completion or AsyncIterator[LLMResponse] for streaming
            
        Raises:
            LLMError: If the LLM request fails
            ValidationError: If user/keys are invalid or model not found
        """
        
        # Optional: Validate that the provider and model actually exist in our catalog
        # This provides an early check before making external calls.
        hosted_model_config = get_hosted_model_instance(provider, model)
        if not hosted_model_config:
            raise ValidationError(f"Model '{model}' not found for provider '{provider}' in the LLM catalog.")

        # Validate input parameters
        if not api_key and not user_id:
            raise ValidationError("Either 'api_key' or 'user_id' must be provided.")
        
        if not api_key and not self.user_repository:
            raise ValidationError("UserRepository is required when using user_id for API key lookup.")

        decrypted_key = None
        try:
            # 1. Get API key (either direct or from database)
            if api_key:
                # Use direct API key
                decrypted_key = api_key
                logger.info(f"Using direct API key for provider={provider}, model={model}")
            else:
                # Get user's encrypted API key from database
                if not self.user_repository:
                    raise ValidationError("UserRepository is required when using user_id for API key lookup.")
                if not user_id:
                    raise ValidationError("user_id is required when not using direct API key.")
                
                user_api_key_record = await self.user_repository.get_api_key(user_id, provider)
                if not user_api_key_record:
                    raise ValidationError(f"No API key found for provider '{provider}' for user '{user_id}'. Please add it via settings.")
                
                # Decrypt the key (only in memory, temporarily)
                decrypted_key = decrypt_api_key(str(user_api_key_record.encrypted_api_key))
                logger.info(f"Using database API key for provider={provider}, model={model}, user={user_id}")
            
            # 2. Create fresh Portkey client for this request - pointing to self-hosted gateway
            portkey_client = AsyncPortkey(
                base_url=settings.PORTKEY_BASE_URL
            )
            
            # 3. Configure request headers for Portkey to use the API key
            portkey_options: Dict[str, Any] = {
                "provider": provider,
                "Authorization": f"Bearer {decrypted_key}",
            }
            
            # Add optional configurations
            if trace_id:
                portkey_options["trace_id"] = trace_id
            
            final_metadata = { 
                "shuscribe_version": "0.1.0",
                "auth_method": "direct_api_key" if api_key else "database_lookup"
            }
            if user_id:
                final_metadata["user_id"] = str(user_id)
            if metadata:
                final_metadata.update(metadata)
            portkey_options["metadata"] = final_metadata
            
            # 4. Convert messages to OpenAI format (Portkey's standard for chat completions)
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # 5. Make the request through self-hosted Portkey
            logger.info(f"Making LLM request: provider={provider}, model={model}, gateway={settings.PORTKEY_BASE_URL}")
            
            create_kwargs: Dict[str, Any] = {
                "model": model,
                "messages": openai_messages,
                "temperature": temperature,
                "stream": stream,
                **kwargs,
            }
            if max_tokens is not None:
                create_kwargs["max_tokens"] = max_tokens

            response = await portkey_client.with_options(
                **portkey_options
            ).chat.completions.create(**create_kwargs)
            
            # 6. Return standardized response
            if stream:
                return self._stream_response_to_llm_response(
                    response,
                    provider,
                    trace_id
                )
            else:
                # Ensure non-streaming response is correctly handled, assuming it's not a stream
                # If Portkey's non-streaming response is truly ChatCompletion, it should work.
                # Otherwise, further inspection of Portkey's non-streaming return type is needed.
                return LLMResponse(
                    content=response.choices[0].message.content, # type: ignore
                    model=response.model, # type: ignore
                    usage=response.usage.dict() if response.usage else None, # type: ignore
                    metadata={
                        "provider": provider,
                        "gateway": "self-hosted",
                        "portkey_request_id": getattr(response, 'id', None),
                        "trace_id": trace_id,
                        "auth_method": "direct_api_key" if api_key else "database_lookup"
                    }
                )
            
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.error(f"LLM request failed: {e}", exc_info=True, extra={
                "user_id": str(user_id) if user_id else "direct_api_key",
                "provider": provider, 
                "model": model,
                "gateway_url": settings.PORTKEY_BASE_URL
            })
            raise LLMError(
                provider=f"portkey-self-hosted/{provider}",
                message=f"An error occurred during LLM call: {e}",
                details={
                    "model": model,
                    "provider": provider,
                    "user_id": str(user_id) if user_id else "direct_api_key"
                }
            )
        finally:
            # Only clear decrypted_key if it came from database (not direct API key)
            if decrypted_key is not None and not api_key:
                del decrypted_key
    
    async def _stream_response_to_llm_response(
        self,
        portkey_stream_response: Any, # Changed to Any to resolve import issues
        provider: str,
        trace_id: Optional[str],
    ) -> AsyncIterator[LLMResponse]:
        """
        Converts a Portkey streaming response into an AsyncIterator of LLMResponse objects.
        """
        async for chunk in portkey_stream_response:
            yield LLMResponse(
                content=chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta.content else "",
                model=chunk.model, # type: ignore
                usage=chunk.usage.dict() if hasattr(chunk, 'usage') and chunk.usage else None, # Handle optional usage
                metadata={
                    "provider": provider,
                    "gateway": "self-hosted",
                    "portkey_request_id": getattr(chunk, 'id', None),
                    "trace_id": trace_id,
                }
            )
    
    def get_all_llm_providers(self) -> List[LLMProvider]:
        """Returns a list of all configured LLM providers with their hosted models."""
        return get_all_llm_providers()

    def get_hosted_models_for_provider(self, provider_id: str) -> List[HostedModelInstance]:
        """Returns a list of hosted model instances offered by a specific provider."""
        return get_hosted_models_for_provider(provider_id)
    
    def get_all_ai_model_families(self) -> List[AIModelFamily]:
        """Returns a list of all abstract AI model families defined in the catalog."""
        return get_all_ai_model_families()

    def get_capabilities_for_hosted_model(self, provider_id: str, model_name: str) -> List[LLMCapability]:
        """Returns the list of capabilities for a specific hosted model."""
        return get_capabilities_for_hosted_model(provider_id, model_name)

    def get_default_test_model_name_for_provider(self, provider_id: str) -> Optional[str]:
        """Gets the default model name for a provider, for API key validation."""
        return get_default_test_model_name_for_provider(provider_id)
    
    def get_hosted_model_details(self, provider_id: str, model_name: str) -> Optional[HostedModelInstance]:
        """Returns detailed information for a specific hosted model instance."""
        return get_hosted_model_instance(provider_id, model_name)