# shuscribe/services/llm/session.py

from typing import Dict, Optional, Any, List, AsyncIterator, Sequence, Union, Tuple
import asyncio
import logging
from contextlib import asynccontextmanager
import uuid

from shuscribe.schemas.pipeline import StreamPipelineChunk, WikiGenPipelineConfig
from shuscribe.schemas.streaming import StreamChunk
from shuscribe.services.llm.interfaces import GenerationConfig, Message
from shuscribe.services.llm.pipeline.pipeline_session import PipelineSession
from shuscribe.services.llm.providers.provider import LLMProvider
from shuscribe.services.llm.streaming import StreamSession

from shuscribe.schemas.session import UserProviders, SessionRegistry, StreamSessionInfo
from shuscribe.schemas.provider import ProviderName
from shuscribe.services.llm.pipeline.pipeline_factory import PipelineFactory, PipelineType

logger = logging.getLogger(__name__)

class LLMSession:
    """
    Manages LLM provider instances and streaming sessions for client reuse.
    Uses a singleton pattern to ensure only one session exists application-wide.
    """
    _instance = None
    _lock = asyncio.Lock()
    
    def __init__(self):
        # Use structured Pydantic models instead of nested dictionaries
        self._user_providers: Dict[str, UserProviders] = {}  # user_id -> UserProviders
        self._sessions = SessionRegistry()
        self._provider_classes = {}
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
        
    async def get_provider(self, provider_name: ProviderName | str, api_key: Optional[str] = None, user_id: Optional[str] = None) -> LLMProvider:
        """Get a provider instance with improved resource management and user isolation."""
        key_id = api_key if api_key else "default"
        user_id = user_id if user_id else "anonymous"
        
        if isinstance(provider_name, str):
            provider_name = ProviderName(provider_name)
        
        masked_key_id = key_id
        if api_key and len(api_key) > 8:
            masked_key_id = f"{api_key[:4]}...{api_key[-4:]}"
        
        if user_id not in self._user_providers:
            self._user_providers[user_id] = UserProviders(user_id=user_id)
        
        user_providers = self._user_providers[user_id]
        provider_instance = user_providers.get_provider(provider_name, key_id)
        if provider_instance:
            user_providers.update_last_used(provider_name, key_id)
            return provider_instance.provider
        
        provider_class = self._provider_classes[provider_name]
        provider = provider_class(api_key=api_key)
        user_providers.add_provider(provider_name, key_id, provider)
        logger.info(f"Created new {provider_name} provider instance for user {user_id} with key_id {masked_key_id}")
        
        await self._cleanup_idle_resources()
        return provider
    
    async def _cleanup_idle_resources(self):
        """Clean up providers and streaming sessions that haven't been used recently."""
        for user_id, user_providers in list(self._user_providers.items()):
            max_idle_time = self._max_idle_time * 3 if user_id == "anonymous" else self._max_idle_time
            idle_providers = user_providers.get_idle_providers(max_idle_time)
            
            for provider_instance in idle_providers:
                provider = provider_instance.provider
                if hasattr(provider, 'close') and callable(provider.close):
                    try:
                        await provider.close()
                    except Exception as e:
                        logger.warning(f"Error closing provider {provider_instance.provider_name} for user {user_id}: {str(e)}")
                
                if provider_instance.provider_name in user_providers.providers:
                    if provider_instance.api_key_id in user_providers.providers[provider_instance.provider_name]:
                        del user_providers.providers[provider_instance.provider_name][provider_instance.api_key_id]
                    if not user_providers.providers[provider_instance.provider_name]:
                        del user_providers.providers[provider_instance.provider_name]
                
                logger.info(f"Cleaned up idle {provider_instance.provider_name} provider for user {user_id}")
            
            if not user_providers.providers:
                del self._user_providers[user_id]
        
        idle_sessions = self._sessions.get_idle_sessions(self._max_session_idle_time)
        for session_id in idle_sessions:
            await self._cleanup_streaming_session(session_id)
    
    @classmethod
    @asynccontextmanager
    async def session_scope(cls):
        """Context manager for using the LLM session."""
        session = await cls.get_instance()
        try:
            yield session
        finally:
            pass
        
    async def generate(self, provider_name: Union[ProviderName, str], model: str, messages: Sequence[Union[Message, str]], 
                       config: Optional[GenerationConfig] = None, api_key: Optional[str] = None, 
                       user_id: Optional[str] = None, **kwargs):
        """Generate a response using the specified provider and model with user tracking."""
        if not provider_name:
            if config and config.provider:
                provider_name = config.provider
            else:
                raise ValueError("No provider name or config provided")
        
        if isinstance(provider_name, str):
            provider_name = ProviderName(provider_name)
        
        provider_instance = await self.get_provider(provider_name, api_key, user_id)

        if not model:
            if config and config.model:
                model = config.model
            else:
                raise ValueError("No model provided")
        
        if config and user_id:
            if not config.context_id:
                config.context_id = f"user_{user_id}"
            elif f"user_{user_id}" not in config.context_id:
                config.context_id = f"user_{user_id}_{config.context_id}"
        
        return await provider_instance.generate(messages, model, config, **kwargs)
    
    async def create_streaming_session(
        self, 
        provider_name: ProviderName, 
        model: str, 
        messages: Sequence[Union[Message, str]], 
        config: Optional[GenerationConfig] = None, 
        api_key: Optional[str] = None, 
        session_id: Optional[str] = None,
        resume_text: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Tuple[str, StreamSession]:
        """Create a new streaming session with user tracking, optimized for SSE."""
        user_id = user_id if user_id else "anonymous"
        provider_instance = await self.get_provider(provider_name, api_key, user_id)
        
        session = StreamSession(session_id)
        if resume_text:
            session.accumulated_text = resume_text
        
        session.user_id = user_id
        self._sessions.add_session(session, user_id)
        
        # Start the streaming session in the background
        await session.start(provider_instance, model, messages, config, **kwargs)
        
        logger.info(f"Created streaming session {session.session_id} for user {user_id}")
        return session.session_id, session
    
    async def generate_stream(
        self, 
        provider_name: Union[ProviderName, str],
        model: str, 
        messages: Sequence[Union[Message, str]],
        config: Optional[GenerationConfig] = None,
        api_key: Optional[str] = None,
        session_id: Optional[str] = None,
        resume_text: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Generate a streaming response, compatible with SSE."""
        if not provider_name:
            if config and config.provider:
                provider_name = config.provider
            else:
                raise ValueError("No provider name or config provided")
        
        if not model:
            if config and config.model:
                model = config.model
            else:
                raise ValueError("No model provided")
        
        if isinstance(provider_name, str):
            provider_name = ProviderName(provider_name)
        
        session_id, stream_session = await self.create_streaming_session(
            provider_name, model, messages, config, api_key, session_id, resume_text, user_id, **kwargs
        )
        
        # Yield chunks as they arrive, suitable for SSE streaming
        async for chunk in stream_session:
            yield chunk
    
    def get_streaming_session(self, session_id: str) -> Optional[StreamSession]:
        """Get an existing streaming session by ID."""
        return self._sessions.get_session(session_id)
    
    # async def pause_streaming_session(self, session_id: str) -> bool:
    #     """Pause a streaming session."""
    #     session = self._sessions.get_session(session_id)
    #     if session and session.is_active:
    #         session.pause()
    #         logger.info(f"Paused streaming session {session_id}")
    #         return True
    #     return False
    
    # async def resume_streaming_session(self, session_id: str) -> bool:
    #     """Resume a paused streaming session."""
    #     session = self._sessions.get_session(session_id)
    #     if session and session.status == StreamStatus.PAUSED:
    #         await session.resume()
    #         logger.info(f"Resumed streaming session {session_id}")
    #         return True
    #     return False
    
    async def cancel_streaming_session(self, session_id: str) -> bool:
        """Cancel a streaming session."""
        session = self._sessions.get_session(session_id)
        if session and session.is_active:
            await session.cancel()
            logger.info(f"Cancelled streaming session {session_id}")
            return True
        return False
    
    async def _cleanup_streaming_session(self, session_id: str) -> bool:
        """Internal method to clean up a streaming session."""
        session = self._sessions.get_session(session_id)
        if not session:
            return False
            
        if session.is_active:
            await session.cancel()
            
        self._sessions.remove_session(session_id)
        user_id = getattr(session, 'user_id', 'anonymous')
        logger.info(f"Cleaned up streaming session {session_id} for user {user_id}")
        return True
    
    async def cleanup_streaming_session(self, session_id: str) -> bool:
        """Cleanup a streaming session."""
        return await self._cleanup_streaming_session(session_id)
    
    async def get_user_streaming_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active streaming sessions for a specific user."""
        result = []
        sessions = self._sessions.get_user_sessions(user_id)
        
        for session in sessions:
            if session.is_active:
                session_info = StreamSessionInfo(
                    session_id=session.session_id,
                    user_id=user_id,
                    provider_name=getattr(session.provider, 'provider_name', None) if session.provider else None,
                    model=session.model,
                    status=session.status,
                    accumulated_text_length=len(session.accumulated_text),
                    created_at=session.created_at,
                    last_active=session.last_active
                )
                result.append(session_info.model_dump())
                
        return result
        
    async def get_active_streaming_sessions(self) -> List[Dict[str, Any]]:
        """Get all active streaming sessions."""
        result = []
        for session_id, session in self._sessions.sessions.items():
            if session.is_active:
                user_id = getattr(session, 'user_id', 'anonymous')
                session_info = StreamSessionInfo(
                    session_id=session_id,
                    user_id=user_id,
                    provider_name=getattr(session.provider, 'provider_name', None) if session.provider else None,
                    model=session.model,
                    status=session.status,
                    accumulated_text_length=len(session.accumulated_text),
                    created_at=session.created_at,
                    last_active=session.last_active
                )
                result.append(session_info.model_dump())
        return result

# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------
# Pipeline Sessions
# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------
    
    async def create_pipeline_session(
        self,
        pipeline_config: WikiGenPipelineConfig,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        pipeline_id: Optional[str] = None,
    ) -> Tuple[str, PipelineSession]:
        """Create a new pipeline session"""
        user_id = user_id if user_id else "anonymous"
        session_id = session_id or str(uuid.uuid4())
        pipeline_id = pipeline_id or str(uuid.uuid4())
        
        # Create the pipeline instance
        pipeline = PipelineFactory.create_pipeline(
            pipeline_type=PipelineType.WIKI_GEN,
            session_id=session_id,
            pipeline_id=pipeline_id,
            config=pipeline_config
        )
        
        # Create and store the pipeline session
        pipeline_session = PipelineSession(
            session_id=session_id,
            pipeline_id=pipeline_id,
            pipeline=pipeline,
            user_id=user_id or "anonymous"
        )
        
        self._sessions.add_pipeline(pipeline_session, user_id)
        return pipeline_id, pipeline_session
    
    async def run_pipeline_stream(
        self,
        pipeline_config: WikiGenPipelineConfig, # TODO: MAKE A FACTORY FOR THIS
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        pipeline_id: Optional[str] = None,
    ) -> AsyncIterator[StreamPipelineChunk]:
        """Run a pipeline and stream its results.
        
        Args:
            pipeline_config: Configuration for the pipeline
            user_id: Optional user ID for tracking
            session_id: Optional session ID for the pipeline
            pipeline_id: Optional pipeline ID for tracking
            
        Returns:
            An async iterator that yields StreamPipelineChunk objects
        """
        pipeline_id, pipeline_session = await self.create_pipeline_session(
            pipeline_config=pipeline_config,
            user_id=user_id,
            session_id=session_id,
            pipeline_id=pipeline_id
        )
        
        # After creating the session, we should call start() before iterating
        await pipeline_session.start()
        
        # Yield chunks as they arrive from the pipeline
        async for chunk in pipeline_session:
            yield chunk
            
    def get_pipeline_session(self, pipeline_id: str) -> Optional[PipelineSession]:
        """Get an existing pipeline session by ID"""
        return self._sessions.get_pipeline(pipeline_id)
        
    async def get_user_pipeline_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all pipeline sessions for a specific user"""
        result = []
        pipelines = self._sessions.get_user_pipelines(user_id)
        
        for pipeline in pipelines:
            result.append({
                "pipeline_id": pipeline.pipeline_id,
                "user_id": user_id,
                "status": pipeline.status,
                "current_step": pipeline.pipeline.current_step.name,
                "current_chapter": pipeline.pipeline.current_chapter_idx,
                "created_at": pipeline.created_at,
                "last_active": pipeline.last_active
            })
                
        return result
    
    async def _cleanup_pipeline_session(self, pipeline_id: str) -> bool:
        """Internal method to clean up a pipeline session."""
        pipeline = self._sessions.get_pipeline(pipeline_id)
        if not pipeline:
            return False
        
        if pipeline.is_running:
            await pipeline.cancel()
            
        self._sessions.remove_pipeline(pipeline_id)
        logger.info(f"Cleaned up pipeline session {pipeline_id}")
        return True

    async def close(self):
        """Close all provider clients and cancel all streaming sessions."""
        for session_id in list(self._sessions.sessions.keys()):
            await self._cleanup_streaming_session(session_id)
            
        for pipeline_id in list(self._sessions.pipelines.keys()):
            await self._cleanup_pipeline_session(pipeline_id)
            
        for user_id, user_providers in self._user_providers.items():
            for provider_dict in user_providers.providers.values():
                for provider_instance in provider_dict.values():
                    provider = provider_instance.provider
                    if hasattr(provider, 'close') and callable(provider.close):
                        try:
                            await provider.close()
                        except Exception as e:
                            logger.warning(f"Error closing provider {provider_instance.provider_name}: {str(e)}")
        
        self._user_providers = {}
        self._sessions = SessionRegistry()
        
        
        
