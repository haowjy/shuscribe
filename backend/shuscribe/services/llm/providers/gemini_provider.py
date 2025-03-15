# shuscribe/services/llm/providers/gemini_provider.py

import os
from typing import List, Optional, AsyncIterator, Union, Any, Type, TypeVar
from google import genai
import google.genai.types as genai_types
from pydantic import BaseModel

from shuscribe.services.llm.providers.provider import (
    LLMProvider, Message, MessageRole, LLMResponse, GenerationConfig, 
    FinishReason, ToolCall, ToolDefinition, TextContent,
    ImageContent
)

T = TypeVar('T', bound=BaseModel)

class GeminiProvider(LLMProvider):
    """Google Gemini API provider implementation."""
    
    def _initialize_client(self, api_key: Optional[str] = None, **kwargs) -> Any:
        """Initialize the Gemini Generative AI client."""
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No Gemini API key provided. Set GEMINI_API_KEY environment variable or pass api_key.")
        
        return genai.Client(api_key=api_key, **kwargs)
    
    @property
    def client(self) -> genai.Client:
        """Gemini supports streaming."""
        return self._client
    
    @property
    def supports_structured_output(self) -> bool:
        """Gemini supports structured outputs."""
        return True
    
    @property
    def supports_multimodal_input(self) -> bool:
        """Gemini supports multimodal inputs including images, audio, and video."""
        return True
    
    @property
    def supports_tool_use(self) -> bool:
        """Gemini supports function/tool calling."""
        return True
    
    @property
    def supports_parallel_tool_calls(self) -> bool:
        """Gemini supports parallel tool calling."""
        return True
    
    @property
    def supports_search(self) -> bool:
        """Gemini supports Google Search integration."""
        return True
    
    def _convert_tool_definitions(self, tools: List[ToolDefinition]) -> genai_types.ToolListUnion:
        """Convert internal tool definitions to Gemini's function format."""
        return [
            genai_types.Tool(
                function_declarations=[
                    genai_types.FunctionDeclaration(
                        name=tool.name,
                        description=tool.description,
                        parameters=genai_types.Schema(
                            type=genai_types.Type.OBJECT,
                            properties=tool.parameters_schema.get("properties", {}),
                            required=tool.parameters_schema.get("required", [])
                        )
                    )
                ]
            ) for tool in tools
        ]
    
    def _convert_messages(self, messages: List[Message]) -> List[Any]:
        """Convert internal message format to Gemini format."""
        gemini_messages = []
        
        for message in messages:
            content_parts = []
            
            for content_block in message.content:
                if isinstance(content_block, TextContent):
                    content_parts.append(content_block.text)
                elif isinstance(content_block, ImageContent):
                    # Handle image content
                    # For Gemini, we need to convert to their image format
                    from PIL import Image
                    import base64
                    import io
                    
                    if isinstance(content_block.image_data, str):
                        # Assume it's a base64 string
                        image_bytes = base64.b64decode(content_block.image_data)
                        image = Image.open(io.BytesIO(image_bytes))
                    else:
                        # Assume it's bytes
                        image = Image.open(io.BytesIO(content_block.image_data))
                    
                    content_parts.append(image)
                
                # Note: Handling for video and audio would be added here
                # depending on Gemini's API requirements
            
            # Gemini handles roles differently in their chat API vs. direct generation
            # For simplicity, we're just adding the content parts here
            gemini_messages.extend(content_parts)
        
        return gemini_messages
    
    def _build_generation_config(self, config: Optional[GenerationConfig] = None) -> genai_types.GenerateContentConfig:
        """Build Gemini generation config from our generic config."""
        if not config:
            config = GenerationConfig()
            
        gemini_config = genai_types.GenerateContentConfig(
            temperature=config.temperature,
            top_p=config.top_p,
            top_k=config.top_k if config.top_k else None,
            max_output_tokens=config.max_tokens if config.max_tokens else None,
            stop_sequences=config.stop_sequences if config.stop_sequences else None,
        )
        
        # Add system instructions if provided
        if config.system_prompt:
            gemini_config.system_instruction = config.system_prompt
            
        # Add tools/functions if provided
        if config.tools:
            gemini_config.tools = self._convert_tool_definitions(config.tools)
            
        # Configure structured output if requested
        if config.response_format:
            gemini_config.response_mime_type = 'application/json'
            gemini_config.response_schema = config.response_format
            
        # Configure Google Search if enabled
        if config.search_enabled:
            gemini_config.tools = gemini_config.tools or []
            gemini_config.tools.append(genai_types.Tool(
                google_search=genai_types.GoogleSearch()
            ))
            
        # Handle parallel tool calling configuration
        if not config.parallel_tool_calling and config.tools:
            gemini_config.automatic_function_calling = genai_types.AutomaticFunctionCallingConfig(
                disable=False,  # Enable automatic function calling
                maximum_remote_calls=10  # Default value
            )
        return gemini_config
    
    def _process_response(self, response: Any) -> LLMResponse:
        """Process a Gemini response into our standard LLMResponse format."""
        # Extract the text content
        text = response.text if hasattr(response, 'text') else None
        
        # Determine finish reason
        finish_reason = None
        if hasattr(response, 'finish_reason'):
            if response.finish_reason == 'stop':
                finish_reason = FinishReason.COMPLETED
            elif response.finish_reason == 'max_tokens':
                finish_reason = FinishReason.MAX_TOKENS
            elif response.finish_reason == 'safety':
                finish_reason = FinishReason.ERROR
            elif response.finish_reason == 'recitation':
                finish_reason = FinishReason.ERROR
            elif response.finish_reason == 'other':
                finish_reason = FinishReason.ERROR
                
        # Extract tool calls if any
        tool_calls = []
        if hasattr(response, 'function_calls') and response.function_calls:
            for fn_call in response.function_calls:
                # Add check to ensure fn_call and fn_call.name are not None
                if fn_call and hasattr(fn_call, 'name') and fn_call.name:
                    tool_calls.append(ToolCall(
                        name=fn_call.name,
                        arguments=fn_call.args,
                        id=fn_call.function_call_id if hasattr(fn_call, 'function_call_id') else None
                    ))
                
        # Extract structured response if present
        parsed_response = None
        if hasattr(response, 'parsed') and response.parsed:
            parsed_response = response.parsed
            
        # Extract usage information
        usage = {}
        if hasattr(response, 'usage'):
            usage = {
                'prompt_tokens': response.usage.prompt_token_count if hasattr(response.usage, 'prompt_token_count') else 0,
                'completion_tokens': response.usage.candidates_token_count if hasattr(response.usage, 'candidates_token_count') else 0,
                'total_tokens': (
                    (response.usage.prompt_token_count if hasattr(response.usage, 'prompt_token_count') else 0) + 
                    (response.usage.candidates_token_count if hasattr(response.usage, 'candidates_token_count') else 0)
                )
            }
            
        # Extract citations if present (Google Search results)
        citations = []
        if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
            if hasattr(response.grounding_metadata, 'search_results') and response.grounding_metadata.search_results:
                for result in response.grounding_metadata.search_results:
                    citations.append({
                        'text': result.snippet if hasattr(result, 'snippet') else "",
                        'source': result.url if hasattr(result, 'url') else "",
                        'metadata': {
                            'title': result.title if hasattr(result, 'title') else ""
                        }
                    })
        
        return LLMResponse(
            text=text,
            model=response.model if hasattr(response, 'model') else "",
            usage=usage,
            finish_reason=finish_reason,
            tool_calls=tool_calls,
            parsed_response=parsed_response,
            raw_response=response,
            citations=citations
        )
    
    async def generate(
        self, 
        messages: List[Message],
        model: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a response using Gemini."""
        gemini_messages = self._convert_messages(messages)
        gemini_config = self._build_generation_config(config)
        
        # Handle system message if present
        system_instruction = None
        if messages and messages[0].role == MessageRole.SYSTEM:
            system_instruction = "".join([
                block.text for block in messages[0].content 
                if isinstance(block, TextContent)
            ])
            messages = messages[1:]  # Remove system message from regular messages
            
        if system_instruction:
            gemini_config.system_instruction = system_instruction
            
        try:
            # Use the async client here
            response = await self.client.aio.models.generate_content(
                model=model,
                contents=gemini_messages,
                config=gemini_config,
                **kwargs
            )
            
            return self._process_response(response)
            
        except Exception as e:
            # Handle exceptions and convert to LLMResponse with error
            return LLMResponse(
                text=f"Error: {str(e)}",
                model=model,
                usage={},
                finish_reason=FinishReason.ERROR,
                raw_response={"error": str(e)}
            )
    
    async def generate_stream(
        self, 
        messages: List[Message],
        model: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> AsyncIterator[Union[str, LLMResponse]]:
        """Generate a streaming response using Gemini."""
        if not config:
            config = GenerationConfig()
            
        gemini_messages = self._convert_messages(messages)
        gemini_config = self._build_generation_config(config)
        
        try:
            # Get the stream response
            stream_response = await self.client.aio.models.generate_content_stream(
                model=model,
                contents=gemini_messages,
                config=gemini_config,
                **kwargs
            )
            
            # Variables to accumulate the full response
            accumulated_text = ""
            finish_reason = None
            tool_calls = []
            
            # Await the iterator before using it
            async for chunk in await stream_response:
                # Update accumulated text
                if hasattr(chunk, 'text'):
                    chunk_text = chunk.text or ""
                    accumulated_text += chunk_text
                    
                    # If streaming as text, yield just the content
                    if config.stream:
                        yield chunk_text
                        continue
                
                # Update finish reason if present
                if hasattr(chunk, 'candidates') and chunk.candidates:
                    candidate = chunk.candidates[0]
                    if hasattr(candidate, 'finish_reason'):
                        if candidate.finish_reason == 'STOP':
                            finish_reason = FinishReason.COMPLETED
                        elif candidate.finish_reason == 'MAX_TOKENS':
                            finish_reason = FinishReason.MAX_TOKENS
                        elif candidate.finish_reason in ('SAFETY', 'RECITATION', 'OTHER'):
                            finish_reason = FinishReason.ERROR
                
                # Handle tool calls if present
                if hasattr(chunk, 'function_calls') and chunk.function_calls:
                    for fn_call in chunk.function_calls:
                        if fn_call and hasattr(fn_call, 'name') and fn_call.name:
                            tool_calls.append(ToolCall(
                                name=fn_call.name,
                                arguments=fn_call.args if fn_call.args else {},
                                id=getattr(fn_call, 'function_call_id', None)
                            ))
                
                # If not streaming as text, yield an LLMResponse for each chunk
                if not config.stream:
                    yield LLMResponse(
                        text=accumulated_text,
                        model=model,
                        finish_reason=finish_reason,
                        tool_calls=tool_calls.copy(),
                        raw_response=chunk
                    )
                    
        except Exception as e:
            # Handle streaming errors
            error_response = LLMResponse(
                text=f"Error: {str(e)}",
                model=model,
                usage={},
                finish_reason=FinishReason.ERROR,
                raw_response={"error": str(e)}
            )
            
            if config.stream:
                yield str(e)
            else:
                yield error_response
    
    async def parse(
        self,
        messages: List[Message],
        model: str,
        response_format: Type[BaseModel],
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> LLMResponse:
        """Parse a response into a structured output using Gemini."""
        if not config:
            config = GenerationConfig()
            
        # Set response format in the config
        config.response_format = response_format
        
        # Use the generate method with the updated config
        return await self.generate(messages, model, config, **kwargs)
    
    async def close(self):
        """Clean up resources."""
        # Gemini client doesn't require explicit cleanup
        pass