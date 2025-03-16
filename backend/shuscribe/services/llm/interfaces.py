# shuscribe/services/llm/interfaces.py
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional, Any, Type, AsyncGenerator, Union
from abc import ABC, abstractmethod

from shuscribe.services.llm.errors import RetryConfig

class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"

class Content(BaseModel):
    """Represents multimodal content that can be used in messages"""
    type: ContentType
    data: Any
    mime_type: Optional[str] = None

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

# Enhanced message to support multimodal content
class Message(BaseModel):
    role: MessageRole = Field(default=MessageRole.USER, description="The role of the message")
    content: Union[str, Content, List[Union[str, Content]]] = Field(description="The content of the message")
    name: Optional[str] = Field(default=None, description="The name of the message")

# Generic tool configurations
class SearchToolConfig(BaseModel):
    """Configuration for search tools - applicable to any provider with search capability"""
    enabled: bool = True
    
class CodeExecutionToolConfig(BaseModel):
    """Configuration for code execution - applicable to any provider with code execution"""
    enabled: bool = True
    timeout: Optional[int] = None
    allow_network_access: bool = False

class ToolType(str, Enum):
    FUNCTION = "function"
    SEARCH = "search"
    CODE_EXECUTION = "code_execution"

class ToolDefinition(BaseModel):
    """Generic tool definition that can be mapped to provider-specific formats"""
    type: ToolType = ToolType.FUNCTION
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    search_config: Optional[SearchToolConfig] = None
    code_execution_config: Optional[CodeExecutionToolConfig] = None

class ThinkingConfig(BaseModel):
    """Configuration for thinking"""
    enabled: bool = False
    budget_tokens: Optional[int] = 3200 # Anthropic Budget https://docs.anthropic.com/en/docs/about-claude/models/extended-thinking-models
    effort: Optional[Literal["low", "medium", "high"]] = "low" # OpenAI Effort https://platform.openai.com/docs/guides/reasoning?api-mode=responses
    
# Enhanced generation config
class GenerationConfig(BaseModel):
    """Provider-agnostic generation configuration"""
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    system_prompt: Optional[str] = None
    top_k: int = 0
    response_schema: Optional[Type[BaseModel]] = None # structured output
    search: bool = False  # Simple flag for backward compatibility
    parallel_tool_calling: bool = False
    tools: Optional[List[ToolDefinition]] = None
    tool_choice: Optional[str] = None
    auto_function_calling: Optional[bool] = None  # Generic automatic function calling
    stop_sequences: Optional[List[str]] = None
    retry_config: Optional[RetryConfig] = None
    context_id: Optional[str] = None  # Generic context/caching ID
    thinking_config: Optional[ThinkingConfig] = None

@dataclass
class Capabilities:
    streaming: bool = False
    structured_output: bool = False
    
    thinking: bool = False
    
    tool_calling: bool = False
    search: bool = False
    parallel_tool_calls: bool = False
    citations: bool = False
    
    caching: bool = False
    code_execution: bool = False
    multimodal: bool = False


class StreamingProvider(ABC):
    @abstractmethod
    async def _stream_generate(
        self, 
        messages: List[Message | str], 
        model: str, 
        config: GenerationConfig
    ) -> AsyncGenerator[str, None]:
        """Stream generate text completions.
        
        Returns:
            An async generator that yields string chunks.
        """
        yield ""  # This is just for type hinting, implementations will override

