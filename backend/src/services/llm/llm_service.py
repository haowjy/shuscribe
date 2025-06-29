# backend/src/services/llm/llm_service.py
"""
LLM Service - handles secure per-request LLM operations with self-hosted Portkey Gateway

Features:
- Secure BYOK (Bring Your Own Key) model with encrypted API key storage
- Streaming and non-streaming chat completions
- Self-hosted Portkey Gateway for privacy and control
- Comprehensive error handling and logging
- Support for multiple LLM providers (OpenAI, Anthropic, Google, etc.)
"""
import logging
from typing import Dict, List, Optional, Any, AsyncIterator, Type, Union
from uuid import UUID
from pydantic import BaseModel

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
from src.utils.json_schema_resolver import json_schema_to_prompt_instructions


logger = logging.getLogger(__name__)


class LLMService:
    """
    Secure LLM service using BYOK model with self-hosted Portkey Gateway
    
    Creates fresh Portkey client instances per request for security.
    Never stores decrypted keys persistently or exposes them.
    
    Key Features:
    - Streaming and non-streaming chat completions
    - Secure API key management with encryption
    - Self-hosted Portkey Gateway for privacy
    - Multi-provider support (OpenAI, Anthropic, Google, etc.)
    - Comprehensive logging and error handling
    """
    
    def __init__(self, user_repository: Optional[AbstractUserRepository] = None):
        self.user_repository = user_repository
        
        # Validate self-hosted Portkey Gateway is configured
        if not settings.PORTKEY_BASE_URL:
            raise ValidationError("PORTKEY_BASE_URL not configured in environment. Please ensure your self-hosted Portkey Gateway is running.")
    
    def _simplify_schema_for_google(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simplifies a JSON schema for Google Gemini by removing validation constraints
        that it doesn't support.
        
        Google's response_schema format doesn't support validation constraints like:
        - minimum, maximum (from ge, le constraints)
        - minLength, maxLength (from min_length, max_length)
        - minItems, maxItems (from min_items, max_items)
        - pattern (from regex patterns)
        
        Args:
            schema: Original JSON schema with validation constraints
            
        Returns:
            Simplified schema without unsupported validation constraints
        """
        def remove_validation_constraints(obj: Any) -> Any:
            if isinstance(obj, dict):
                # Create a new dict without validation constraints
                cleaned = {}
                for key, value in obj.items():
                    # Skip validation constraint keys
                    if key in ['minimum', 'maximum', 'minLength', 'maxLength', 
                              'minItems', 'maxItems', 'pattern', 'format']:
                        continue
                    # Recursively clean nested objects
                    cleaned[key] = remove_validation_constraints(value)
                return cleaned
            elif isinstance(obj, list):
                # Recursively clean list items
                return [remove_validation_constraints(item) for item in obj]
            else:
                # Return primitive values as-is
                return obj
        
        return remove_validation_constraints(schema)

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
        response_format: Optional[Type[BaseModel]] = None,
        
        **kwargs
    ) -> Union[LLMResponse, AsyncIterator[LLMResponse]]:
        """
        Generate chat completion using user's API key through self-hosted Portkey Gateway
        
        This method supports both streaming and non-streaming responses:
        - When stream=False: Returns LLMResponse object with the complete response
        - When stream=True: Returns AsyncIterator[LLMResponse] for real-time streaming
        
        Streaming is useful for:
        - Long-running operations where user feedback is important
        - Real-time chat interfaces
        - Reducing perceived latency in user interfaces
        
        Args:
            provider: LLM provider ID (e.g., 'openai', 'anthropic')
            model: Exact hosted model name to use (e.g., 'gpt-4o')
            messages: List of messages for the conversation
            user_id: UUID of the user making the request (required if using database)
            api_key: Direct API key (bypasses database lookup if provided)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            trace_id: Optional trace ID for debugging
            metadata: Optional metadata for the request
            stream: Whether to return a stream of responses
            response_format: Optional pydantic model type for structured output
            **kwargs: Additional parameters for the LLM
            
        Returns:
            - LLMResponse: Complete response when stream=False
            - AsyncIterator[LLMResponse]: Stream of response chunks when stream=True
            
        Raises:
            LLMError: If the LLM request fails
            ValidationError: If user/keys are invalid or model not found
            
        Examples:
            # Non-streaming usage
            response = await llm_service.chat_completion(
                provider="openai",
                model="gpt-4o",
                messages=[LLMMessage(role="user", content="Hello")],
                user_id=user_id,
                stream=False
            )
            print(response.content)
            
            # Streaming usage
            async for chunk in await llm_service.chat_completion(
                provider="openai", 
                model="gpt-4o",
                messages=[LLMMessage(role="user", content="Hello")],
                user_id=user_id,
                stream=True
            ):
                print(chunk.content, end="")
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
                "auth_method": "direct_api_key" if api_key else "database_lookup",
                "streaming": stream
            }
            if user_id:
                final_metadata["user_id"] = str(user_id)
            if metadata:
                final_metadata.update(metadata)
            portkey_options["metadata"] = final_metadata
            
            # 4. Check if model supports structured output and handle response format
            model_capabilities = get_capabilities_for_hosted_model(provider, model)
            supports_structured_output = LLMCapability.STRUCTURED_OUTPUT in model_capabilities
            
            # Convert messages to OpenAI format (Portkey's standard for chat completions)
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Handle response_format conversion based on model capabilities
            if response_format is not None:
                # Get the base JSON schema
                base_schema = response_format.model_json_schema()
                
                if supports_structured_output:
                    # Model supports structured output - use response_format parameter
                    logger.info(f"Model {model} supports structured output - using response_format parameter")
                    
                    # Simplify schema for Google Gemini (remove validation constraints)
                    if provider.lower() == "google":
                        simplified_schema = self._simplify_schema_for_google(base_schema)
                        logger.info(f"Using simplified schema for Google Gemini (removed validation constraints)")
                    else:
                        simplified_schema = base_schema
                        logger.info(f"Using standard schema for provider: {provider}")
                else:
                    # Model doesn't support structured output - append instructions to prompt
                    logger.info(f"Model {model} does not support structured output - appending schema instructions to prompt")
                    
                    # Generate prompt instructions from schema
                    schema_instructions = json_schema_to_prompt_instructions(
                        base_schema, 
                        response_format.__name__
                    )
                    
                    # Append instructions to the last message (assuming it's a user message)
                    if openai_messages and openai_messages[-1]["role"] in ["user", "system"]:
                        openai_messages[-1]["content"] += schema_instructions
                    else:
                        # If no user/system message, add as a system message
                        openai_messages.append({
                            "role": "system",
                            "content": f"Important: {schema_instructions}"
                        })
            
            # 5. Make the request through self-hosted Portkey
            logger.info(f"Making LLM request: provider={provider}, model={model}, gateway={settings.PORTKEY_BASE_URL}, streaming={stream}")
            
            create_kwargs: Dict[str, Any] = {
                "model": model,
                "messages": openai_messages,
                "temperature": temperature,
                "stream": stream,
                **kwargs,
            }
            if max_tokens is not None:
                create_kwargs["max_tokens"] = max_tokens

            # Only set response_format if model supports structured output
            if response_format is not None and supports_structured_output:
                # Get the base JSON schema
                base_schema = response_format.model_json_schema()
                
                # Simplify schema for Google Gemini (remove validation constraints)
                if provider.lower() == "google":
                    simplified_schema = self._simplify_schema_for_google(base_schema)
                else:
                    simplified_schema = base_schema
                
                # Convert Pydantic model to stable JSON schema format
                create_kwargs["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": f"{response_format.__name__.lower()}_schema",
                        "schema": simplified_schema
                    }
                }

            # Use stable chat.completions.create() method
            response = await portkey_client.with_options(
                **portkey_options
            ).chat.completions.create(**create_kwargs)
            
            # 7. Return standardized response
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
                    usage=response.usage.model_dump() if response.usage else None, # type: ignore
                    metadata={
                        "provider": provider,
                        "gateway": "self-hosted",
                        "portkey_request_id": getattr(response, 'id', None),
                        "trace_id": trace_id,
                        "auth_method": "direct_api_key" if api_key else "database_lookup",
                        "streaming": False
                    }
                )
            
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.error(f"LLM request failed: {e}", exc_info=True, extra={
                "user_id": str(user_id) if user_id else "direct_api_key",
                "provider": provider, 
                "model": model,
                "gateway_url": settings.PORTKEY_BASE_URL,
                "streaming": stream
            })
            raise LLMError(
                provider=f"portkey-self-hosted/{provider}",
                message=f"An error occurred during LLM call: {e}",
                details={
                    "model": model,
                    "provider": provider,
                    "user_id": str(user_id) if user_id else "direct_api_key",
                    "streaming": stream
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
        
        This method handles the conversion from Portkey's streaming format to our
        standardized LLMResponse format, ensuring consistent interfaces across
        different LLM providers.
        
        Args:
            portkey_stream_response: Streaming response from Portkey
            provider: Provider ID for metadata
            trace_id: Optional trace ID for debugging
            
        Yields:
            LLMResponse objects with incremental content
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
                    "streaming": True,
                    "chunk": True
                }
            )
    
    @staticmethod
    def get_all_llm_providers() -> List[LLMProvider]:
        """Returns a list of all configured LLM providers with their hosted models."""
        return get_all_llm_providers()

    @staticmethod
    def get_hosted_models_for_provider(provider_id: str) -> List[HostedModelInstance]:
        """Returns a list of hosted model instances offered by a specific provider."""
        return get_hosted_models_for_provider(provider_id)
    
    @staticmethod
    def get_all_ai_model_families() -> List[AIModelFamily]:
        """Returns a list of all abstract AI model families defined in the catalog."""
        return get_all_ai_model_families()

    @staticmethod
    def get_capabilities_for_hosted_model(provider_id: str, model_name: str) -> List[LLMCapability]:
        """Returns the list of capabilities for a specific hosted model."""
        return get_capabilities_for_hosted_model(provider_id, model_name)
    
    @staticmethod
    def get_default_test_model_name_for_provider(provider_id: str) -> str:
        """Gets the default model name for a provider, for API key validation."""
        return get_default_test_model_name_for_provider(provider_id)
    
    @staticmethod
    def get_hosted_model_details(provider_id: str, model_name: str) -> Optional[HostedModelInstance]:
        """Returns detailed information for a specific hosted model instance."""
        return get_hosted_model_instance(provider_id, model_name)