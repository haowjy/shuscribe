# shuscribe/services/llm/providers/gemini_provider.py

import logging
import os
import traceback
from typing import Any, AsyncGenerator, List, Optional, Sequence, Tuple

from google import genai
from google.genai import types as genai_types

from shuscribe.schemas.streaming import StreamEvent
from shuscribe.services.llm.errors import ErrorCategory, LLMProviderException
from shuscribe.schemas.llm import Message, MessageRole, GenerationConfig, Capabilities # ToolDefinition, ToolType, 
from shuscribe.schemas.provider import LLMResponse, LLMUsage
from shuscribe.services.llm.providers.provider import (
    LLMProvider, 
)

logger = logging.getLogger(__name__)

class GeminiProvider(LLMProvider):
    """
    Google Gemini provider implementation using the new Google GenAI SDK.
    Uses async methods exclusively for compatibility with the system architecture.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini provider with the given API key.
        
        Args:
            api_key: Google Gemini API key. If None, will try to use from environment.
        """
        super().__init__(api_key=api_key)
    
    def _initialize_client(self) -> Any:
        """
        Initialize the Gemini client and configure the API key
        """
        # Use the provided API key or fall back to environment variable
        api_key = self.api_key or os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            logger.warning("No Google Gemini API key provided. Client will fail on API calls.")
        
        # Create a client with the API key
        return genai.Client(api_key=api_key)
    
    @property
    def client(self) -> genai.Client:
        """Get the Gemini client"""
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
            thinking=False, # TODO: add thinking
            tool_calling=True, # TODO: don't know if this works atm
            parallel_tool_calls=True, # TODO: don't know if this works atm
            citations=True, # TODO: don't know if this works atm
            caching=True, # TODO: don't know if this works atm
            search=True, # TODO: don't know if this works atm
        )
    
    def _prepare_content(self, messages: List[Message | str]) -> Tuple[Any, Optional[str]]:
        """
        Convert our messages to Gemini's format.
        Returns a tuple of (contents, system_instruction) where:
        - contents is properly formatted for the SDK's ContentListUnion | ContentListUnionDict types
        - system_instruction is extracted from system messages
        
        The contents will be formatted as:
        - A single string for simple text queries
        - A dictionary with 'role' and 'parts' for a single message with role
        - A list of dictionaries for multiple messages
        """
        system_messages = []
        
        # Special case for a single string message
        if len(messages) == 1 and isinstance(messages[0], str):
            return messages[0], None
        
        # Process messages into the format expected by the SDK
        gemini_contents = []
        
        for msg in messages:
            if isinstance(msg, str):
                # For a simple string, create a user message
                gemini_contents.append({
                    "role": "user",
                    "parts": [{"text": msg}]
                })
            elif isinstance(msg, Message):
                # Handle system messages separately
                if msg.role == MessageRole.SYSTEM:
                    system_messages.append(msg.content)
                    continue
                    
                # Map role (Gemini uses user/model)
                gemini_role = "user"
                if msg.role == MessageRole.ASSISTANT:
                    gemini_role = "model"
                elif msg.role == MessageRole.TOOL:
                    gemini_role = "function"  # This may need adjustment
                
                # Process content based on type
                parts = []
                
                if isinstance(msg.content, str):
                    # Simple text content
                    parts.append({"text": msg.content})
                elif isinstance(msg.content, list):
                    # List of content elements
                    for item in msg.content:
                        if isinstance(item, str):
                            # Text content
                            parts.append({"text": item})
                        elif hasattr(item, 'type') and hasattr(item, 'data'):
                            # Structured content object
                            if item.type == "text":
                                parts.append({"text": item.data})
                            # elif item.type == "image":
                            #     # Handle image data
                            #     # This would need appropriate conversion for Gemini API
                            #     try:
                            #         import PIL.Image
                            #         # If it's a PIL Image
                            #         if isinstance(item.data, PIL.Image.Image):
                            #             parts.append(item.data)  # SDK should accept PIL images directly
                            #         # If it's a URL
                            #         elif isinstance(item.data, str) and (
                            #             item.data.startswith("http://") or item.data.startswith("https://")
                            #         ):
                            #             # Make sure we have requests
                            #             import requests
                            #             # Fetch the image
                            #             response = requests.get(item.data, stream=True)
                            #             response.raise_for_status()
                            #             # Convert to PIL Image
                            #             img = PIL.Image.open(response.raw)
                            #             parts.append(img)
                            #         else:
                            #             # Try to treat as inline data
                            #             parts.append({
                            #                 "inline_data": {
                            #                     "mime_type": item.mime_type or "image/jpeg",
                            #                     "data": item.data
                            #                 }
                            #             })
                            #     except (ImportError, Exception) as e:
                            #         logger.warning(f"Failed to process image: {str(e)}")
                            #         # Fallback to text
                            #         parts.append({"text": f"[Image: {str(item.data)}]"})
                else:
                    # Default to treating unknown content as text
                    parts.append({"text": str(msg.content)})
                    
                gemini_contents.append({
                    "role": gemini_role,
                    "parts": parts
                })
        
        # Combine any system messages
        system_instruction = "\n".join(system_messages) if system_messages else None
        
        # Handle the case where we have only one user message with a simple text part
        if len(gemini_contents) == 1 and gemini_contents[0]["role"] == "user" and len(gemini_contents[0]["parts"]) == 1:
            if isinstance(gemini_contents[0]["parts"][0], dict) and "text" in gemini_contents[0]["parts"][0]:
                # The SDK can accept a simple string for a single user message
                return gemini_contents[0]["parts"][0]["text"], system_instruction
        
        # Return the properly formatted content
        return gemini_contents, system_instruction
    
    # def _map_generic_tools_to_gemini(self, tools: List[ToolDefinition]) -> List[genai_types.Tool]:
    #     """Map our generic tool definitions to Gemini-specific format"""
    #     gemini_tools = []
        
    #     for tool in tools:
    #         if tool.type == ToolType.FUNCTION:
    #             # Map function tool
    #             gemini_tools.append({
    #                 "function_declarations": [{
    #                     "name": tool.name,
    #                     "description": tool.description,
    #                     "parameters": tool.parameters
    #                 }]
    #             })
    #         elif tool.type == ToolType.SEARCH:
    #             # Map search tool
    #             gemini_tools.append({"google_search": {}})
    #         elif tool.type == ToolType.CODE_EXECUTION:
    #             # Map code execution tool
    #             config = {}
    #             if tool.code_execution_config:
    #                 if tool.code_execution_config.timeout:
    #                     config["timeout"] = tool.code_execution_config.timeout
    #             gemini_tools.append({"code_execution": config})
        
    #     return gemini_tools
    
    def _prepare_config(self, config: GenerationConfig, system_instruction: Optional[str] = None) -> genai_types.GenerateContentConfig:
        """
        Convert our generic GenerationConfig to Gemini-specific parameters
        """
        gemini_config = genai_types.GenerateContentConfig()
        
        # Add system instruction if provided
        if system_instruction:
            gemini_config.system_instruction = system_instruction
            
        # Add basic generation parameters
        if config.temperature is not None:
            gemini_config.temperature = config.temperature
        if config.top_p is not None:
            gemini_config.top_p = config.top_p
        if config.top_k is not None:
            gemini_config.top_k = config.top_k
        if config.max_output_tokens is not None:
            gemini_config.max_output_tokens = config.max_output_tokens
        if config.stop_sequences:
            gemini_config.stop_sequences = config.stop_sequences
        
        # Add response schema for structured output
        if config.response_schema:
            if config.thinking_config and config.thinking_config.enabled: # NOTE: Gemini doesn't support thinking + structured output yet
                response_schema_str = config.response_schema.to_output_schema_str()
                gemini_config.system_instruction = f"{gemini_config.system_instruction}\n\nThe full response should be in the **SINGLE** (1 json block) following JSON schema: ```json\n{response_schema_str}\n```"
            else:
                gemini_config.response_mime_type = "application/json"
                gemini_config.response_schema = config.response_schema
            
        # Handle context/caching ID
        if config.context_id:
            gemini_config.cached_content = config.context_id
        
        # TODO: add tools
        # # Convert our generic tool definitions to Gemini-specific format
        # if config.tools:
        #     gemini_config.tools = self._map_generic_tools_to_gemini(config.tools)
            
        #     # Handle tool_choice if specified
        #     if config.tool_choice:
        #         gemini_config.tool_choice = config.tool_choice
                
        #     # Handle automatic function calling setting
        #     if config.auto_function_calling is False:
        #         gemini_config.automatic_function_calling = {"disable": True}
        
        # # Legacy/simple search flag support
        # elif config.search:
        #     gemini_config.tools = [{"google_search": {}}]
        
        return gemini_config
    
    async def _generate_internal(
        self, 
        messages: List[Message | str],
        model: str,
        config: Optional[GenerationConfig] = None
    ) -> LLMResponse:
        """
        Generate a text completion response from Gemini
        """
        try:
            # Set default config if none provided
            config = config or GenerationConfig()
            
            # Prepare content and configuration
            contents, system_instruction = self._prepare_content(messages)
            gemini_config = self._prepare_config(config, system_instruction)
            
            # Make the async API call
            response: genai_types.GenerateContentResponse = await self.client.aio.models.generate_content(
                model=model,
                contents=contents,
                config=gemini_config
            )
            
            # Extract text content
            content = response.text
            
            # Extract tool calls if available
            tool_calls = None
            if (hasattr(response, 'candidates') and response.candidates and 
                hasattr(response.candidates[0], 'content') and response.candidates[0].content):
                
                # Check for function calls in parts
                if response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call'):
                            if tool_calls is None:
                                tool_calls = []
                            tool_calls.append({
                                "name": part.function_call.name if part.function_call else None,
                                "arguments": part.function_call.args if part.function_call else None,
                            })
            
            # Extract usage information
            usage = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
            
            # Extract token usage if available
            if response.usage_metadata:
                usage["prompt_tokens"] = response.usage_metadata.prompt_token_count or 0
                usage["completion_tokens"] = response.usage_metadata.candidates_token_count or 0
                usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
            
            # Create and return the LLMResponse
            return LLMResponse(
                text=content or "",
                model=model,
                usage=LLMUsage(
                    prompt_tokens=usage["prompt_tokens"],
                    completion_tokens=usage["completion_tokens"],
                ),
                raw_response=response,
                tool_calls=tool_calls
            )
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            logger.error(traceback.format_exc())
            raise self._handle_provider_error(e)
    
    async def _stream_generate(
        self, 
        messages: List[Message | str],
        model: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Stream a text completion response from Gemini
        """
        try:
            # Set default config if none provided
            config = config or GenerationConfig()
            
            # Prepare content and configuration
            contents, system_instruction = self._prepare_content(messages)
            gemini_config = self._prepare_config(config, system_instruction)
            
            # Make the streaming API call using the dedicated streaming method
            async for chunk in await self.client.aio.models.generate_content_stream(
                model=model,
                contents=contents,
                config=gemini_config
            ): # type: ignore # NOTE: I'm getting a type error here... but it works???
                # Extract and yield text from the chunk
                chunk: genai_types.GenerateContentResponse
                
                if chunk.text:
                    yield StreamEvent(
                        type="in_progress",
                        text=chunk.text,
                        usage=LLMUsage(
                        prompt_tokens=0,
                        completion_tokens=0,
                        )
                    )
                if chunk.candidates:
                    # TODO: if google adds "thinking" to the response, we can use that to yield a "thinking" event
                    # Currently google doesn't support getting the "thinking" through the API - https://ai.google.dev/gemini-api/docs/thinking
                    
                    # If the model has finished generating, yield the final chunk
                    if chunk.candidates[0].finish_reason is not None:
                        prompt_tokens = chunk.usage_metadata.prompt_token_count or 0 if chunk.usage_metadata else 0
                        completion_tokens = chunk.usage_metadata.candidates_token_count or 0 if chunk.usage_metadata else 0
                        yield StreamEvent(
                            type="complete",
                            text="",
                            usage=LLMUsage(
                                prompt_tokens=prompt_tokens,
                                completion_tokens=completion_tokens,
                            )
                        )
                
        except Exception as e:
            logger.error(f"Gemini API streaming error: {str(e)}")
            logger.error(traceback.format_exc())
            # Yield an error event before raising the exception
            yield StreamEvent(
                type="error",
                text="",
                error=str(e),
                usage=LLMUsage(
                    prompt_tokens=0,
                    completion_tokens=0,
                    )
            )
            raise self._handle_provider_error(e)
    
    # def embed(self, contents: Sequence, model: str, embed_config: EmbedContentConfig) -> Sequence:
    #     """
    #     Embed a list of contents using Gemini
    #     """
    #     response = self.client.models.embed_content(
    #         model=model,
    #         contents=contents,
    #         config=genai_types.EmbedContentConfig(
    #             embedding_dim=embedding_dim
    #         )
    #     )
    #     return response.embeddings
    
    def _handle_provider_error(self, exception: Exception) -> LLMProviderException:
        """
        Convert provider-specific exceptions to our exception types
        Must be implemented by each provider
        """
        error_message = str(exception)
        error_code = "gemini_error"
        category = ErrorCategory.UNKNOWN
        retry_after = None
        
        # TODO: handle specific errors better
        
        # Categorize based on error message content
        if any(text in error_message.lower() for text in ["quota", "rate limit", "429"]):
            category = ErrorCategory.RATE_LIMIT
            error_code = "rate_limit_exceeded"
            
        elif any(text in error_message.lower() for text in ["unauthenticated", "unauthorized", "invalid api key", "401", "403"]):
            category = ErrorCategory.AUTHENTICATION
            error_code = "authentication_error"
            
        elif any(text in error_message.lower() for text in ["safety", "blocked", "harmful", "content filter"]):
            category = ErrorCategory.CONTENT_FILTER
            error_code = "content_filter_error"
            
        elif any(text in error_message.lower() for text in ["model not found", "invalid model", "not supported"]):
            category = ErrorCategory.INVALID_REQUEST
            error_code = "model_not_found"
            
        elif any(text in error_message.lower() for text in ["server error", "internal error", "500", "503", "service unavailable"]):
            category = ErrorCategory.SERVICE_ERROR
            error_code = "service_error"
            
        elif any(text in error_message.lower() for text in ["connection", "timeout", "network"]):
            category = ErrorCategory.NETWORK_ERROR
            error_code = "network_error"
            
        elif any(text in error_message.lower() for text in ["context length", "too long", "token limit"]):
            category = ErrorCategory.CONTEXT_LENGTH
            error_code = "context_length_error"
        
        # Extract retry-after information if present
        # This would depend on the specific error response structure
        return LLMProviderException(
            message=error_message,
            code=error_code,
            category=category,
            provider=self.__class__.__name__,
            retry_after=retry_after,
            raw_error=exception
        )
    
    async def close(self):
        """
        Clean up resources
        """
        # The Gemini client doesn't have explicit close methods,
        # but we can help garbage collection by removing references
        self._client = None
        
        # Call parent close method to handle stream manager cleanup
        await super().close()
        
if __name__ == "__main__":
    from google import genai

    client = genai.Client(api_key="GEMINI_API_KEY")

    result = client.models.embed_content(
            model="gemini-embedding-exp-03-07",
            contents="How does alphafold work?",
    )

    print(result.embeddings)