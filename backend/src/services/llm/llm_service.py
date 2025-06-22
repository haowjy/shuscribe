# backend/src/services/llm/llm_service.py
"""
LLM Service - handles secure per-request LLM operations with self-hosted Portkey Gateway
"""
import logging
from typing import Dict, List, Optional, Any
from uuid import UUID

from portkey_ai import AsyncPortkey

from src.config import settings
from src.core.constants import DEFAULT_PROVIDER_CONFIGS
from src.core.exceptions import LLMError, ValidationError
from src.database.repositories.user import UserRepository # This import will be valid soon
from src.services.llm.base import LLMMessage, LLMResponse
from src.utils.encryption import decrypt_api_key # This import will be valid soon


logger = logging.getLogger(__name__)


class LLMService:
    """
    Secure LLM service using BYOK model with self-hosted Portkey Gateway
    
    Creates fresh Portkey client instances per request for security.
    Never stores decrypted keys persistently or exposes them.
    """
    
    def __init__(self, user_repository: "UserRepository"): # Forward ref for now
        self.user_repository = user_repository
        
        # Validate self-hosted Portkey Gateway is configured
        if not settings.PORTKEY_BASE_URL:
            raise ValidationError("PORTKEY_BASE_URL not configured in environment. Please ensure your self-hosted Portkey Gateway is running.")
    
    async def chat_completion(
        self,
        user_id: UUID,
        provider: str,
        model: str,
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
            provider: LLM provider name (e.g., 'openai', 'anthropic')
            model: Model name to use
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
            ValidationError: If user/keys are invalid
        """
        
        decrypted_key = None # Initialize to None for finally block
        try:
            # 1. Get user's encrypted API key for this provider
            user_api_key_record = await self.user_repository.get_api_key(user_id, provider)
            if not user_api_key_record:
                raise ValidationError(f"No API key found for provider '{provider}' for user '{user_id}'. Please add it via settings.")
            
            # 2. Decrypt the key (only in memory, temporarily)
            decrypted_key = decrypt_api_key(user_api_key_record.encrypted_api_key)
            
            # 3. Create fresh Portkey client for this request - pointing to self-hosted gateway
            portkey_client = AsyncPortkey(
                # No api_key parameter needed for self-hosted gateway
                base_url=settings.PORTKEY_BASE_URL  # Points to your self-hosted gateway (e.g., http://localhost:8787/v1)
            )
            
            # 4. Configure request headers for Portkey to use the user's key
            request_config = {
                "provider": provider,
                "Authorization": f"Bearer {decrypted_key}",
            }
            
            # Add optional configurations
            if trace_id:
                request_config["trace_id"] = trace_id
            if metadata:
                request_config["metadata"] = {
                    **metadata,
                    "user_id": str(user_id),
                    "shuscribe_version": "0.1.0"
                }
            
            # 5. Convert messages to OpenAI format (Portkey's standard for chat completions)
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # 6. Make the request through self-hosted Portkey
            logger.info(f"Making LLM request: provider={provider}, model={model}, user={user_id}, gateway={settings.PORTKEY_BASE_URL}")
            
            response = await portkey_client.with_options(**request_config).chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # 7. Return standardized response
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage=response.usage.model_dump() if response.usage else None,
                metadata={
                    "provider": provider,
                    "gateway": "self-hosted",
                    "portkey_request_id": getattr(response, 'id', None),
                    "trace_id": trace_id,
                }
            )
            
        except ValidationError as e:
            raise e # Re-raise validation errors directly
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
                    "user_id": str(user_id),
                    "gateway_url": settings.PORTKEY_BASE_URL
                }
            )
        finally:
            # Ensure the decrypted key is cleared from memory
            if decrypted_key is not None:
                del decrypted_key
    
    async def validate_api_key(
        self,
        provider: str,
        api_key: str,
        test_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate a user's raw API key by making a minimal test request through self-hosted Portkey Gateway.
        
        Args:
            provider: The name of the LLM provider (e.g., 'openai').
            api_key: The raw API key provided by the user.
            test_model: An optional specific model to test against.
            
        Returns:
            A dictionary indicating validation status and details.
        """
        
        try:
            # Use a default test model if none provided
            if not test_model:
                test_model = DEFAULT_PROVIDER_CONFIGS.get(provider, {}).get("default_model")
                if not test_model:
                    raise ValidationError(f"No suitable test model configured for provider '{provider}'.")
            
            # Create a temporary Portkey client for this validation request
            portkey_client = AsyncPortkey(
                # No api_key parameter needed for self-hosted gateway
                base_url=settings.PORTKEY_BASE_URL
            )
            
            # Test with a minimal request (e.g., "Hello" with max_tokens=5)
            test_messages = [{"role": "user", "content": "Hello"}]
            
            validation_response = await portkey_client.with_options(
                provider=provider,
                Authorization=f"Bearer {api_key}" # Use the raw key directly for validation
            ).chat.completions.create(
                model=test_model,
                messages=test_messages,
                max_tokens=5, # Keep it short and cheap
                temperature=0.0 # No randomness
            )
            
            # If we get here, the key is likely valid
            return {
                "valid": True,
                "provider": provider,
                "test_model": test_model,
                "response_model": validation_response.model,
                "gateway": "self-hosted",
                "message": "API key successfully validated."
            }
            
        except Exception as e:
            # Catch all exceptions to provide a clear error message
            logger.warning(f"API key validation failed for provider '{provider}': {e}")
            return {
                "valid": False,
                "provider": provider,
                "gateway": "self-hosted",
                "error": str(e),
                "message": "API key validation failed. Please check your key or provider."
            }
    
    def get_supported_providers(self) -> List[str]:
        """Get a list of currently supported LLM providers for UI display."""
        return POPULAR_LLM_PROVIDERS

    def get_models_for_provider(self, provider: str) -> List[str]:
        """Get models configured for a specific provider."""
        return DEFAULT_PROVIDER_CONFIGS.get(provider, {}).get("models", [])