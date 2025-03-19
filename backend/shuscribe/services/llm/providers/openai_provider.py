# shuscribe/services/llm/providers/openai_provider.py

import logging
import os
import traceback
from typing import Any, AsyncGenerator, Dict, List, Optional

from openai import AsyncOpenAI, AsyncStream
from openai.types.responses.response import Response as OpenAIResponse
from openai.types.responses.response_stream_event import ResponseStreamEvent as OpenAIResponseStreamEvent

from shuscribe.services.llm.errors import ErrorCategory, LLMProviderException
from shuscribe.schemas.llm import Message, GenerationConfig, Capabilities
from shuscribe.services.llm.providers.provider import (
    LLMProvider, 
    LLMResponse, 
)

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    """
    OpenAI provider implementation using the official OpenAI Python client.
    Uses async client exclusively.
    Updated to use the Responses API instead of Chat Completions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI provider with the given API key.
        
        Args:
            api_key: OpenAI API key. If None, will try to use from environment.
        """
        super().__init__(api_key=api_key)
    
    def _initialize_client(self) -> AsyncOpenAI:
        """Initialize the OpenAI client"""
        # Use the provided API key or fall back to environment variable
        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            logger.warning("No OpenAI API key provided. Client will fail on API calls.")
        
        # Initialize only the async client
        # __init__ will set self._client
        return AsyncOpenAI(api_key=api_key)
    
    @property
    def client(self) -> AsyncOpenAI:
        """Get the OpenAI client"""
        if self._client is None:
            raise ValueError("Client not initialized")
        return self._client
    
    def capabilities(self) -> Capabilities:
        """
        Get the provider capabilities
        """
        
        return Capabilities(
            streaming=True,
            structured_output=True,
            thinking=True, # TODO: add thinking
            tool_calling=True, # TODO: add tool calling
            parallel_tool_calls=True, # TODO: add parallel tool calls
            citations=True, # TODO: add citations
            caching=True, # TODO: add caching
            search=True, # TODO: add search
        )
    
    def _map_to_openai_messages(self, messages: List[Message | str]) -> List[Dict[str, Any]]:
        """
        Map our internal Message objects to OpenAI message format
        """
        openai_messages = []
        
        for msg in messages:
            if isinstance(msg, Message):
                message_dict = {
                    "role": msg.role,
                    "content": msg.content
                }
            elif isinstance(msg, str):
                message_dict = {
                    "role": "user",
                    "content": msg
                }
            
            if isinstance(msg, Message) and msg.name:
                message_dict["name"] = msg.name
                
            openai_messages.append(message_dict)
            
        return openai_messages
    
    def _prepare_config(
        self,
        messages: List[Message | str],
        model: str,
        config: Optional[GenerationConfig] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Prepare the configuration dictionary for the OpenAI API call.
        """
        # Set default config if none provided
        config = config or GenerationConfig()
        
        # Map internal messages to OpenAI format
        openai_messages = self._map_to_openai_messages(messages)
        
        # Prepare request parameters for the Responses API
        # The input should be a list of messages directly, not wrapped in an object
        params = {
            "model": model,
            "input": openai_messages,  # Direct list of messages as input
            "temperature": config.temperature,
            "top_p": config.top_p,
        }
        
        # Add max_tokens if specified
        if config.max_tokens is not None:
            params["max_output_tokens"] = config.max_tokens
            
        if stream:
            params["stream"] = True
        
        # Add system prompt if provided and not already in messages
        if config.system_prompt:
            params["input"].insert(0, {"role": "system", "content": config.system_prompt})
        
        # Add tools if specified
        if config.tools:
            tools = []
            for tool in config.tools:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    }
                })
            params["tools"] = tools
            
            if config.tool_choice:
                params["tool_choice"] = config.tool_choice
        
        # Add stop sequences if specified
        if config.stop_sequences:
            params["stop"] = config.stop_sequences
        
        # Add search capability if specified
        if config.search:
            params["tools"] = params.get("tools", [])
            params["tools"].append({
                "type": "web_search"
            })
        
        # Add response format configuration for structured output
        if config.response_schema:
            schema = config.response_schema.model_json_schema()
            schema["additionalProperties"] = False
            params["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": config.response_schema.__name__,
                    "schema": schema,
                    "strict": True
                }
            }
        
        if config.thinking_config and config.thinking_config.enabled:
            params["reasoning"] = {"effort": config.thinking_config.effort}
            # NOTE: TEMPERATURE IS NOT AVAILABLE FOR THINKING MODELS
            del params["temperature"]
        
        return params
    
    async def _generate_internal(
        self, 
        messages: List[Message | str],
        model: str,
        config: Optional[GenerationConfig] = None
    ) -> LLMResponse:
        """
        Generate a text completion response from OpenAI using the Responses API
        """
        try:
            # Set default config if none provided
            config = config or GenerationConfig()
            
            params = self._prepare_config(messages=messages, model=model, config=config)
            
            # Make the API call to the responses endpoint
            response: OpenAIResponse = await self.client.responses.create(**params)
            
            # Extract response information (content from the output)
            content = response.output_text
                            
            # Create and return the LLMResponse
            return LLMResponse(
                text=content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.input_tokens if response.usage else 0,
                    "completion_tokens": response.usage.output_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                raw_response=response,
            )
            
        except Exception as e:
            # Let the error propagate to be handled by the LLM session manager
            logger.error(f"OpenAI Responses API error: {str(e)}")
            raise self._handle_provider_error(e)
    
    async def _stream_generate(
        self, 
        messages: List[Message | str],
        model: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a text completion response from OpenAI using Responses API
        """
        # Set default config if none provided
        config = config or GenerationConfig()
        
        params = self._prepare_config(messages=messages, model=model, config=config, stream=True)
        
        # Make the streaming API call using the responses endpoint
        try:
            # Create the stream - this returns a coroutine that needs to be awaited
            stream: AsyncStream[OpenAIResponseStreamEvent] = await self.client.responses.create(**params)
            
            # Process the streamed chunks from the responses API
            # https://platform.openai.com/docs/guides/streaming-responses?api-mode=responses
            async for chunk in stream:
                if chunk.type == "response.output_text.delta":
                    yield chunk.delta
                    
        except Exception as e:
            logger.error(f"OpenAI Responses API streaming error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise self._handle_provider_error(e)
    
    
    def _handle_provider_error(self, exception: Exception) -> LLMProviderException:
        """
        Convert provider-specific exceptions to our exception types
        Must be implemented by each provider
        """
        # TODO: be more specific about OpenAI errors
        return LLMProviderException(
            message=str(exception),
            code="openai_provider_error",
            category=ErrorCategory.UNKNOWN,
            provider=self.__class__.__name__
        )
    
    async def close(self):
        """Close the client and release resources"""
        # The OpenAI client doesn't have explicit close methods,
        # but we can help garbage collection by removing references
        self._client = None
        
        # Call parent close method to handle stream manager cleanup
        await super().close()