# backend/src/services/llm/llm_service.py
"""
LLM Service - handles secure per-request LLM operations with self-hosted Portkey Gateway

Features:
- Secure BYOK (Bring Your Own Key) model with encrypted API key storage
- Streaming and non-streaming chat completions
- Self-hosted Portkey Gateway for privacy and control
- Comprehensive error handling and logging
- Support for multiple LLM providers (OpenAI, Anthropic, Google, etc.)
- Thinking effort support with model-specific budget token conversion
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
    model_supports_temperature, # NEW: For checking temperature support
    get_temperature_restriction_message, # NEW: For temperature warnings
    should_use_completion_tokens_param, # NEW: For max_tokens parameter handling
    calculate_thinking_budget_tokens, # NEW: For thinking budget calculation
    model_supports_thinking, # NEW: For checking thinking support
)
from src.core.exceptions import LLMError, ValidationError
from src.database.interfaces.user_repository import IUserRepository
# NEW: Import Pydantic models from their new schema locations
from src.schemas.llm.models import LLMMessage, LLMResponse, ChunkType, ThinkingEffort
from src.schemas.llm.config import LLMCapability, HostedModelInstance, LLMProvider, AIModelFamily
from src.core.encryption import decrypt_api_key
from src.utils import json_schema_to_prompt_instructions


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
    - Thinking effort support with model-specific budget token conversion
    - Comprehensive logging and error handling
    """
    
    def __init__(self, user_repository: Optional[IUserRepository] = None):
        self.user_repository = user_repository
        
        # Validate self-hosted Portkey Gateway is configured
        if not settings.PORTKEY_BASE_URL:
            raise ValidationError("PORTKEY_BASE_URL not configured in environment. Please ensure your self-hosted Portkey Gateway is running.")
    
    def _prepare_thinking_parameters(
        self,
        thinking_effort: ThinkingEffort,
        provider: str,
        model: str,
        max_tokens: Optional[int]
    ) -> tuple[Optional[int], Optional[Dict[str, Any]]]:
        """
        Unified method to handle all thinking mode preparation.
        
        This method:
        1. Calculates thinking budget tokens if needed
        2. Adjusts max_tokens for provider constraints 
        3. Creates the thinking parameter dict for the API call
        
        Args:
            thinking_effort: The thinking effort level
            provider: LLM provider ID
            model: Model name
            max_tokens: Original max_tokens requested
            
        Returns:
            Tuple of (adjusted_max_tokens, thinking_params_dict)
            - adjusted_max_tokens: Modified max_tokens value or original if no change needed
            - thinking_params_dict: Dict to add to create_kwargs, or None if not applicable
        """
        # Check if model supports thinking
        if not model_supports_thinking(provider, model):
            logger.warning(f"Model {provider}/{model} does not support thinking mode")
            return max_tokens, None
        
        provider_lower = provider.lower()
        
        # Create thinking parameters dict based on provider
        thinking_params = None
        adjusted_max_tokens = max_tokens
        
        if provider_lower == "openai":
            # OpenAI uses reasoning_effort parameter
            effort_mapping = {
                ThinkingEffort.LOW: "low",
                ThinkingEffort.MEDIUM: "medium", 
                ThinkingEffort.HIGH: "high",
                ThinkingEffort.AUTO: "medium"  # Default to medium for AUTO
            }
            reasoning_effort = effort_mapping[thinking_effort]
            thinking_params = {"reasoning_effort": reasoning_effort}
            logger.info(f"Using reasoning_effort='{reasoning_effort}' for OpenAI model {model}")
            
        else:
            # Google/Anthropic use token budget system
            budget_tokens = None
            if thinking_effort != ThinkingEffort.AUTO:
                try:
                    budget_tokens = calculate_thinking_budget_tokens(
                        provider, model, thinking_effort.value
                    )
                    if budget_tokens is not None:
                        logger.info(f"Calculated thinking budget: {budget_tokens} tokens "
                                   f"for {thinking_effort.value} effort on {provider}/{model}")
                except Exception as e:
                    logger.warning(f"Failed to calculate thinking budget for {provider}/{model}: {e}")
            
            # Adjust max_tokens based on provider requirements
            if adjusted_max_tokens is not None:
                if provider_lower == "anthropic":
                    if budget_tokens is not None:
                        # Specific budget: max_tokens must be > thinking.budget_tokens
                        if adjusted_max_tokens <= budget_tokens:
                            adjusted_max_tokens = budget_tokens + adjusted_max_tokens
                            logger.info(f"Anthropic thinking: Adjusting max_tokens from {max_tokens} to {adjusted_max_tokens} "
                                       f"(thinking: {budget_tokens} + output: {max_tokens})")
                    else:
                        # AUTO mode: Add conservative buffer
                        adjusted_max_tokens = adjusted_max_tokens + min(adjusted_max_tokens, 8000)
                        logger.info(f"Anthropic AUTO thinking: Adjusting max_tokens from {max_tokens} to {adjusted_max_tokens} "
                                   f"(original: {max_tokens} + buffer: {min(adjusted_max_tokens, 8000)})")
                        
                elif provider_lower == "google":
                    if budget_tokens is not None:
                        # Specific budget: Conservative approach
                        if adjusted_max_tokens <= budget_tokens:
                            adjusted_max_tokens = budget_tokens + min(adjusted_max_tokens, 8000)
                            logger.info(f"Google thinking: Adjusting max_tokens from {max_tokens} to {adjusted_max_tokens} "
                                       f"(thinking: {budget_tokens} + output buffer: {min(adjusted_max_tokens, 8000)})")
                    else:
                        # AUTO mode: Conservative buffer
                        adjusted_max_tokens = adjusted_max_tokens + min(adjusted_max_tokens // 2, 4000)
                        logger.info(f"Google AUTO thinking: Adjusting max_tokens from {max_tokens} to {adjusted_max_tokens} "
                                   f"(original: {max_tokens} + buffer: {min(adjusted_max_tokens // 2, 4000)})")
            
            # Create thinking parameters for non-OpenAI providers
            if provider_lower == "anthropic":
                if thinking_effort == ThinkingEffort.AUTO or budget_tokens is None:
                    thinking_params = {"type": "enabled"}
                    logger.info(f"Using AUTO thinking for Anthropic model {model}")
                else:
                    thinking_params = {
                        "type": "enabled",
                        "budget_tokens": budget_tokens
                    }
                    logger.info(f"Using thinking with {budget_tokens} budget tokens for Anthropic model {model}")
                    
            elif provider_lower == "google":
                if thinking_effort == ThinkingEffort.AUTO or budget_tokens is None:
                    thinking_params = {"type": "enabled"}
                    logger.info(f"Using AUTO thinking for Google model {model}")
                else:
                    thinking_params = {
                        "type": "enabled",
                        "budget_tokens": budget_tokens
                    }
                    logger.info(f"Using thinking with {budget_tokens} budget tokens for Google model {model}")
        
        return adjusted_max_tokens, thinking_params
    
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

    def _determine_chunk_type_from_content_blocks(self, chunk: Any) -> ChunkType:
        """
        Determine chunk type using Portkey's built-in content_blocks structure for thinking models.
        
        For thinking/reasoning models, Portkey provides content in content_blocks array:
        - thinking content: content_blocks with type "thinking" or "thinking" field
        - regular content: content_blocks with type "text"/"content" or regular content field
        
        Args:
            chunk: The streaming chunk from Portkey
            
        Returns:
            ChunkType indicating whether this is thinking or content
        """
        try:
            # Check if this chunk has content_blocks (thinking models)
            if (hasattr(chunk, 'choices') and chunk.choices and 
                hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta):
                
                delta = chunk.choices[0].delta
                
                # Check for content_blocks array (thinking models)
                content_blocks = getattr(delta, 'content_blocks', None)
                if content_blocks:
                    # DEBUG: Log content_blocks structure for the first few chunks
                    if len(content_blocks) <= 2:  # Only log first couple chunks to avoid spam
                        logger.debug(f"Content blocks structure: {len(content_blocks)} blocks")
                        for i, block in enumerate(content_blocks):
                            if hasattr(block, '__dict__'):
                                logger.debug(f"  Block {i} attributes: {list(block.__dict__.keys())}")
                            elif isinstance(block, dict):
                                logger.debug(f"  Block {i} dict keys: {list(block.keys())}")
                            logger.debug(f"  Block {i} type: {type(block)}, repr: {repr(block)[:200]}...")
                    
                    # Process each content block to determine type
                    has_thinking = False
                    has_content = False
                    
                    for content_block in content_blocks:
                        # Check for explicit type field
                        if hasattr(content_block, 'type'):
                            if content_block.type == 'thinking':
                                has_thinking = True
                            elif content_block.type in ['text', 'content']:
                                has_content = True
                        # Check for thinking field presence
                        elif hasattr(content_block, 'thinking') and content_block.thinking:
                            has_thinking = True
                        elif hasattr(content_block, 'text') and content_block.text:
                            has_content = True
                        elif hasattr(content_block, 'content') and content_block.content:
                            has_content = True
                        # Check for delta field (Anthropic thinking mode)
                        elif hasattr(content_block, 'delta') and content_block.delta:
                            if hasattr(content_block.delta, 'thinking') and content_block.delta.thinking:
                                has_thinking = True
                            elif hasattr(content_block.delta, 'text') and content_block.delta.text:
                                has_content = True
                        # Handle dict structure
                        elif isinstance(content_block, dict):
                            if 'type' in content_block:
                                if content_block['type'] == 'thinking':
                                    has_thinking = True
                                elif content_block['type'] in ['text', 'content']:
                                    has_content = True
                            elif 'thinking' in content_block and content_block['thinking']:
                                has_thinking = True
                            elif 'text' in content_block and content_block['text']:
                                has_content = True
                            elif 'content' in content_block and content_block['content']:
                                has_content = True
                            # Handle Anthropic delta structure: {'index': 0, 'delta': {'thinking': '...'}}
                            elif 'delta' in content_block and content_block['delta']:
                                delta = content_block['delta']
                                if isinstance(delta, dict):
                                    if 'thinking' in delta and delta['thinking']:
                                        has_thinking = True
                                    elif 'text' in delta and delta['text']:
                                        has_content = True
                    
                    # Return type based on what we found
                    if has_thinking and not has_content:
                        return ChunkType.THINKING
                    elif has_content and not has_thinking:
                        return ChunkType.CONTENT
                    elif has_thinking and has_content:
                        # Mixed content - return THINKING to indicate this chunk has reasoning
                        return ChunkType.THINKING
                    else:
                        logger.debug(f"No thinking or content detected in {len(content_blocks)} content_blocks")
                        return ChunkType.UNKNOWN
                
                # Regular content (non-thinking models) or fallback for Gemini
                if hasattr(delta, 'content') and delta.content:
                    # GEMINI FALLBACK: Check if the content looks like thinking based on patterns
                    content_str = str(delta.content)
                    if self._is_gemini_thinking_content(content_str):
                        logger.debug(f"Detected Gemini thinking content via pattern matching")
                        return ChunkType.THINKING
                    else:
                        return ChunkType.CONTENT
            
            return ChunkType.UNKNOWN
            
        except Exception as e:
            logger.debug(f"Error determining chunk type from content_blocks: {e}")
            return ChunkType.UNKNOWN

    def _is_gemini_thinking_content(self, content: str) -> bool:
        """
        Detect if content from Gemini appears to be thinking/reasoning content.
        
        Gemini thinking models often use specific patterns in their reasoning.
        
        Args:
            content: The content string to analyze
            
        Returns:
            True if content appears to be thinking/reasoning content
        """
        if not content or not content.strip():
            return False
        
        content_lower = content.lower().strip()
        
        # Gemini thinking patterns (based on the logs)
        gemini_thinking_patterns = [
            # Headers with asterisks (common in thinking)
            "***", "**",
            # Explicit thinking phrases
            "i'm currently focused on", "i've been analyzing", "i am now",
            "i'm now", "i need to consider", "let me think", "let me analyze",
            "i should consider", "i'll now", "i'm leaning towards",
            # Process descriptions
            "structuring", "mapping", "defining", "analyzing", "outlining",
            "framing", "revising", "finalizing", "determining",
            # Gemini-specific thinking headers seen in logs
            "framing narrative", "mapping story", "structuring narrative",
            "defining arc", "analyzing story", "outlining arc", "revising story"
        ]
        
        # Check for thinking patterns
        for pattern in gemini_thinking_patterns:
            if pattern in content_lower:
                return True
        
        # Check for structured thinking with headers (like "**Framing Narrative Arcs**")
        if content.strip().startswith("**") and content.count("**") >= 2:
            return True
        
        # Check if it looks like a reasoning process (first-person analysis)
        first_person_reasoning = [
            "i'm", "i've", "i am", "i need", "i should", "i'll", "my focus", "my current"
        ]
        
        # If it contains first-person reasoning language, likely thinking
        first_person_count = sum(1 for phrase in first_person_reasoning if phrase in content_lower)
        if first_person_count >= 2:  # Multiple first-person reasoning phrases
            return True
        
        # Check if it contains JSON-like structured output (likely final content, not thinking)
        stripped_content = content.strip()
        if (stripped_content.startswith("{") and "}" in stripped_content) or \
           (stripped_content.startswith("[") and "]" in stripped_content):
            return False  # Structured output is content, not thinking
        
        return False

    def _extract_content_from_chunk(self, chunk: Any) -> str:
        """
        Extract content from a Portkey streaming chunk, handling both regular and thinking models.
        
        For thinking models, content is in content_blocks array with different types.
        We extract ALL content (both thinking and regular) and return it as a single string.
        The chunk type determination happens separately.
        
        Args:
            chunk: The streaming chunk from Portkey
            
        Returns:
            String content from the chunk
        """
        try:
            if (hasattr(chunk, 'choices') and chunk.choices and 
                hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta):
                
                delta = chunk.choices[0].delta
                
                # Check for content_blocks array (thinking models like Gemini, Anthropic)
                content_blocks = getattr(delta, 'content_blocks', None)
                if content_blocks:
                    # DEBUG: Log actual content_blocks structure for Anthropic (first few chunks only)
                    if not content_blocks or len(content_blocks) == 0:
                        logger.debug(f"Empty content_blocks array: {content_blocks}")
                    elif len(content_blocks) <= 3:  # Only log first few chunks to avoid spam
                        # Log structure of first content block for debugging
                        first_block = content_blocks[0]
                        if hasattr(first_block, '__dict__'):
                            logger.debug(f"Content block attributes: {list(first_block.__dict__.keys())}")
                        elif isinstance(first_block, dict):
                            logger.debug(f"Content block dict keys: {list(first_block.keys())}")
                        logger.debug(f"Content block type: {type(first_block)}, repr: {repr(first_block)}")
                    
                    # Extract content from all content blocks
                    content_parts = []
                    for content_block in content_blocks:
                        # Handle different content block structures
                        content_found = False
                        
                        # Try common Anthropic thinking field names
                        if hasattr(content_block, 'thinking') and content_block.thinking:
                            content_parts.append(str(content_block.thinking))
                            content_found = True
                        elif hasattr(content_block, 'text') and content_block.text:
                            content_parts.append(str(content_block.text))
                            content_found = True
                        elif hasattr(content_block, 'content') and content_block.content:
                            content_parts.append(str(content_block.content))
                            content_found = True
                        # Try additional Anthropic-specific fields
                        elif hasattr(content_block, 'delta') and content_block.delta:
                            if hasattr(content_block.delta, 'text') and content_block.delta.text:
                                content_parts.append(str(content_block.delta.text))
                                content_found = True
                            elif hasattr(content_block.delta, 'thinking') and content_block.delta.thinking:
                                content_parts.append(str(content_block.delta.thinking))
                                content_found = True
                        # Handle content_block as dict
                        elif isinstance(content_block, dict):
                            if 'thinking' in content_block and content_block['thinking']:
                                content_parts.append(str(content_block['thinking']))
                                content_found = True
                            elif 'text' in content_block and content_block['text']:
                                content_parts.append(str(content_block['text']))
                                content_found = True
                            elif 'content' in content_block and content_block['content']:
                                content_parts.append(str(content_block['content']))
                                content_found = True
                            elif 'delta' in content_block and content_block['delta']:
                                delta = content_block['delta']
                                if isinstance(delta, dict):
                                    if 'text' in delta and delta['text']:
                                        content_parts.append(str(delta['text']))
                                        content_found = True
                                    elif 'thinking' in delta and delta['thinking']:
                                        content_parts.append(str(delta['thinking']))
                                        content_found = True
                        
                        if not content_found:
                            # DEBUG: Log unhandled content block structure (limit spam)
                            logger.debug(f"Unhandled content block: type={type(content_block)}, "
                                        f"is_dict={isinstance(content_block, dict)}, "
                                        f"repr={repr(content_block)[:100]}...")
                    
                    if content_parts:
                        return ''.join(content_parts)
                    else:
                        # DEBUG: Log when no content was extracted
                        logger.debug(f"No content extracted from {len(content_blocks)} content_blocks")
                        return ""
                
                # Try additional fallback patterns for Anthropic thinking mode
                # Check for direct delta fields that might contain thinking/content
                if hasattr(delta, 'thinking') and delta.thinking:
                    logger.debug(f"Found thinking content in delta.thinking: {len(str(delta.thinking))} chars")
                    return str(delta.thinking)
                elif hasattr(delta, 'text') and delta.text:
                    logger.debug(f"Found content in delta.text: {len(str(delta.text))} chars")
                    return str(delta.text)
                
                # Regular content (non-thinking models)
                if hasattr(delta, 'content') and delta.content:
                    return str(delta.content)
                
                # DEBUG: Log when no content sources found (once per stream)
                has_content_blocks = content_blocks is not None
                has_regular_content = hasattr(delta, 'content') and delta.content
                logger.debug(f"No content found: has_content_blocks={has_content_blocks}, "
                           f"has_regular_content={has_regular_content}")
            
            return ""
            
        except Exception as e:
            logger.debug(f"Error extracting content from chunk: {e}")
            return ""

    def _determine_chunk_type(self, content: str, provider: str, model: str, chunk_metadata: Optional[Dict[str, Any]] = None) -> ChunkType:
        """
        Legacy method for determining chunk type from content analysis.
        
        Note: This method is deprecated in favor of _determine_chunk_type_from_content_blocks
        which uses Portkey's built-in content_blocks structure for thinking models.
        
        Args:
            content: The content of the chunk
            provider: The LLM provider
            model: The model name
            chunk_metadata: Optional metadata from the chunk
            
        Returns:
            ChunkType indicating whether this is thinking or content
        """
        if not content or not content.strip():
            return ChunkType.UNKNOWN
        
        # Provider-specific detection patterns
        if provider.lower() == "anthropic":
            # Anthropic thinking mode uses <thinking> tags
            if content.strip().startswith("<thinking>") or "</thinking>" in content or "<thinking>" in content:
                return ChunkType.THINKING
        
        elif provider.lower() == "openai":
            # OpenAI reasoning models (o1 series) might have reasoning metadata
            # Check if this is from a reasoning model
            if "o1" in model.lower():
                # For o1 models, check if chunk metadata indicates reasoning
                if chunk_metadata and chunk_metadata.get("reasoning"):
                    return ChunkType.THINKING
        
        # Default patterns for thinking content across providers
        thinking_indicators = [
            "let me think", "i need to consider", "thinking about", 
            "let me analyze", "i should consider", "reasoning:",
            "thought process:", "analysis:", "let me break this down"
        ]
        
        content_lower = content.lower()
        if any(indicator in content_lower for indicator in thinking_indicators):
            return ChunkType.THINKING
        
        # Check for JSON-like content (likely structured output)
        stripped_content = content.strip()
        if (stripped_content.startswith("{") and stripped_content.endswith("}")) or \
           (stripped_content.startswith("[") and stripped_content.endswith("]")):
            return ChunkType.CONTENT
        
        # Default to content for most cases
        return ChunkType.CONTENT

    async def chat_completion(
        self,
        provider: str, # The provider ID (e.g., 'openai')
        model: str,    # The exact hosted model name (e.g., 'gpt-4o', 'claude-3-opus-20240229')
        messages: List[LLMMessage],
        user_id: Optional[UUID] = None,  # Optional when using direct API key
        api_key: Optional[str] = None,   # Optional direct API key (bypasses database)
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        thinking: Optional[ThinkingEffort] = None,  # NEW: Thinking effort parameter
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
            thinking: Thinking effort for models that support thinking modes
            trace_id: Optional trace ID for debugging
            metadata: Optional metadata for the request
            stream: Whether to return a stream of responses
            response_format: Optional pydantic model type for structured output
            **kwargs: Additional parameters for the LLM
                     For thinking/reasoning models (e.g., claude-3-7-sonnet-latest), 
                     include thinking={type: "enabled", budget_tokens: 2030} and
                     set strict_open_ai_compliance=False in Portkey client
            
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
            
            # Streaming usage with thinking
            async for chunk in await llm_service.chat_completion(
                provider="anthropic", 
                model="claude-3-5-sonnet-20241022",
                messages=[LLMMessage(role="user", content="Complex problem")],
                user_id=user_id,
                thinking=ThinkingEffort.HIGH,
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
            
            # Set strict_open_ai_compliance=False for thinking models (required by Portkey)
            if thinking is not None:
                portkey_options["strict_open_ai_compliance"] = False
                logger.info(f"Set strict_open_ai_compliance=False for thinking mode")
            
            # Add optional configurations
            if trace_id:
                portkey_options["trace_id"] = trace_id
            
            # Validate temperature support for this model
            temp_warning = get_temperature_restriction_message(provider, model, False, temperature)
            if temp_warning:
                logger.warning(temp_warning)
            
            final_metadata = { 
                "shuscribe_version": "0.1.0",
                "auth_method": "direct_api_key" if api_key else "database_lookup",
                "streaming": stream
            }
            if user_id:
                final_metadata["user_id"] = str(user_id)
            if thinking:
                final_metadata["thinking_effort"] = thinking.value
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
                "stream": stream,
                **kwargs,
            }
            
            # Handle temperature based on model support and thinking mode
            if thinking is not None and provider.lower() == "anthropic":
                # Anthropic requires temperature=1.0 when thinking is enabled
                create_kwargs["temperature"] = 1.0
                if temperature != 1.0:
                    logger.info(f"Overriding temperature to 1.0 for Anthropic thinking mode (was {temperature})")
            elif model_supports_temperature(provider, model, thinking is not None):
                create_kwargs["temperature"] = temperature
            
            # Handle thinking effort parameter first (may need to adjust max_tokens)
            adjusted_max_tokens = max_tokens
            if thinking is not None:
                # Use unified method to handle all thinking preparation
                adjusted_max_tokens, thinking_params = self._prepare_thinking_parameters(
                    thinking, provider, model, max_tokens
                )
                
                # Add thinking parameters to request if they were created
                if thinking_params is not None:
                    create_kwargs["thinking"] = thinking_params

            # Handle max_tokens parameter (OpenAI reasoning models use max_completion_tokens)
            if adjusted_max_tokens is not None:
                if should_use_completion_tokens_param(provider, model):
                    create_kwargs["max_completion_tokens"] = adjusted_max_tokens
                    logger.info(f"Using max_completion_tokens={adjusted_max_tokens} for OpenAI reasoning model {model}")
                else:
                    create_kwargs["max_tokens"] = adjusted_max_tokens

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
                # Extract content and determine chunk type using Portkey's content_blocks structure
                content, chunk_type = self._extract_content_from_non_streaming_response(response)
                
                return LLMResponse(
                    content=content,
                    model=response.model, # type: ignore
                    chunk_type=chunk_type,
                    usage=response.usage.model_dump() if response.usage else None, # type: ignore
                    metadata={
                        "provider": provider,
                        "gateway": "self-hosted",
                        "portkey_request_id": getattr(response, 'id', None),
                        "trace_id": trace_id,
                        "auth_method": "direct_api_key" if api_key else "database_lookup",
                        "streaming": False,
                        "thinking_effort": thinking.value if thinking else None
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
                "streaming": stream,
                "thinking_effort": thinking.value if thinking else None
            })
            raise LLMError(
                provider=f"portkey-self-hosted/{provider}",
                message=f"An error occurred during LLM call: {e}",
                details={
                    "model": model,
                    "provider": provider,
                    "user_id": str(user_id) if user_id else "direct_api_key",
                    "streaming": stream,
                    "thinking_effort": thinking.value if thinking else None
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
        different LLM providers. It properly handles both regular and thinking models
        using Portkey's content_blocks structure.
        
        Args:
            portkey_stream_response: Streaming response from Portkey
            provider: Provider ID for metadata
            trace_id: Optional trace ID for debugging
            
        Yields:
            LLMResponse objects with incremental content
        """
        async for chunk in portkey_stream_response:
            # Use Portkey's content_blocks structure for proper chunk handling
            content = self._extract_content_from_chunk(chunk)
            chunk_type = self._determine_chunk_type_from_content_blocks(chunk)
            
            yield LLMResponse(
                content=content,
                model=chunk.model, # type: ignore
                chunk_type=chunk_type,
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

    def _extract_content_from_non_streaming_response(self, response: Any) -> tuple[str, ChunkType]:
        """
        Extract content and determine chunk type from a non-streaming Portkey response.
        
        Args:
            response: The complete response from Portkey
            
        Returns:
            Tuple of (content, chunk_type)
        """
        try:
            # Check if this is a thinking model response with content blocks
            if (hasattr(response, 'choices') and response.choices and 
                hasattr(response.choices[0], 'message') and response.choices[0].message):
                
                message = response.choices[0].message
                
                # Check for content_blocks array (thinking models)
                content_blocks = getattr(message, 'content_blocks', None)
                if content_blocks:
                    # Extract content from all content blocks
                    content_parts = []
                    has_thinking = False
                    has_content = False
                    
                    for content_block in content_blocks:
                        # Handle explicit type field
                        if hasattr(content_block, 'type'):
                            if content_block.type == 'thinking':
                                has_thinking = True
                                if hasattr(content_block, 'thinking') and content_block.thinking:
                                    content_parts.append(str(content_block.thinking))
                            elif content_block.type in ['text', 'content']:
                                has_content = True
                                if hasattr(content_block, 'text') and content_block.text:
                                    content_parts.append(str(content_block.text))
                                elif hasattr(content_block, 'content') and content_block.content:
                                    content_parts.append(str(content_block.content))
                        # Handle thinking field presence
                        elif hasattr(content_block, 'thinking') and content_block.thinking:
                            has_thinking = True
                            content_parts.append(str(content_block.thinking))
                        elif hasattr(content_block, 'text') and content_block.text:
                            has_content = True
                            content_parts.append(str(content_block.text))
                        elif hasattr(content_block, 'content') and content_block.content:
                            has_content = True
                            content_parts.append(str(content_block.content))
                        # Handle dict structure
                        elif isinstance(content_block, dict):
                            if 'type' in content_block:
                                if content_block['type'] == 'thinking':
                                    has_thinking = True
                                    if 'thinking' in content_block and content_block['thinking']:
                                        content_parts.append(str(content_block['thinking']))
                                elif content_block['type'] in ['text', 'content']:
                                    has_content = True
                                    if 'text' in content_block and content_block['text']:
                                        content_parts.append(str(content_block['text']))
                                    elif 'content' in content_block and content_block['content']:
                                        content_parts.append(str(content_block['content']))
                            elif 'thinking' in content_block and content_block['thinking']:
                                has_thinking = True
                                content_parts.append(str(content_block['thinking']))
                            elif 'text' in content_block and content_block['text']:
                                has_content = True
                                content_parts.append(str(content_block['text']))
                            elif 'content' in content_block and content_block['content']:
                                has_content = True
                                content_parts.append(str(content_block['content']))
                    
                    content = ''.join(content_parts)
                    
                    # Determine chunk type based on what we found
                    if has_thinking and not has_content:
                        chunk_type = ChunkType.THINKING
                    elif has_content and not has_thinking:
                        chunk_type = ChunkType.CONTENT
                    elif has_thinking and has_content:
                        # Mixed content - return CONTENT for final response (thinking + content combined)
                        chunk_type = ChunkType.CONTENT
                    else:
                        chunk_type = ChunkType.UNKNOWN
                    
                    return content, chunk_type
                
                # Regular content (non-thinking models)
                if hasattr(message, 'content') and message.content:
                    content = str(message.content)
                    return content, ChunkType.CONTENT
            
            return "", ChunkType.UNKNOWN
            
        except Exception as e:
            logger.debug(f"Error extracting content from non-streaming response: {e}")
            return "", ChunkType.UNKNOWN