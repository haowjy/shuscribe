# shuscribe/services/llm/providers/anthropic_provider.py

import json
import logging
import os
import traceback
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

import anthropic
from anthropic import AsyncAnthropic, AsyncStream
from anthropic.types import MessageParam
from anthropic.types.message import Message as AnthropicMessage
from anthropic.types.message_stream_event import MessageStreamEvent as AnthropicMessageStreamEvent
from anthropic.types.raw_content_block_delta_event import RawContentBlockDeltaEvent as AnthropicContentBlockDeltaEvent
from anthropic.types.text_delta import TextDelta as AnthropicTextDelta
from anthropic.types.thinking_delta import ThinkingDelta as AnthropicThinkingDelta
from shuscribe.services.llm.errors import ErrorCategory, LLMProviderException
from shuscribe.schemas.llm import Message, MessageRole, GenerationConfig
from shuscribe.schemas.provider import LLMResponse, LLMUsage
from shuscribe.services.llm.providers.provider import (
    LLMProvider,
)
from shuscribe.schemas.streaming import StreamEvent

logger = logging.getLogger(__name__)

class AnthropicProvider(LLMProvider):
    """
    Anthropic provider implementation using the official Anthropic Python client.
    Uses async client exclusively for compatibility with the system architecture.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Anthropic provider with the given API key.
        
        Args:
            api_key: Anthropic API key. If None, will try to use from environment.
        """
        super().__init__(api_key=api_key)
    
    def _initialize_client(self) -> AsyncAnthropic:
        """Initialize the Anthropic client"""
        # Use the provided API key or fall back to environment variable
        api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        if not api_key:
            logger.warning("No Anthropic API key provided. Client will fail on API calls.")
        
        # Initialize the async client
        return AsyncAnthropic(api_key=api_key)
    
    @property
    def client(self) -> AsyncAnthropic:
        """Get the Anthropic client"""
        if self._client is None:
            raise ValueError("Client not initialized")
        return self._client
    
    def capabilities(self) -> Dict[str, bool]:
        """
        Get the provider capabilities
        """
        return {
            "streaming": True,
            "structured_output": False, # Not a true structured output
            "thinking": False,  # TODO: Claude supports a thinking process via system prompt
            "tool_calling": False,  # TODO: Claude supports tools
            "parallel_tool_calls": False,  # Not currently available
            "citations": False,  # TODO: Claude can provide citations in its responses
            "caching": False,  # TODO: Not yet implemented
            "search": False,  # Not currently available
        }
    
    def _map_to_anthropic_messages(self, messages: List[Message | str]) -> Tuple[List[MessageParam], str]:
        """
        Map our internal Message objects to Anthropic message format
        """
        anthropic_messages = []
        anthropic_system_message = []
        
        for msg in messages:
            if isinstance(msg, str):
                # Convert string to user message
                anthropic_messages.append({
                    "role": "user",
                    "content": msg
                })
            elif isinstance(msg, Message):
                # Convert our Message object to Anthropic format
                if msg.role == MessageRole.SYSTEM:
                    # System messages are handled differently in Anthropic
                    anthropic_system_message.append(msg.content)
                    continue  # Will be handled separately as system parameter
                
                # Map role (Claude uses user/assistant/tool)
                anthropic_messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        return anthropic_messages, "\n".join(anthropic_system_message)
    
    def _prepare_anthropic_params(
        self,
        messages: List[Message | str],
        model: str,
        config: Optional[GenerationConfig] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Prepare parameters for Anthropic API calls, ensuring all required parameters
        are included with appropriate defaults.
        
        Args:
            messages: The messages to send
            model: The model to use
            config: Generation configuration
            stream: Whether to enable streaming
            
        Returns:
            Dictionary of parameters for the Anthropic API
        """
        # Set default config if none provided
        config = config or GenerationConfig()
        
        # Map internal messages to Anthropic format
        anthropic_messages, system_prompt = self._map_to_anthropic_messages(messages)
        
        # Extract system prompt from messages or use from config
        if config.system_prompt:
            system_prompt += config.system_prompt
        
        # Add a mock response schema if specified
        if config.response_schema:
            response_schema_str = config.response_schema.to_output_schema_str()
            system_prompt += f"\n\nThe response should be in the following JSON format: ```json\n{response_schema_str}\n```"
            
        # Prepare request parameters with appropriate defaults
        params = {
            "model": model,
            "messages": anthropic_messages,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "max_tokens": config.max_output_tokens or 4096,  # Default to 4096 if not specified
        }
        
        # Add streaming if requested
        if stream:
            params["stream"] = True
            
        # Add system prompt if provided
        if system_prompt:
            params["system"] = system_prompt
        
        # Add stop sequences if specified
        if config.stop_sequences:
            params["stop_sequences"] = config.stop_sequences
        
        # # Add tools if specified
        # if config.tools:
        #     tools = []
        #     for tool in config.tools:
        #         tools.append({
        #             "name": tool.name,
        #             "description": tool.description,
        #             "input_schema": tool.parameters,
        #         })
        #     params["tools"] = tools
        
        # add reasoning if specified
        if config.thinking_config and config.thinking_config.enabled:
            params["thinking"] = {"type": "enabled", "budget_tokens": config.thinking_config.budget_tokens}
            params["temperature"] = 1 # NOTE: TEMPERATURE IS NOT AVAILABLE FOR THINKING MODELS
            del params["top_p"]
            # params["betas"] = ["output-128k-2025-02-19"] # ?
            
        return params
    
    async def _generate_internal(
        self, 
        messages: List[Message | str],
        model: str,
        config: Optional[GenerationConfig] = None
    ) -> LLMResponse:
        """Generate a text completion response from Anthropic"""
        try:
            # Prepare parameters
            params = self._prepare_anthropic_params(
                messages=messages,
                model=model,
                config=config,
                stream=False
            )
            
            # Make the API call
            response: AnthropicMessage = await self.client.messages.create(**params)
            
            # Extract response information
            content = ""
            tool_calls = []
            
            for block in response.content:
                if block.type == "text":
                    content += block.text
                elif block.type == "tool_use":
                    # Extract tool use information from content blocks
                    tool_calls.append({
                        "id": block.id if hasattr(block, 'id') else f"tool_{len(tool_calls)}",
                        "name": block.name,
                        "input": block.input,
                    })
            
            # Create and return the LLMResponse
            return LLMResponse(
                text=content,
                model=response.model,
                usage=LLMUsage(
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                ),
                raw_response=response,
                tool_calls=tool_calls if tool_calls else None
            )
            
        except Exception as e:
            # Let the error propagate to be handled by the LLM session manager
            logger.error(f"Anthropic API error: {str(e)}")
            raise self._handle_provider_error(e)
    
    async def _stream_generate(
        self, 
        messages: List[Message | str],
        model: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream a text completion response from Anthropic"""
        try:
            # Prepare parameters with streaming enabled
            params = self._prepare_anthropic_params(
                messages=messages,
                model=model,
                config=config
            )
            
            # Process the streamed chunks
            async with self.client.messages.stream(**params) as stream:
                is_thinking = False
                
                async for event in stream:
                    if isinstance(event, AnthropicContentBlockDeltaEvent):
                        delta = event.delta
                        
                        if isinstance(delta, AnthropicThinkingDelta):
                            thinking_text = delta.thinking
                            if not is_thinking:
                                thinking_text = "<ANTHROPIC_THINKING>" + thinking_text
                            yield StreamEvent(
                                type="in_progress",
                                text=thinking_text,
                            )
                            is_thinking = True
                            
                        if isinstance(delta, AnthropicTextDelta):
                            if is_thinking:
                                yield StreamEvent(
                                    type="in_progress",
                                    text="</ANTHROPIC_THINKING>",
                                )
                                is_thinking = False
                            yield StreamEvent(
                                type="in_progress",
                                text=delta.text,
                            )

            message: AnthropicMessage = await stream.get_final_message()
            yield StreamEvent(
                type="complete",
                text="",
                usage=LLMUsage(
                    prompt_tokens=message.usage.input_tokens,
                    completion_tokens=message.usage.output_tokens,
                ),
            )
            
        except Exception as e:
            logger.error(f"Anthropic API streaming error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise self._handle_provider_error(e)
        
    def _handle_provider_error(self, exception: Exception) -> LLMProviderException:
        """
        Convert Anthropic-specific exceptions to our exception types
        """
        error_message = str(exception)
        error_code = "anthropic_error"
        category = ErrorCategory.UNKNOWN
        retry_after = None
        
        if isinstance(exception, anthropic.RateLimitError):
            category = ErrorCategory.RATE_LIMIT
            error_code = "rate_limit_exceeded"
            
            # Try to extract retry-after from response property if it exists
            if hasattr(exception, 'response') and hasattr(exception.response, 'headers'):
                retry_header = exception.response.headers.get('retry-after')
                if retry_header:
                    try:
                        retry_after = float(retry_header)
                    except (ValueError, TypeError):
                        retry_after = None
        
        elif isinstance(exception, anthropic.APIStatusError):
            status_code = getattr(exception, 'status_code', None)
            
            if status_code:
                if status_code == 400:
                    category = ErrorCategory.INVALID_REQUEST
                    error_code = "bad_request"
                elif status_code == 401:
                    category = ErrorCategory.AUTHENTICATION
                    error_code = "unauthorized"
                elif status_code == 403:
                    category = ErrorCategory.AUTHENTICATION
                    error_code = "forbidden"
                elif status_code == 404:
                    category = ErrorCategory.INVALID_REQUEST
                    error_code = "not_found"
                elif status_code == 429:
                    category = ErrorCategory.RATE_LIMIT
                    error_code = "rate_limit_exceeded"
                    
                    # Try to extract retry-after if available
                    if hasattr(exception, 'response') and hasattr(exception.response, 'headers'):
                        retry_header = exception.response.headers.get('retry-after')
                        if retry_header:
                            try:
                                retry_after = float(retry_header)
                            except (ValueError, TypeError):
                                retry_after = None
                elif status_code == 500:
                    category = ErrorCategory.SERVICE_ERROR
                    error_code = "internal_server_error"
                elif status_code == 503:
                    category = ErrorCategory.SERVICE_ERROR
                    error_code = "service_unavailable" 
                elif status_code == 529:
                    category = ErrorCategory.SERVICE_ERROR
                    error_code = "overloaded_error"
                    
        elif isinstance(exception, anthropic.APITimeoutError):
            category = ErrorCategory.NETWORK_ERROR
            error_code = "request_timeout"
        
        elif isinstance(exception, anthropic.APIConnectionError):
            category = ErrorCategory.NETWORK_ERROR
            error_code = "connection_error"
            
        return LLMProviderException(
            message=error_message,
            code=error_code,
            category=category,
            provider=self.__class__.__name__,
            retry_after=retry_after,
            raw_error=exception
        )
    
     
    async def close(self):
        """Close the client and release resources"""
        # The Anthropic client doesn't have explicit close methods,
        # but we can help garbage collection by removing references
        self._client = None
        
        # Call parent close method to handle stream manager cleanup
        await super().close()