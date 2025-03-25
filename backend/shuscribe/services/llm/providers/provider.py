# shuscribe/services/llm/providers/provider.py

from abc import abstractmethod
from typing import AsyncGenerator, List, Any, Optional, Sequence, TypeVar, Callable, Awaitable
import asyncio
import random
import logging

from shuscribe.schemas.llm import EmbeddingConfig, Message, MessageRole, GenerationConfig, Capabilities
from shuscribe.schemas.provider import LLMResponse

from shuscribe.services.llm.streaming import StreamManager, StreamSession
from shuscribe.services.llm.errors import ErrorCategory, LLMProviderException, RetryConfig
from shuscribe.services.llm.interfaces import StreamingProvider

T = TypeVar('T')
logger = logging.getLogger(__name__)

    
class LLMProvider(StreamingProvider):
    """Base provider with new streaming support"""
    
    def __init__(self, api_key: Optional[str] = None, retry_config: Optional[RetryConfig] = None):
        self.api_key = api_key
        self.stream_manager = StreamManager()
        self.retry_config = retry_config or RetryConfig(enabled=False)
        self._client = self._initialize_client()
    
    @property
    @abstractmethod
    def client(self) -> Any:
        """Get the provider-specific client instance.
        TODO: implement this in the provider classes to return the actual client instance type
        """
        return self._client

    @abstractmethod
    def capabilities(self) -> Capabilities:
        """Get the provider capabilities"""
        return Capabilities()
    
    
    @abstractmethod
    def _initialize_client(self) -> Any:
        """Initialize the provider client"""
        pass
    
    async def _with_retry(
        self, 
        func: Callable[..., Awaitable[T]], 
        *args, 
        retry_config: Optional[RetryConfig] = None,
        **kwargs
    ) -> T:
        """
        Execute a function with retry logic
        
        Args:
            func: Async function to execute
            retry_config: Optional override for retry configuration
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            The function result
            
        Raises:
            LLMProviderException: If all retries failed
        """
        config = retry_config or self.retry_config
        
        if not config.enabled:
            # Retries disabled, just run once
            return await func(*args, **kwargs)
        
        # Retries enabled
        attempt = 0
        last_exception = None
        
        while attempt <= config.max_retries:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                attempt += 1
                # Convert to our exception type
                if not isinstance(e, LLMProviderException):
                    exception = self._handle_provider_error(e)
                else:
                    exception = e
                
                last_exception = exception
                
                # If not retryable or we've hit max retries, raise
                if not exception.is_retryable() or attempt > config.max_retries:
                    raise exception
                
                # Calculate backoff with jitter
                delay = min(
                    config.max_delay,
                    config.min_delay * (config.backoff_factor ** (attempt - 1))
                )
                # Add jitter (±25%)
                jitter = random.uniform(0.75, 1.25)
                delay *= jitter
                
                # If provider gave specific retry-after, use that instead
                if exception.retry_after is not None:
                    delay = exception.retry_after
                
                logger.warning(
                    f"Retrying {func.__name__} after error: {exception.message}. "
                    f"Attempt {attempt}/{config.max_retries}. "
                    f"Waiting {delay:.2f}s"
                )
                
                await asyncio.sleep(delay)
        
        if last_exception:
            raise last_exception
        else:
            # Should never get here, but just in case
            raise LLMProviderException(
                message="Maximum retries exceeded with no specific error",
                code="max_retries_exceeded",
                category=ErrorCategory.UNKNOWN,
                provider=self.__class__.__name__
            )
    
    @abstractmethod
    def _handle_provider_error(self, exception: Exception) -> LLMProviderException:
        """
        Convert provider-specific exceptions to our exception types
        Must be implemented by each provider
        """
        pass
    
    def embed(
        self, 
        text: str, 
        config: Optional[EmbeddingConfig] = None
    ) -> List[float]:
        """Embed a text"""
        raise NotImplementedError("Embedding is not implemented for this provider")
    
    # Update generate method to use retry
    async def generate(
        self, 
        messages: Sequence[Message | str],
        model: str,
        config: Optional[GenerationConfig] = None
    ) -> LLMResponse:
        """Generate a complete response with retry support"""
        config = config or GenerationConfig()
        retry_config = config.retry_config or self.retry_config
        
        t_messages = []
        if isinstance(messages, list):
            for item in messages:
                if isinstance(item, str):
                    t_messages.append(Message(role=MessageRole.USER, content=item))
                else:
                    t_messages.append(item)
        
        return await self._with_retry(
            self._generate_internal,
            messages=t_messages,
            model=model,
            config=config,
            retry_config=retry_config
        )
    
    @abstractmethod
    async def _generate_internal(
        self, 
        messages: List[Message | str],
        model: str,
        config: Optional[GenerationConfig] = None
    ) -> LLMResponse:
        """Internal method for actual generation"""
        pass
    
    @abstractmethod
    async def _stream_generate(
        self, 
        messages: List[Message | str],
        model: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]:
        """Internal method to generate raw text chunks"""
        pass
    
    async def generate_stream(
        self,
        messages: List[Message | str],
        model: str,
        config: Optional[GenerationConfig] = None,
        session_id: Optional[str] = None,
        resume_text: Optional[str] = None
    ) -> StreamSession:
        """Create and return a streaming session"""
        return await self.stream_manager.create_session(
            provider=self,
            messages=messages,
            model=model,
            config=config,
            session_id=session_id,
            resume_text=resume_text
        )
    
    def get_stream_session(self, session_id: str) -> Optional[StreamSession]:
        """Get an existing stream session by ID"""
        return self.stream_manager.get_session(session_id)
    
    async def cleanup_stream_session(self, session_id: str) -> bool:
        """Clean up a stream session"""
        return await self.stream_manager.cleanup_session(session_id)
    
    async def close(self):
        """Clean up resources"""
        # Stop all active streaming sessions
        await self.stream_manager.stop_all_sessions()