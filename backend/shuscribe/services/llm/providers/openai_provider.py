# shuscribe/services/llm/providers/openai_provider.py

import os
import json
from typing import Dict, List, Optional, AsyncIterator, Union, Any, Type, TypeVar
from openai import AsyncOpenAI
from pydantic import BaseModel

from shuscribe.services.llm.providers.provider import (
    LLMProvider, Message, MessageRole, LLMResponse, GenerationConfig, 
    FinishReason, ToolCall, ToolDefinition, TextContent,
    ImageContent
)

T = TypeVar('T', bound=BaseModel)

class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""
    
    def _initialize_client(self, api_key: Optional[str] = None, **kwargs) -> Any:
        """Initialize the OpenAI client."""
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No OpenAI API key provided. Set OPENAI_API_KEY environment variable or pass api_key.")
        
        return AsyncOpenAI(api_key=api_key, **kwargs)
    
    @property
    def client(self) -> AsyncOpenAI:
        """OpenAI supports streaming."""
        return self._client
    
    @property
    def supports_structured_output(self) -> bool:
        """OpenAI supports structured outputs."""
        return True
    
    @property
    def supports_multimodal_input(self) -> bool:
        """OpenAI supports multimodal inputs."""
        return True
    
    @property
    def supports_tool_use(self) -> bool:
        """OpenAI supports function/tool calling."""
        return True
    
    @property
    def supports_parallel_tool_calls(self) -> bool:
        """OpenAI supports parallel tool calling."""
        return True
    
    @property
    def supports_search(self) -> bool:
        """OpenAI supports web search integration."""
        return True
    
    def _convert_role(self, role: MessageRole) -> str:
        """Convert internal role to OpenAI role."""
        if role == MessageRole.SYSTEM:
            return "system"
        elif role == MessageRole.USER:
            return "user"
        elif role == MessageRole.ASSISTANT:
            return "assistant"
        elif role == MessageRole.FUNCTION:
            return "function"
        else:
            return "user"  # Default to user for unknown roles
    
    def _convert_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert internal message format to OpenAI format."""
        openai_messages = []
        
        for message in messages:
            content: Union[str, List[Dict[str, Any]], None] = None
            
            # Handle multimodal content
            if len(message.content) > 1 or not isinstance(message.content[0], TextContent):
                content = []
                for block in message.content:
                    if isinstance(block, TextContent):
                        content.append({
                            "type": "text",
                            "text": block.text
                        })
                    elif isinstance(block, ImageContent):
                        # Handle image content
                        import base64
                        
                        if isinstance(block.image_data, str):
                            # Assume base64 string
                            image_data = block.image_data
                        else:
                            # Convert bytes to base64
                            image_data = base64.b64encode(block.image_data).decode('utf-8')
                        
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{block.mime_type};base64,{image_data}"
                            }
                        })
            else:
                # Simple text message
                content = message.content[0].text
            
            msg_dict = {
                "role": self._convert_role(message.role),
                "content": content
            }
            
            # Add name if provided (useful for function calls)
            if message.name:
                msg_dict["name"] = message.name
                
            openai_messages.append(msg_dict)
        
        return openai_messages
    
    def _convert_tool_definitions(self, tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
        """Convert internal tool definitions to OpenAI's function format."""
        openai_tools = []
        
        for tool in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters_schema
                }
            })
            
        return openai_tools
    
    def _build_request_params(self, 
                             messages: List[Message], 
                             model: str, 
                             config: Optional[GenerationConfig] = None) -> Dict[str, Any]:
        """Build OpenAI API request parameters."""
        if not config:
            config = GenerationConfig()
            
        # Convert messages
        openai_messages = self._convert_messages(messages)
        
        # Start building request parameters
        request_params = {
            "model": model,
            "messages": openai_messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
            "frequency_penalty": config.frequency_penalty,
            "presence_penalty": config.presence_penalty,
        }
        
        # Add stop sequences if provided
        if config.stop_sequences:
            request_params["stop"] = config.stop_sequences
            
        # Configure seed if provided
        if config.seed is not None:
            request_params["seed"] = config.seed
            
        # Configure response format for JSON
        if config.response_format:
            # OpenAI API only accepts {"type": "json_object"} without a schema property
            # The schema information should be included in the system message
            request_params["response_format"] = {"type": "json_object"}
            
        # Configure tools if provided
        if config.tools:
            request_params["tools"] = self._convert_tool_definitions(config.tools)
            
            # Configure tool choice behavior
            if not config.parallel_tool_calling:
                request_params["tool_choice"] = "auto"
            else:
                # Allow parallel tool calling
                request_params["tool_choice"] = {"type": "any"}
                
        # Add web search if enabled
        if config.search_enabled:
            # Add the retrieval tool for web search
            if "tools" not in request_params:
                request_params["tools"] = []
                
            request_params["tools"].append({
                "type": "retrieval"
            })
            
        # Add any additional parameters from the config
        if hasattr(config, 'additional_params'):
            request_params.update(config.additional_params)
            
        return request_params
    
    def _process_response(self, response: Any) -> LLMResponse:
        """Process an OpenAI response into our standard LLMResponse format."""
        # Extract the text content
        text = None
        if hasattr(response, 'choices') and response.choices:
            if hasattr(response.choices[0].message, 'content'):
                text = response.choices[0].message.content
                
        # Determine finish reason
        finish_reason = None
        if hasattr(response, 'choices') and response.choices:
            reason = response.choices[0].finish_reason
            if reason == "stop":
                finish_reason = FinishReason.COMPLETED
            elif reason == "length":
                finish_reason = FinishReason.MAX_TOKENS
            elif reason == "content_filter":
                finish_reason = FinishReason.ERROR
            elif reason == "tool_calls":
                finish_reason = FinishReason.TOOL_CALLS
                
        # Extract tool calls if any
        tool_calls = []
        if (hasattr(response, 'choices') and response.choices and 
            hasattr(response.choices[0].message, 'tool_calls') and 
            response.choices[0].message.tool_calls):
            
            for tool_call in response.choices[0].message.tool_calls:
                # Parse the arguments JSON
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {"raw_arguments": tool_call.function.arguments}
                    
                tool_calls.append(ToolCall(
                    name=tool_call.function.name,
                    arguments=arguments,
                    id=tool_call.id
                ))
                
        # Try to extract structured response if it was requested
        parsed_response = None
        if text and text.strip().startswith('{') and text.strip().endswith('}'):
            try:
                parsed_response = json.loads(text)
            except json.JSONDecodeError:
                parsed_response = None
                
        # Extract usage information
        usage = {}
        if hasattr(response, 'usage'):
            usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        
        return LLMResponse(
            text=text,
            model=response.model if hasattr(response, 'model') else "",
            usage=usage,
            finish_reason=finish_reason,
            tool_calls=tool_calls,
            parsed_response=parsed_response,
            raw_response=response
        )
    
    async def generate(
        self, 
        messages: List[Message],
        model: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a response using OpenAI."""
        request_params = self._build_request_params(messages, model, config)
        request_params.update(kwargs)
        
        try:
            response = await self.client.chat.completions.create(**request_params)
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
        """Generate a streaming response using OpenAI."""
        if not config:
            config = GenerationConfig()
            
        # Build request parameters and set stream to True
        request_params = self._build_request_params(messages, model, config)
        request_params["stream"] = True
        request_params.update(kwargs)
        
        try:
            stream = await self.client.chat.completions.create(**request_params)
            
            # Variables to accumulate the full response
            accumulated_text = ""
            current_tool_calls = []
            finish_reason = None
            
            async for chunk in stream:
                # Process the chunk
                if len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    
                    # Update finish reason if present
                    if choice.finish_reason:
                        if choice.finish_reason == "stop":
                            finish_reason = FinishReason.COMPLETED
                        elif choice.finish_reason == "length":
                            finish_reason = FinishReason.MAX_TOKENS
                        elif choice.finish_reason == "content_filter":
                            finish_reason = FinishReason.ERROR
                        elif choice.finish_reason == "tool_calls":
                            finish_reason = FinishReason.TOOL_CALLS
                    
                    # Handle content delta if present
                    delta = choice.delta
                    
                    if hasattr(delta, 'content') and delta.content:
                        accumulated_text += delta.content
                        # If streaming as text, yield just the content
                        if config.stream:
                            yield delta.content
                            
                    # Handle tool call deltas
                    if hasattr(delta, 'tool_calls') and delta.tool_calls:
                        for tool_call_delta in delta.tool_calls:
                            # Find or create the tool call
                            tool_call = None
                            for existing in current_tool_calls:
                                if existing.id == tool_call_delta.id:
                                    tool_call = existing
                                    break
                                    
                            if tool_call is None and hasattr(tool_call_delta, 'id'):
                                # Create a new tool call record
                                tool_call = ToolCall(
                                    name="" if not hasattr(tool_call_delta, 'function') else tool_call_delta.function.name or "",
                                    arguments={},
                                    id=tool_call_delta.id
                                )
                                current_tool_calls.append(tool_call)
                                
                            # Update the tool call with delta information
                            if tool_call:
                                if hasattr(tool_call_delta, 'function'):
                                    if hasattr(tool_call_delta.function, 'name'):
                                        tool_call.name = tool_call_delta.function.name
                                        
                                    if hasattr(tool_call_delta.function, 'arguments'):
                                        # Append to the arguments JSON string
                                        if isinstance(tool_call.arguments, dict) and 'raw_arguments' in tool_call.arguments:
                                            tool_call.arguments['raw_arguments'] += tool_call_delta.function.arguments
                                        else:
                                            tool_call.arguments = {'raw_arguments': tool_call_delta.function.arguments}
                
                # If not streaming as text, create and yield an LLMResponse for each chunk
                if not config.stream:
                    # Try to parse accumulated tool call arguments as JSON
                    for tool_call in current_tool_calls:
                        if isinstance(tool_call.arguments, dict) and 'raw_arguments' in tool_call.arguments:
                            try:
                                tool_call.arguments = json.loads(tool_call.arguments['raw_arguments'])
                            except json.JSONDecodeError:
                                # Keep as raw if not valid JSON yet
                                pass
                                
                    yield LLMResponse(
                        text=accumulated_text,
                        model=model,
                        finish_reason=finish_reason,
                        tool_calls=current_tool_calls.copy(),
                        raw_response=chunk
                    )
            
            # Parse final tool call arguments if needed
            for tool_call in current_tool_calls:
                if isinstance(tool_call.arguments, dict) and 'raw_arguments' in tool_call.arguments:
                    try:
                        tool_call.arguments = json.loads(tool_call.arguments['raw_arguments'])
                    except json.JSONDecodeError:
                        # Keep as raw if not valid JSON
                        pass
                        
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
        response_format: Type[T],
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> LLMResponse:
        """Parse a response into a structured output using OpenAI."""
        if not config:
            config = GenerationConfig()
        
        # Set response format in the config
        config.response_format = response_format
        
        # Add schema information to the system message
        system_message_found = False
        schema_info = ""
        
        # Build schema info from the response_format
        if hasattr(response_format, "__annotations__"):
            schema_info = "Return a JSON object with the following structure:\n"
            for field, type_hint in response_format.__annotations__.items():
                field_type = str(type_hint).replace("typing.", "")
                schema_info += f"- {field}: {field_type}\n"
        
        # Add or update system message with schema information
        for i, message in enumerate(messages):
            if message.role == MessageRole.SYSTEM:
                system_message_found = True
                # Append schema info to existing system message
                current_content = message.content[0].text if isinstance(message.content[0], TextContent) else ""
                message.content = [TextContent(text=f"{current_content}\n\n{schema_info}")]
                break
        
        # If no system message found, add one
        if not system_message_found:
            messages.insert(0, Message(
                role=MessageRole.SYSTEM,
                content=f"You provide information in a structured format. {schema_info}"
            ))
        
        # Use the generate method with the updated config
        response = await self.generate(messages, model, config, **kwargs)
        
        # If we received text, try to parse it as JSON
        if response.text and not response.parsed_response:
            try:
                data = json.loads(response.text)
                
                # If response_format is a Pydantic model, instantiate it
                if hasattr(response_format, "parse_obj"):
                    response.parsed_response = response_format.parse_obj(data)
                else:
                    response.parsed_response = data
                    
            except (json.JSONDecodeError, ValueError) as e:
                # Failed to parse as JSON
                response.text = f"Failed to parse: {response.text} - Error: {str(e)}"
        
        # For error cases, create an empty instance of the response format
        # This prevents AttributeError when accessing properties
        if response.finish_reason == FinishReason.ERROR and not response.parsed_response:
            try:
                # Try to create an empty instance with default values
                empty_instance = response_format()
                response.parsed_response = empty_instance
            except Exception:
                # If we can't create an empty instance, leave as None
                pass
            
        return response
    
    async def close(self):
        """Clean up resources."""
        if self.client and hasattr(self.client, 'close') and callable(self.client.close):
            await self.client.close()