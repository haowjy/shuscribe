# shuscribe/services/llm/streaming.py

import asyncio
import time
import traceback
import uuid
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field
import logging

from shuscribe.services.llm.interfaces import StreamingProvider, Message, GenerationConfig

logger = logging.getLogger(__name__)

class StreamStatus(str, Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETE = "complete"
    ERROR = "error"

class StreamChunk(BaseModel):
    text: str
    accumulated_text: str = Field(default="")
    status: StreamStatus
    session_id: str
    error: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StreamSession:
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.accumulated_text = ""
        self.tool_calls: List[Dict[str, Any]] = []
        self.error: Optional[str] = None
        self._queue: asyncio.Queue[StreamChunk] = asyncio.Queue()
        self.created_at: float = time.time()
        self.last_active: float = time.time()
        self.metadata: Dict[str, Any] = {}
        
        self.status: StreamStatus = StreamStatus.INITIALIZING
        
        self.provider: StreamingProvider
        self.model: str
        self.messages: List[Message | str]
        self.config: GenerationConfig
        self._task: asyncio.Task
    
    async def start(self, provider: StreamingProvider, model: str,  messages: List[Message | str], config: Optional[GenerationConfig] = None) -> 'StreamSession':
        self.provider: StreamingProvider = provider
        self.model: str = model
        self.messages: List[Message | str] = messages
        self.config: GenerationConfig = config or GenerationConfig()
        self.status: StreamStatus = StreamStatus.ACTIVE
        self.last_active: float = time.time()
        self._task: asyncio.Task = asyncio.create_task(self._run_stream())
        return self
    
    async def _run_stream(self):
        """Run the streaming process and handle each chunk."""
        try:
            # Call the provider's internal streaming method
            if self.model is None:
                raise ValueError("Model is not set")
            if self.provider is None:
                raise ValueError("Provider is not set")
            
            async for chunk in self.provider._stream_generate(
                messages=self.messages,
                model=self.model,
                config=self.config
            ):
                # Add the chunk to accumulated text
                self.accumulated_text += chunk
                self.last_active = time.time()
                
                # Create a StreamChunk and put it in the queue
                await self._queue.put(StreamChunk(
                    text=chunk,
                    accumulated_text=self.accumulated_text,
                    status=self.status,
                    session_id=self.session_id,
                    tool_calls=self.tool_calls
                ))
                
                # Check if paused - wait until resumed
                while self.status == StreamStatus.PAUSED:
                    await asyncio.sleep(0.1)
                    
                    # If canceled while paused, exit
                    if self.status == StreamStatus.ERROR:
                        return
            
            # Mark as complete when done
            self.status = StreamStatus.COMPLETE
            
            # Final empty chunk to signal completion
            await self._queue.put(StreamChunk(
                text="",
                accumulated_text=self.accumulated_text,
                status=StreamStatus.COMPLETE,
                session_id=self.session_id,
                tool_calls=self.tool_calls
            ))
            
        except Exception as e:
            # Handle errors
            error_msg = str(e)
            logger.error(f"Stream error in session {self.session_id}: {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.error = error_msg
            self.status = StreamStatus.ERROR
            
            # Put error chunk in queue
            await self._queue.put(StreamChunk(
                text="",
                accumulated_text=self.accumulated_text,
                status=StreamStatus.ERROR,
                session_id=self.session_id,
                error=self.error
            ))
    
    def __aiter__(self):
        """Make the session directly iterable."""
        return self
    
    async def __anext__(self):
        """Get the next chunk from the stream."""
        if self.status == StreamStatus.COMPLETE and self._queue.empty():
            raise StopAsyncIteration
            
        # Wait for the next chunk from the queue
        chunk = await self._queue.get()
        self.last_active = time.time()
        
        # If this was the final chunk and queue is now empty, raise StopAsyncIteration
        if chunk.status in (StreamStatus.COMPLETE, StreamStatus.ERROR) and self._queue.empty():
            raise StopAsyncIteration
            
        return chunk
    
    def pause(self):
        """Pause the stream."""
        if self.status == StreamStatus.ACTIVE:
            self.status = StreamStatus.PAUSED
            self.last_active = time.time()
    
    async def resume(self):
        """Resume a paused stream."""
        if self.status == StreamStatus.PAUSED:
            self.status = StreamStatus.ACTIVE
            self.last_active = time.time()
    
    async def cancel(self):
        """Cancel the stream."""
        self.status = StreamStatus.ERROR
        self.error = "Stream canceled by user"
        self.last_active = time.time()
        
        if self._task and not self._task.done():
            self._task.cancel()
            
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    @property
    def is_active(self):
        """Check if the stream is still active."""
        return self.status == StreamStatus.ACTIVE or self.status == StreamStatus.PAUSED
    
    @property
    def is_complete(self):
        """Check if the stream has completed."""
        return self.status == StreamStatus.COMPLETE
    
    @property
    def has_error(self):
        """Check if the stream encountered an error."""
        return self.status == StreamStatus.ERROR


class StreamManager:
    """Manages multiple streaming sessions."""
    
    def __init__(self):
        """Initialize the stream manager."""
        self._sessions = {}
    
    async def create_session(
        self, 
        provider: StreamingProvider,  # Changed to interface
        messages: List[Message | str], 
        model: str, 
        config: Optional[GenerationConfig] = None,
        session_id: Optional[str] = None,
        resume_text: Optional[str] = None
    ) -> StreamSession:
        session = StreamSession(session_id)
        if resume_text:
            session.accumulated_text = resume_text
        self._sessions[session.session_id] = session
        await session.start(provider, model, messages, config)
        return session
    
    def get_session(self, session_id: str) -> Optional[StreamSession]:
        """Get a streaming session by ID."""
        return self._sessions.get(session_id)
    
    async def cleanup_session(self, session_id: str) -> bool:
        """Remove a session when no longer needed."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            
            # Cancel if still running
            if session.status in (StreamStatus.ACTIVE, StreamStatus.PAUSED):
                await session.cancel()
                
            # Remove from sessions
            del self._sessions[session_id]
            return True
            
        return False
    
    async def cleanup_completed_sessions(self, max_age_seconds: int = 3600):
        """Remove completed sessions older than max_age_seconds."""
        # Implementation would track session creation time and clean up old ones
        pass
    
    async def stop_all_sessions(self):
        """Stop all active sessions."""
        for session in self._sessions.values():
            if session.status in (StreamStatus.ACTIVE, StreamStatus.PAUSED):
                await session.cancel()