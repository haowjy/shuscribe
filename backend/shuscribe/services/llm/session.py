# shuscribe/services/llm/session.py

from typing import Dict, Optional, Any, List, AsyncIterator, Union, Tuple
import asyncio
import logging
import time
from contextlib import asynccontextmanager

from shuscribe.services.llm.interfaces import GenerationConfig, Message
from shuscribe.services.llm.providers.provider import LLMProvider, ProviderName
from shuscribe.services.llm.streaming import StreamSession, StreamChunk, StreamStatus

logger = logging.getLogger(__name__)

class LLMSession:
    """
    Manages LLM provider instances and streaming sessions for client reuse.
    Uses a singleton pattern to ensure only one session exists application-wide.
    """
    _instance = None
    _lock = asyncio.Lock()
    
    def __init__(self):
        # Only called once when singleton is created
        self._providers: Dict[str, Dict[str, LLMProvider]] = {}
        self._provider_classes = {}
        self._last_used: Dict[str, Dict[str, float]] = {}  # Track last usage time
        self._streaming_sessions: Dict[str, StreamSession] = {}  # Track active streaming sessions
        self._max_idle_time = 3600  # 1 hour in seconds for providers
        self._max_session_idle_time = 1800  # 30 minutes for streaming sessions
        
    @classmethod
    async def get_instance(cls):
        """Get or create the singleton instance."""
        async with cls._lock:
            if cls._instance is None:
                cls._instance = LLMSession()
                await cls._instance._initialize()
            return cls._instance
    
    async def _initialize(self):
        """Initialize the session by registering provider classes."""
        # Import here to avoid circular imports
        from shuscribe.services.llm.providers.openai_provider import OpenAIProvider
        from shuscribe.services.llm.providers.anthropic_provider import AnthropicProvider
        from shuscribe.services.llm.providers.gemini_provider import GeminiProvider
        
        self._provider_classes = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "gemini": GeminiProvider,
        }
        
    async def get_provider(self, provider_name: str, api_key: Optional[str] = None) -> LLMProvider:
        """Get a provider instance with improved resource management."""
        # Use "default" as the key for default API key
        key_id = api_key if api_key else "default"
        
        # Initialize tracking structures if needed
        if provider_name not in self._providers:
            self._providers[provider_name] = {}
            self._last_used[provider_name] = {}
            
        # Clean up idle providers and sessions occasionally
        await self._cleanup_idle_resources()
            
        # Create provider if it doesn't exist
        if key_id not in self._providers[provider_name]:
            provider_class = self._provider_classes[provider_name]
            self._providers[provider_name][key_id] = provider_class(api_key=api_key)
            logger.info(f"Created new {provider_name} provider instance for key_id {key_id[:4] if key_id != 'default' else 'default'}***")
            
        # Update last used timestamp
        self._last_used[provider_name][key_id] = time.time()
            
        return self._providers[provider_name][key_id]
    
    async def _cleanup_idle_resources(self):
        """Clean up providers and streaming sessions that haven't been used recently."""
        current_time = time.time()
        
        # Clean up idle providers
        providers_to_remove = []
        for provider_name, providers in self._providers.items():
            for key_id, provider in providers.items():
                last_used = self._last_used.get(provider_name, {}).get(key_id, 0)
                if current_time - last_used > self._max_idle_time:
                    providers_to_remove.append((provider_name, key_id, provider))
                    
        for provider_name, key_id, provider in providers_to_remove:
            if hasattr(provider, 'close') and callable(provider.close):
                try:
                    await provider.close()
                except Exception as e:
                    logger.warning(f"Error closing provider {provider_name}: {str(e)}")
                    
            del self._providers[provider_name][key_id]
            del self._last_used[provider_name][key_id]
            logger.info(f"Cleaned up idle {provider_name} provider for key_id {key_id[:4] if key_id != 'default' else 'default'}***")
        
        # Clean up idle streaming sessions
        sessions_to_remove = []
        for session_id, session in self._streaming_sessions.items():
            # Check if session has been idle too long
            if session.is_complete or session.has_error or (current_time - session.last_active > self._max_session_idle_time):
                sessions_to_remove.append(session_id)
                
        for session_id in sessions_to_remove:
            await self._cleanup_streaming_session(session_id)
    
    @classmethod
    @asynccontextmanager
    async def session_scope(cls):
        """
        Context manager for using the LLM session.
        Ensures proper cleanup of resources when session is done.
        
        Usage:
            async with LLMSession.session_scope() as session:
                provider = await session.get_provider("openai")
        """
        session = await cls.get_instance()
        try:
            yield session
        finally:
            # Any cleanup needed when session is done
            pass
        
    async def generate(self, provider_name: ProviderName | str, model: str, messages: List[Message | str], config: Optional[GenerationConfig] = None, api_key: Optional[str] = None, **kwargs):
        """Generate a response using the specified provider and model."""
        if isinstance(provider_name, str):
            provider_name = ProviderName(provider_name)
        provider_instance = await self.get_provider(provider_name, api_key)
        return await provider_instance.generate(messages, model, config, **kwargs)
    
    async def create_streaming_session(
        self, 
        provider_name: ProviderName, 
        model: str, 
        messages: List[Message | str], 
        config: Optional[GenerationConfig] = None, 
        api_key: Optional[str] = None, 
        session_id: Optional[str] = None,
        resume_text: Optional[str] = None,
        **kwargs
    ) -> Tuple[str, StreamSession]:
        """Create a new streaming session."""
        provider_instance = await self.get_provider(provider_name, api_key)
        
        # Create a new streaming session
        session = StreamSession(session_id)
        if resume_text:
            session.accumulated_text = resume_text
            
        # Store the session
        self._streaming_sessions[session.session_id] = session
        
        # Start the session
        await session.start(provider_instance, model, messages, config)
        
        return session.session_id, session
    
    async def generate_stream(
        self, 
        provider_name: ProviderName | str,
        model: str, 
        messages: List[Message | str],
        config: Optional[GenerationConfig] = None,
        api_key: Optional[str] = None,
        session_id: Optional[str] = None,
        resume_text: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Generate a streaming response using the specified provider and model."""
        if isinstance(provider_name, str):
            provider_name = ProviderName(provider_name)
        # Create a streaming session with the new parameter order
        _, stream_session = await self.create_streaming_session(
            provider_name, model, messages, config, 
            api_key, session_id, resume_text, **kwargs
        )
        
        # Yield text chunks from the streaming session
        async for chunk in stream_session:
            yield chunk
    
    def get_streaming_session(self, session_id: str) -> Optional[StreamSession]:
        """Get an existing streaming session by ID."""
        return self._streaming_sessions.get(session_id)
    
    async def pause_streaming_session(self, session_id: str) -> bool:
        """Pause a streaming session."""
        session = self._streaming_sessions.get(session_id)
        if session and session.is_active:
            session.pause()
            return True
        return False
    
    async def resume_streaming_session(self, session_id: str) -> bool:
        """Resume a paused streaming session."""
        session = self._streaming_sessions.get(session_id)
        if session and session.status == StreamStatus.PAUSED:
            await session.resume()
            return True
        return False
    
    async def cancel_streaming_session(self, session_id: str) -> bool:
        """Cancel a streaming session."""
        session = self._streaming_sessions.get(session_id)
        if session and session.is_active:
            await session.cancel()
            return True
        return False
    
    async def _cleanup_streaming_session(self, session_id: str) -> bool:
        """Internal method to clean up a streaming session."""
        session = self._streaming_sessions.get(session_id)
        if not session:
            return False
            
        # Cancel if still active
        if session.is_active:
            await session.cancel()
            
        # Remove from sessions
        del self._streaming_sessions[session_id]
        logger.info(f"Cleaned up streaming session {session_id}")
        return True
    
    async def cleanup_streaming_session(self, session_id: str) -> bool:
        """Cleanup a streaming session."""
        return await self._cleanup_streaming_session(session_id)
    
    async def get_active_streaming_sessions(self) -> List[Dict[str, Any]]:
        """Get all active streaming sessions."""
        result = []
        for session_id, session in self._streaming_sessions.items():
            if session.is_active:
                result.append({
                    "session_id": session_id,
                    "provider": session.provider.__class__.__name__ if session.provider else None,
                    "model": session.model,
                    "status": session.status,
                    "accumulated_text_length": len(session.accumulated_text),
                    "created_at": session.created_at,
                    "last_active": session.last_active
                })
        return result

    async def close(self):
        """Close all provider clients and cancel all streaming sessions."""
        # Cancel all streaming sessions
        for session_id in list(self._streaming_sessions.keys()):
            await self._cleanup_streaming_session(session_id)
            
        # Close all providers
        for provider_name, providers in self._providers.items():
            for key_id, provider in providers.items():
                if hasattr(provider, 'close') and callable(provider.close):
                    try:
                        await provider.close()
                    except Exception as e:
                        logger.warning(f"Error closing provider {provider_name}: {str(e)}")
        
        self._providers = {}
        self._last_used = {}