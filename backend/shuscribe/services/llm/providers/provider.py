# shuscribe/services/llm/providers/provider.py

from typing import Callable, Dict, List, Optional, AsyncIterator, Union, Any, Type, TypeVar
from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel, Field, field_validator

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"  # For tool responses

class MediaType(str, Enum):
    """Types of media that can be included in messages."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"

class ToolCallStatus(str, Enum):
    """Status of a tool call."""
    REQUESTED = "requested"  # Tool call was requested by the model
    EXECUTED = "executed"    # Tool was executed by the client
    FAILED = "failed"        # Tool execution failed

class ContentBlock(BaseModel):
    """Base class for different types of content."""
    type: MediaType

class TextContent(ContentBlock):
    """Text content in a message."""
    type: MediaType = MediaType.TEXT
    text: str

class ImageContent(ContentBlock):
    """Image content in a message."""
    type: MediaType = MediaType.IMAGE
    image_data: Union[str, bytes]
    mime_type: str

class AudioContent(ContentBlock):
    """Audio content in a message."""
    type: MediaType = MediaType.AUDIO
    audio_data: Union[str, bytes]
    mime_type: str

class VideoContent(ContentBlock):
    """Video content in a message."""
    type: MediaType = MediaType.VIDEO
    video_data: Union[str, bytes]
    mime_type: str

class Message(BaseModel):
    """A message in a conversation."""
    role: MessageRole
    content: Union[str, List[ContentBlock]]
    name: Optional[str] = None
    
    @field_validator('content', mode='before')
    def convert_string_to_text_content(cls, v):
        """Convert string content to TextContent list before validation."""
        if isinstance(v, str):
            return [TextContent(type=MediaType.TEXT, text=v)]
        elif isinstance(v, list):
            # Handle case where content might be a list of strings
            return [
                TextContent(type=MediaType.TEXT, text=item) if isinstance(item, str) 
                else item 
                for item in v
            ]
        return v

class ToolCall(BaseModel):
    """Represents a tool/function call."""
    name: str
    arguments: Dict[str, Any]
    id: Optional[str] = None
    status: ToolCallStatus = ToolCallStatus.REQUESTED
    result: Optional[Any] = None

class ToolDefinition(BaseModel):
    """Definition of a tool that can be called by the model."""
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    function: Optional[Callable] = None

class Citation(BaseModel):
    """A citation for a piece of content."""
    text: str
    source: str
    metadata: Optional[Dict[str, Any]] = None

class FinishReason(str, Enum):
    """Reasons why generation stopped."""
    COMPLETED = "completed"        # Natural completion
    MAX_TOKENS = "max_tokens"      # Reached token limit
    STOP_SEQUENCE = "stop_sequence"  # Hit a stop sequence
    TOOL_CALLS = "tool_calls"      # Model decided to call tools
    ERROR = "error"                # Something went wrong

class LLMResponse(BaseModel):
    """Response from an LLM."""
    text: Optional[str] = None
    model: str = ""
    usage: Dict[str, int] = Field(default_factory=dict)
    finish_reason: Optional[FinishReason] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)
    parsed_response: Optional[Any] = None
    raw_response: Optional[Any] = None
    citations: List[Citation] = Field(default_factory=list)
    content_blocks: List[ContentBlock] = Field(default_factory=list)
        
    @property
    def has_tool_calls(self) -> bool:
        """Check if the response includes tool calls."""
        return bool(self.tool_calls)

    def model_dump(self) -> dict:
        """Custom serialization method."""
        return {
            "text": self.text,
            "model": self.model,
            "usage": self.usage,
            "finish_reason": self.finish_reason,
            "tool_calls": [tc.model_dump() for tc in self.tool_calls],
            "parsed_response": self.parsed_response.model_dump() if self.parsed_response and hasattr(self.parsed_response, 'model_dump') else self.parsed_response,
            "citations": [c.model_dump() for c in self.citations],
            "content_blocks": [cb.model_dump() for cb in self.content_blocks]
        }

    def __str__(self) -> str:
        """Custom string representation."""
        if self.parsed_response is not None:
            return str(self.parsed_response)
        return self.text or ""

class GenerationConfig(BaseModel):
    """Configuration for text generation."""
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    top_k: Optional[int] = None
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = Field(default_factory=list)
    tools: List[ToolDefinition] = Field(default_factory=list)
    response_format: Optional[Union[Type[BaseModel], Dict[str, Any]]] = None
    system_prompt: Optional[str] = None
    stream: bool = False
    seed: Optional[int] = None
    extended_thinking: bool = False
    extended_thinking_budget: Optional[int] = None
    search_enabled: bool = False
    parallel_tool_calling: bool = True
    additional_params: Dict[str, Any] = Field(default_factory=dict)

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the provider with an API key and additional options.
        
        Args:
            api_key: The API key for the provider. If None, will attempt to use
                    environment variables or other default authentication methods.
            **kwargs: Additional provider-specific configuration options.
        """
        self._api_key = api_key
        self._client = self._initialize_client(api_key, **kwargs)
    
    @property
    @abstractmethod
    def client(self) -> Any:
        """Get the provider-specific client instance."""
        return self._client
    
    @abstractmethod
    def _initialize_client(self, api_key: Optional[str] = None, **kwargs) -> Any:
        """
        Initialize and return the provider-specific client.
        
        Each provider implementation must override this method to create
        the appropriate client instance for their API.
        """
        pass
    
    @property
    def supports_structured_output(self) -> bool:
        """Whether this provider supports structured outputs."""
        return False
    
    @property
    def supports_multimodal_input(self) -> bool:
        """Whether this provider supports multimodal inputs."""
        return False
    
    @property
    def supports_tool_use(self) -> bool:
        """Whether this provider supports tool use."""
        return False
    
    @property
    def supports_parallel_tool_calls(self) -> bool:
        """Whether this provider supports multiple tool calls in one response."""
        return False
    
    @property
    def supports_search(self) -> bool:
        """Whether this provider supports search integration."""
        return False
    
    @property
    def supports_extended_thinking(self) -> bool:
        """Whether this provider supports showing reasoning process."""
        return False
    
    @property
    def supports_citations(self) -> bool:
        """Whether this provider supports citations."""
        return False
    
    @abstractmethod
    async def generate(
        self, 
        messages: List[Message],
        model: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a response synchronously."""
        pass
    
    @abstractmethod
    async def generate_stream(
        self, 
        messages: List[Message],
        model: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> AsyncIterator[Union[str, LLMResponse]]:
        """Generate a streaming response."""
        yield ""
    
    async def parse(
        self,
        messages: List[Message],
        model: str,
        response_format: Type[BaseModel],
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Parse a response into a structured output.
        Default implementation throws NotImplementedError.
        Providers that support structured output should override this.
        """
        raise NotImplementedError(f"Provider {self.__class__.__name__} does not support structured output parsing")
    
    async def execute_tool_call(self, tool_call: ToolCall) -> Any:
        """
        Execute a tool call and return the result.
        Default implementation throws NotImplementedError.
        Providers that support tool use should override this.
        """
        raise NotImplementedError(f"Provider {self.__class__.__name__} does not support tool execution")
    
    @abstractmethod
    async def close(self):
        """Clean up resources."""
        pass