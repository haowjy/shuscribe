# backend/src/services/llm/llm_service.py
"""
LLM Service - handles secure per-request LLM operations with self-hosted Portkey Gateway
"""
import logging
from typing import Dict, List, Optional, Any
from uuid import UUID

from portkey_ai import AsyncPortkey

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
from src.database.repositories.user import UserRepository
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
    
    def __init__(self, user_repository: "UserRepository"):
        self.user_repository = user_repository
        
        # Validate self-hosted Portkey Gateway is configured
        if not settings.PORTKEY_BASE_URL:
            raise ValidationError("PORTKEY_BASE_URL not configured in environment. Please ensure your self-hosted Portkey Gateway is running.")
    
    async def chat_completion(
        self,
        user_id: UUID,
        provider: str, # The provider ID (e.g., 'openai')
        model: str,    # The exact hosted model name (e.g., 'gpt-4o', 'claude-3-opus-20240229')
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion using user's API key through self-hosted Portkey Gateway
        
        Args:
            user_id: UUID of the user making the request
            provider: LLM provider ID (e.g., 'openai', 'anthropic')
            model: Exact hosted model name to use (e.g., 'gpt-4o')
            messages: List of messages for the conversation
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            trace_id: Optional trace ID for debugging
            metadata: Optional metadata for the request
            **kwargs: Additional parameters for the LLM
            
        Returns:
            LLMResponse with the completion
            
        Raises:
            LLMError: If the LLM request fails
            ValidationError: If user/keys are invalid or model not found
        """
        
        # Optional: Validate that the provider and model actually exist in our catalog
        # This provides an early check before making external calls.
        hosted_model_config = get_hosted_model_instance(provider, model)
        if not hosted_model_config:
            raise ValidationError(f"Model '{model}' not found for provider '{provider}' in the LLM catalog.")

        decrypted_key = None
        try:
            # 1. Get user's encrypted API key for this provider
            user_api_key_record = await self.user_repository.get_api_key(user_id, provider)
            if not user_api_key_record:
                raise ValidationError(f"No API key found for provider '{provider}' for user '{user_id}'. Please add it via settings.")
            
            # 2. Decrypt the key (only in memory, temporarily)
            decrypted_key = decrypt_api_key(str(user_api_key_record.encrypted_api_key))
            
            # 3. Create fresh Portkey client for this request - pointing to self-hosted gateway
            portkey_client = AsyncPortkey(
                base_url=settings.PORTKEY_BASE_URL
            )
            
            # 4. Configure request headers for Portkey to use the user's key
            portkey_options: Dict[str, Any] = {
                "provider": provider,
                "Authorization": f"Bearer {decrypted_key}",
            }
            
            # Add optional configurations
            if trace_id:
                portkey_options["trace_id"] = trace_id
            
            final_metadata = { "user_id": str(user_id), "shuscribe_version": "0.1.0" }
            if metadata:
                final_metadata.update(metadata)
            portkey_options["metadata"] = final_metadata
            
            # 5. Convert messages to OpenAI format (Portkey's standard for chat completions)
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # 6. Make the request through self-hosted Portkey
            logger.info(f"Making LLM request: provider={provider}, model={model}, user={user_id}, gateway={settings.PORTKEY_BASE_URL}")
            
            create_kwargs: Dict[str, Any] = {
                "model": model,
                "messages": openai_messages,
                "temperature": temperature,
                "stream": False,
                **kwargs,
            }
            if max_tokens is not None:
                create_kwargs["max_tokens"] = max_tokens

            response = await portkey_client.with_options(
                **portkey_options
            ).chat.completions.create(**create_kwargs)
            
            # 7. Return standardized response
            return LLMResponse(
                content=response.choices[0].message.content, # type: ignore
                model=response.model, # type: ignore
                usage=response.usage.dict() if response.usage else None, # type: ignore
                metadata={
                    "provider": provider,
                    "gateway": "self-hosted",
                    "portkey_request_id": getattr(response, 'id', None),
                    "trace_id": trace_id,
                }
            )
            
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.error(f"LLM request failed: {e}", exc_info=True, extra={
                "user_id": str(user_id),
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
                    "user_id": str(user_id)
                }
            )
        finally:
            if decrypted_key is not None:
                del decrypted_key
    
    async def validate_api_key(
        self,
        provider: str,
        api_key: str,
        test_model: Optional[str] = None # This is now the exact hosted model name
    ) -> Dict[str, Any]:
        """
        Validate a user's raw API key by making a minimal test request through self-hosted Portkey Gateway.
        
        Args:
            provider: The ID of the LLM provider (e.g., 'openai').
            api_key: The raw API key provided by the user.
            test_model: An optional specific *hosted model name* to test against.
            
        Returns:
            A dictionary indicating validation status and details.
        """
        
        try:
            # Use a default test model if none provided
            if not test_model:
                # CHANGED: Use the catalog helper function to get the default test model name
                test_model = get_default_test_model_name_for_provider(provider)
                if not test_model:
                    raise ValidationError(f"No suitable default test model configured for provider '{provider}'.")
            
            portkey_client = AsyncPortkey(
                base_url=settings.PORTKEY_BASE_URL
            )
            
            test_messages = [{"role": "user", "content": "Hello"}]
            
            validation_response = await portkey_client.with_options(
                provider=provider,
                Authorization=f"Bearer {api_key}"
            ).chat.completions.create(
                model=test_model,
                messages=test_messages,
                max_tokens=5,
                temperature=0.0,
                stream=False,
            )
            
            return {
                "valid": True,
                "provider": provider,
                "test_model": test_model,
                "response_model": validation_response.model, # type: ignore
                "gateway": "self-hosted",
                "message": "API key successfully validated."
            }
            
        except Exception as e:
            logger.warning(f"API key validation failed for provider '{provider}': {e}")
            return {
                "valid": False,
                "provider": provider,
                "gateway": "self-hosted",
                "error": str(e),
                "message": "API key validation failed. Please check your key or provider."
            }
    
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
        """
        Returns the capabilities of a specific hosted model instance by looking up its
        AI Model Family.
        """
        return get_capabilities_for_hosted_model(provider_id, model_name)
    
    def get_hosted_model_details(self, provider_id: str, model_name: str) -> Optional[HostedModelInstance]:
        """Returns the full HostedModelInstance object for a specific provider and model name."""
        return get_hosted_model_instance(provider_id, model_name)