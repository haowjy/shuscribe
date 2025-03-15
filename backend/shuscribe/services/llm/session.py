# shuscribe/services/llm/session.py

from typing import Dict, Optional, Type
import asyncio
import logging
from contextlib import asynccontextmanager

import httpx

from shuscribe.services.llm.providers.provider import LLMProvider

logger = logging.getLogger(__name__)

class LLMSession:
    """
    Manages LLM provider instances for client reuse.
    Uses a singleton pattern to ensure only one session exists application-wide.
    """
    _instance = None
    _lock = asyncio.Lock()
    
    def __init__(self):
        # Only called once when singleton is created
        self._providers: Dict[str, Dict[str, LLMProvider]] = {}
        self._provider_classes = {}
        self._last_used: Dict[str, Dict[str, float]] = {}  # Track last usage time
        self._max_idle_time = 3600  # 1 hour in seconds
        
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
        import time
        
        # Use "default" as the key for default API key
        key_id = api_key if api_key else "default"
        
        # Initialize tracking structures if needed
        if provider_name not in self._providers:
            self._providers[provider_name] = {}
            self._last_used[provider_name] = {}
            
        # Clean up idle providers occasionally
        await self._cleanup_idle_providers()
            
        # Create provider if it doesn't exist
        if key_id not in self._providers[provider_name]:
            provider_class = self._provider_classes[provider_name]
            self._providers[provider_name][key_id] = provider_class(api_key=api_key)
            logger.info(f"Created new {provider_name} provider instance for key_id {key_id[:4]}***")
            
        # Update last used timestamp
        self._last_used[provider_name][key_id] = time.time()
            
        return self._providers[provider_name][key_id]
    
    async def _cleanup_idle_providers(self):
        """Clean up providers that haven't been used recently to free resources."""
        import time
        
        current_time = time.time()
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
            logger.info(f"Cleaned up idle {provider_name} provider for key_id {key_id[:4]}***")
    
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
        
    async def generate(self, messages, model, provider, config=None, api_key=None, **kwargs):
        """Generate a response using the specified provider and model."""
        provider_instance = await self.get_provider(provider, api_key)
        return await provider_instance.generate(messages, model, config, **kwargs)
    
    async def generate_stream(self, messages, model, provider, config=None, api_key=None, **kwargs):
        """Generate a streaming response using the specified provider and model."""
        provider_instance = await self.get_provider(provider, api_key)
        
        # Get the stream from the provider
        stream = provider_instance.generate_stream(messages, model, config, **kwargs)
        
        # Yield each chunk from the stream
        async for chunk in stream:
            yield chunk
    
    async def parse(self, messages, model, provider, response_format, config=None, api_key=None, **kwargs):
        """Parse structured output using the specified provider and model."""
        provider_instance = await self.get_provider(provider, api_key)
        return await provider_instance.parse(messages, model, response_format, config, **kwargs)
            
    async def close(self):
        """Close all provider clients and release resources."""
        for _, providers in self._providers.items():
            for _, provider in providers.items():
                if hasattr(provider, 'close') and callable(provider.close):
                    await provider.close()
        self._providers = {}
        
        
# New class to manage streaming sessions
class StreamingSessionManager:
    def __init__(self):
        self._sessions = {}
        
    async def create_session(self, session_id, provider_name, api_key, messages, model, config):
        # Store session parameters and current state
        self._sessions[session_id] = {
            "provider_name": provider_name,
            "api_key": api_key, 
            "messages": messages,
            "model": model,
            "config": config,
            "current_output": "",
            "status": "active"
        }
        
    async def get_session(self, session_id):
        return self._sessions.get(session_id)
        
    async def update_session(self, session_id, new_content):
        if session_id in self._sessions:
            self._sessions[session_id]["current_output"] += new_content
            
    async def complete_session(self, session_id):
        if session_id in self._sessions:
            self._sessions[session_id]["status"] = "completed"
            
    async def close_session(self, session_id):
        if session_id in self._sessions:
            del self._sessions[session_id]
            
    async def get_active_sessions(self):
        return [session for session in self._sessions.values() if session["status"] == "active"]


# class KeyManager:
#     def __init__(self):
#         self._org_keys = {}  # Your organization's keys
#         self._user_rate_limits = {}  # Track user usage against rate limits
        
#     async def get_appropriate_key(self, user_id, provider_name, operation_type):
#         """
#         Determine whether to use user's key or organization key based on:
#         - User tier (free vs paid)
#         - Operation type (quick query vs. long-running agent)
#         - Current rate limit status
#         """
#         user_tier = await self._get_user_tier(user_id)
        
#         if user_tier == "free" and self._is_premium_operation(operation_type):
#             # For free users doing premium operations, use rate-limited org key
#             return self._get_rate_limited_org_key(provider_name)
#         elif user_tier == "paid":
#             # For paid users, use org key with appropriate rate limit
#             return self._get_paid_tier_org_key(provider_name)
#         else:
#             # Default to user's own key
#             return await self._get_user_key(user_id, provider_name)