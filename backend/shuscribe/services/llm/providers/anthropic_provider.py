# shuscribe/services/llm/providers/anthropic_provider.py

import os
import json
from typing import Dict, List, Optional, AsyncIterator, Type, Union, Any, TypeVar
import anthropic
from pydantic import BaseModel
import traceback
import logging

from shuscribe.services.llm.providers.provider import (
    LLMProvider, Message, MessageRole, LLMResponse, GenerationConfig, 
    FinishReason, ToolCall, ToolDefinition, TextContent,
    ImageContent
)

T = TypeVar('T', bound=BaseModel)

class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider implementation."""
    
    def _initialize_client(self, api_key: Optional[str] = None, **kwargs) -> Any:
        """Initialize the Anthropic client."""
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("No Anthropic API key provided. Set ANTHROPIC_API_KEY environment variable or pass api_key.")
        
        return anthropic.AsyncAnthropic(api_key=api_key, **kwargs)
    
    @property
    def client(self) -> anthropic.AsyncAnthropic:
        """Anthropic supports streaming."""
        return self._client
    
    @property
    def supports_structured_output(self) -> bool:
        """Claude supports structured outputs through JSON format."""
        return True
    
    @property
    def supports_multimodal_input(self) -> bool:
        """Claude supports text and image inputs."""
        return True
    
    @property
    def supports_tool_use(self) -> bool:
        """Claude supports function/tool calling."""
        return True
    
    @property
    def supports_parallel_tool_calls(self) -> bool:
        """Claude supports parallel tool calling."""
        return True
    
    @property
    def supports_extended_thinking(self) -> bool:
        """Claude supports extended thinking."""
        return True
    
    @property
    def supports_citations(self) -> bool:
        """Claude supports citations."""
        return True
    
    def _convert_role(self, role: MessageRole) -> str:
        """Convert internal role to Anthropic role."""
        if role == MessageRole.USER:
            return "user"
        elif role == MessageRole.ASSISTANT:
            return "assistant"
        elif role == MessageRole.FUNCTION:
            return "assistant"  # Anthropic doesn't have a function role, use assistant
        else:
            # System role is handled separately in Anthropic
            return "user"
    
    def _convert_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert internal message format to Anthropic format."""
        anthropic_messages = []
        
        for message in messages:
            # Skip system messages as they're handled separately
            if message.role == MessageRole.SYSTEM:
                continue
                
            content = []
            
            for content_block in message.content:
                if isinstance(content_block, TextContent):
                    content.append({
                        "type": "text",
                        "text": content_block.text
                    })
                elif isinstance(content_block, ImageContent):
                    # Handle image content for Claude
                    import base64
                    
                    if isinstance(content_block.image_data, str):
                        # Assume it's already a base64 string
                        image_data = content_block.image_data
                    else:
                        # Convert bytes to base64
                        image_data = base64.b64encode(content_block.image_data).decode('utf-8')
                    
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": content_block.mime_type,
                            "data": image_data
                        }
                    })
            
            anthropic_messages.append({
                "role": self._convert_role(message.role),
                "content": content
            })
        
        return anthropic_messages
    
    def _extract_system_prompt(self, messages: List[Message]) -> Optional[str]:
        """Extract system prompt from messages if present."""
        if messages and messages[0].role == MessageRole.SYSTEM:
            # Extract text content from system message
            return "".join([
                block.text for block in messages[0].content 
                if isinstance(block, TextContent)
            ])
        return None
    
    def _convert_tool_definitions(self, tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
        """Convert internal tool definitions to Anthropic's tool format."""
        anthropic_tools = []
        
        for tool in tools:
            anthropic_tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters_schema
            })
            
        return anthropic_tools
    
    def _build_request_params(self, 
                             messages: List[Message], 
                             model: str, 
                             config: Optional[GenerationConfig] = None) -> Dict[str, Any]:
        """Build Anthropic API request parameters."""
        if not config:
            config = GenerationConfig()
            
        # Convert messages and extract system prompt
        anthropic_messages = self._convert_messages(messages)
        system = self._extract_system_prompt(messages)
        
        # Start building request parameters
        request_params = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": config.max_tokens if config.max_tokens else 1024,
            "temperature": config.temperature,
            "top_p": config.top_p,
        }
        
        # Add system prompt if present
        if system or config.system_prompt:
            request_params["system"] = config.system_prompt or system
            
        # Add stop sequences if provided
        if config.stop_sequences:
            request_params["stop_sequences"] = config.stop_sequences
            
        # Configure tools if provided
        if config.tools:
            request_params["tools"] = self._convert_tool_definitions(config.tools)
            
            # Configure tool choice behavior
            if not config.parallel_tool_calling:
                request_params["tool_choice"] = {
                    "type": "auto",
                    "disable_parallel_tool_use": True
                }
                
        # Configure extended thinking if enabled
        if config.extended_thinking:
            request_params["thinking"] = {
                "type": "enabled",
                "budget_tokens": config.extended_thinking_budget or 1024
            }
            
        # Add any additional parameters from the config
        if hasattr(config, 'additional_params'):
            request_params.update(config.additional_params)
            
        return request_params
    
    def _process_response(self, response: Any) -> LLMResponse:
        """Process an Anthropic response into our standard LLMResponse format."""
        # Extract the text content
        text = None
        content_blocks = []
        tool_calls = []
        citations = []
        
        try:
            if hasattr(response, 'content'):
                # Handle content blocks
                for block in response.content:
                    try:
                        # Case 1: TextBlock object from Anthropic API
                        if hasattr(block, 'text'):
                            block_text = block.text
                            if text is None:
                                text = block_text
                            else:
                                text += block_text
                            content_blocks.append(TextContent(text=block_text))
                        # Case 2: Dictionary-style block
                        elif isinstance(block, dict):
                            if block.get('type') == 'text':
                                block_text = block.get('text', '')
                                if text is None:
                                    text = block_text
                                else:
                                    text += block_text
                                content_blocks.append(TextContent(text=block_text))
                                
                                # Process citations
                                if 'citations' in block:
                                    for citation in block.get('citations', []):
                                        citations.append({
                                            'text': citation.get('cited_text', ''),
                                            'source': citation.get('title', ''),
                                            'metadata': {
                                                'start_index': citation.get('start_index', 0),
                                                'end_index': citation.get('end_index', 0)
                                            }
                                        })
                        
                            # Process tool calls
                            elif block.get('type') == 'tool_use':
                                tool_calls.append(ToolCall(
                                    name=block.get('name', ''),
                                    arguments=block.get('input', {}),
                                    id=block.get('id')
                                ))
                    
                    except Exception as block_error:
                        logging.error(f"Error processing content block: {block_error}\n{traceback.format_exc()}")
                        # Continue processing other blocks even if one fails
                        continue

            # Determine finish reason - moved outside the if block
            finish_reason = None
            if hasattr(response, 'stop_reason'):
                if response.stop_reason == 'end_turn':
                    finish_reason = FinishReason.COMPLETED
                elif response.stop_reason == 'max_tokens':
                    finish_reason = FinishReason.MAX_TOKENS
                elif response.stop_reason == 'stop_sequence':
                    finish_reason = FinishReason.STOP_SEQUENCE
                elif response.stop_reason == 'tool_use':
                    finish_reason = FinishReason.TOOL_CALLS
            
            # Extract usage information - moved outside the if block
            usage = {}
            if hasattr(response, 'usage'):
                # Handle Usage object from Anthropic API - access attributes directly
                try:
                    input_tokens = getattr(response.usage, 'input_tokens', 0)
                    output_tokens = getattr(response.usage, 'output_tokens', 0)
                    usage = {
                        'prompt_tokens': input_tokens,
                        'completion_tokens': output_tokens,
                        'total_tokens': input_tokens + output_tokens
                    }
                except Exception as usage_error:
                    logging.error(f"Error processing usage info: {usage_error}")
                    # Fallback to empty usage if processing fails
            
            # Return response regardless of whether content exists
            return LLMResponse(
                text=text,
                model=response.model if hasattr(response, 'model') else "",
                usage=usage,
                finish_reason=finish_reason,
                tool_calls=tool_calls,
                raw_response=response,
                citations=citations,
                content_blocks=content_blocks
            )
                
        except Exception as e:
            error_traceback = traceback.format_exc()
            logging.error(f"Error in _process_response: {str(e)}\n{error_traceback}")
            
            return LLMResponse(
                text=f"Error processing response: {str(e)}",
                model="",
                usage={},
                finish_reason=FinishReason.ERROR,
                raw_response={
                    "error": str(e),
                    "traceback": error_traceback,
                    "original_response": response
                }
            )
    
    async def generate(
        self, 
        messages: List[Message],
        model: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a response using Anthropic Claude."""
        request_params = self._build_request_params(messages, model, config)
        request_params.update(kwargs)
        
        try:
            response = await self.client.messages.create(**request_params)
            return self._process_response(response)
            
        except Exception as e:
            # Capture the full error traceback
            error_traceback = traceback.format_exc()
            logging.error(f"Error in Anthropic generate: {str(e)}\n{error_traceback}")
            
            return LLMResponse(
                text=f"Error: {str(e)}",
                model=model,
                usage={},
                finish_reason=FinishReason.ERROR,
                raw_response={
                    "error": str(e),
                    "traceback": error_traceback,
                    "request_params": request_params  # Include request params for debugging
                }
            )
    
    async def generate_stream(
        self, 
        messages: List[Message],
        model: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> AsyncIterator[Union[str, LLMResponse]]:
        """Generate a streaming response using Anthropic Claude."""
        if not config:
            config = GenerationConfig()
            
        # Set streaming to True
        request_params = self._build_request_params(messages, model, config)
        request_params["stream"] = True
        request_params.update(kwargs)
        
        try:
            stream = await self.client.messages.create(**request_params)
            
            # Initialize a partial response that we'll build up
            partial_response = {
                "model": model,
                "content": [],
                "stop_reason": None,
                "usage": {"input_tokens": 0, "output_tokens": 0}
            }
            
            current_text = ""
            
            async for chunk in stream:
                # Update the partial response with this chunk's data
                if hasattr(chunk, 'model'):
                    partial_response["model"] = chunk.model
                    
                if hasattr(chunk, 'type') and chunk.type == 'content_block_start':
                    # Start of a new content block
                    if chunk.content_block.get('type') == 'text':
                        current_text = ""
                        
                elif hasattr(chunk, 'type') and chunk.type == 'content_block_delta':
                    # Content delta
                    if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                        current_text += chunk.delta.text
                        
                        # Return just the text if stream is set to text mode
                        if config.stream:
                            yield chunk.delta.text
                        
                elif hasattr(chunk, 'type') and chunk.type == 'content_block_stop':
                    # End of a content block
                    if current_text:
                        partial_response["content"].append({
                            "type": "text",
                            "text": current_text
                        })
                        
                elif hasattr(chunk, 'type') and chunk.type == 'message_stop':
                    # End of the message
                    if hasattr(chunk, 'stop_reason'):
                        partial_response["stop_reason"] = chunk.stop_reason
                        
                    if hasattr(chunk, 'usage'):
                        partial_response["usage"] = chunk.usage
                        
                # If not in text-only stream mode, yield an LLMResponse for each chunk
                if not config.stream:
                    yield self._process_response(type('obj', (object,), partial_response))
                    
        except Exception as e:
            # Capture the full error traceback
            error_traceback = traceback.format_exc()
            logging.error(f"Error in Anthropic generate_stream: {str(e)}\n{error_traceback}")
            
            yield LLMResponse(
                text=f"Error: {str(e)}",
                model=model,
                usage={},
                finish_reason=FinishReason.ERROR,
                raw_response={
                    "error": str(e),
                    "traceback": error_traceback,
                    "request_params": request_params  # Include request params for debugging
                }
            )
    
    async def parse(
        self,
        messages: List[Message],
        model: str,
        response_format: Type[BaseModel],
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> LLMResponse:
        """Parse a response into a structured output using Anthropic Claude."""
        if not config:
            config = GenerationConfig()
            
        # For Claude, we'll use JSON mode by appending instructions
        # to the system prompt or the last user message
        
        # First convert the expected schema to a JSON schema
        schema_dict = {}
        if hasattr(response_format, "__annotations__"):
            # For Pydantic models
            for field_name, field_type in response_format.__annotations__.items():
                schema_dict[field_name] = str(field_type)
        else:
            # Use the raw type as a fallback
            schema_dict = {"type": str(response_format)}
            
        schema_str = json.dumps(schema_dict, indent=2)
        
        # Create system prompt instruction for JSON output
        json_instruction = f"You must respond with valid JSON that matches this schema: {schema_str}. Do not include explanations or other text outside the JSON."
        
        if config.system_prompt:
            config.system_prompt += "\n\n" + json_instruction
        else:
            # Check if there's a system message we can append to
            system_found = False
            for i, message in enumerate(messages):
                if message.role == MessageRole.SYSTEM:
                    # Add JSON instruction to existing system message
                    if isinstance(message.content[0], TextContent):
                        message.content[0].text += "\n\n" + json_instruction
                    elif isinstance(message.content, str):
                            message.content += "\n\n" + json_instruction
                    system_found = True
                    break
                    
            if not system_found:
                # Create a new system message with the JSON instruction
                messages.insert(0, Message(
                    role=MessageRole.SYSTEM,
                    content=[TextContent(text=json_instruction)]
                ))
                
        # Now generate the response
        response = await self.generate(messages, model, config, **kwargs)
        
        # Try to parse the response as JSON
        if response.text:
            try:
                # Find JSON in the response
                import re
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```|^\s*({[\s\S]*}|\[[\s\S]*\])\s*$', response.text)
                
                if json_match:
                    json_str = json_match.group(1) or json_match.group(2)
                    parsed_json = json.loads(json_str)
                    
                    # Create a pydantic model instance if response_format is a pydantic model
                    if hasattr(response_format, "model_validate"):
                        response.parsed_response = response_format.model_validate(parsed_json)
                    else:
                        response.parsed_response = parsed_json
                else:
                    # Try parsing the whole response as JSON
                    parsed_json = json.loads(response.text)
                    
                    # Create a pydantic model instance if response_format is a pydantic model
                    if hasattr(response_format, "model_validate"):
                        response.parsed_response = response_format.model_validate(parsed_json)
                    else:
                        response.parsed_response = parsed_json
                        
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                # JSON parsing failed
                response.text += f"\n\nError parsing JSON: {str(e)}"
                
        return response
    
    async def close(self):
        """Clean up resources."""
        if self.client and hasattr(self.client, 'close') and callable(self.client.close):
            await self.client.close()