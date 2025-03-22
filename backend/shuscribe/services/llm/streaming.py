# shuscribe/services/llm/streaming.py

import asyncio
import time
import traceback
import uuid
from typing import Dict, Any, Optional, List, Sequence
import logging

from shuscribe.services.llm.interfaces import StreamingProvider, Message, GenerationConfig
from shuscribe.schemas.streaming import StreamChunk, StreamEvent, StreamStatus

logger = logging.getLogger(__name__)

# Define the StreamSession class
class StreamSession:
    """
    A class to manage a streaming session for LLM responses, supporting asynchronous iteration and SSE.
    """
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize a new streaming session.

        Args:
            session_id (Optional[str]): A unique identifier for the session. If None, a UUID is generated.
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = "anonymous"  # Default user ID, overridden during creation
        self.accumulated_text = ""  # Accumulated text from all chunks
        self.tool_calls: List[Dict[str, Any]] = []  # List of tool calls, if any
        self.error: Optional[str] = None  # Error message, if any
        self._queue: asyncio.Queue[StreamChunk] = asyncio.Queue()  # Queue for streaming chunks
        self.created_at: float = time.time()  # Timestamp of session creation
        self.last_active: float = time.time()  # Timestamp of last activity
        self.metadata: Dict[str, Any] = {}  # Additional metadata
        
        self.status: StreamStatus = StreamStatus.INITIALIZING  # Initial status
        
        # Streaming configuration
        self.provider: Optional[StreamingProvider] = None
        self.model: Optional[str] = None
        self.messages: Sequence[Message | str] = []
        self.config: Optional[GenerationConfig] = None
        self._task: Optional[asyncio.Task] = None  # Task running the stream
        self._cancel_requested: bool = False  # Flag to indicate cancellation

    async def start(
        self,
        provider: StreamingProvider,
        model: str,
        messages: Sequence[Message | str],
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> 'StreamSession':
        """
        Start the streaming session with the given provider, model, messages, and configuration.

        Args:
            provider (StreamingProvider): The LLM provider instance.
            model (str): The model to use for generation.
            messages (List[Message | str]): The input messages for the stream.
            config (Optional[GenerationConfig]): Configuration for generation. Defaults to None.

        Returns:
            StreamSession: The current instance for method chaining.
        """
        self.provider = provider
        self.model = model
        self.messages = messages
        self.config = config or GenerationConfig()
        self.status = StreamStatus.ACTIVE
        self.last_active = time.time()
        self._task = asyncio.create_task(self._run_stream())
        return self

    async def _run_stream(self):
        """
        Core method to run the streaming process and populate the queue with chunks.
        """
        try:
            if self.model is None:
                raise ValueError("Model is not set")
            if self.provider is None:
                raise ValueError("Provider is not set")
            
            # Stream chunks from the provider
            async for event in self.provider._stream_generate(
                messages=self.messages,
                model=self.model,
                config=self.config or GenerationConfig()
            ):
                self.accumulated_text += event.text
                self.usage = event.usage
                self.last_active = time.time()
                
                # Create a StreamChunk and add it to the queue
                stream_chunk = StreamChunk(
                    event=event,
                    # accumulated_text=self.accumulated_text, # no accumulated text except for the final chunk
                    status=self.status,
                    session_id=self.session_id,
                    tool_calls=self.tool_calls,
                    metadata=self.metadata
                )
                await self._queue.put(stream_chunk)
            
            # Mark stream as complete and add final chunk
            self.status = StreamStatus.COMPLETE
            final_chunk = StreamChunk(
                event=StreamEvent(
                    type="complete",
                    text="",
                    usage=self.usage,
                ),
                accumulated_text=self.accumulated_text,
                status=StreamStatus.COMPLETE,
                session_id=self.session_id,
                tool_calls=self.tool_calls,
                metadata=self.metadata
            )
            # print("FINAL CHUNK", final_chunk)
            await self._queue.put(final_chunk)
            
            # Optional: Save to database (placeholder)
            try:
                # TODO: Implement database module
                from shuscribe.services.db.session import save_stream_result  # type: ignore
                await save_stream_result(self.session_id, self.accumulated_text)
            except ImportError:
                logger.warning("Database module not implemented. Skipping save.")
            
        except Exception as e:
            self.error = str(e)
            self.status = StreamStatus.ERROR
            logger.error(f"Stream error in session {self.session_id}: {self.error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            error_chunk = StreamChunk(
                event=StreamEvent(
                    type="error",
                    text="",
                    usage=None,
                ),
                accumulated_text=self.accumulated_text,
                status=StreamStatus.ERROR,
                session_id=self.session_id,
                error=self.error,
                tool_calls=self.tool_calls,
                metadata=self.metadata
            )
            await self._queue.put(error_chunk)

    def __aiter__(self):
        """
        Return the asynchronous iterator object.

        Returns:
            StreamSession: Self as the iterator.
        """
        return self

    async def __anext__(self) -> StreamChunk:
        """
        Retrieve the next chunk from the stream.

        Returns:
            StreamChunk: The next chunk of streamed data.

        Raises:
            StopAsyncIteration: When the stream is complete and no more chunks are available.
        """
        if self.status == StreamStatus.COMPLETE and self._queue.empty():
            raise StopAsyncIteration
        
        chunk = await self._queue.get()
        self.last_active = time.time()
        
        # Return the chunk first
        return_chunk = chunk
        
        # Then check if this was the final chunk - if so, mark for next iteration to stop
        if chunk.status in (StreamStatus.COMPLETE, StreamStatus.ERROR) and self._queue.empty():
            self.status = StreamStatus.COMPLETE
        
        return return_chunk

    def pause(self):
        """Pause the stream if it is active."""
        if self.status == StreamStatus.ACTIVE:
            self.status = StreamStatus.PAUSED
            self.last_active = time.time()

    async def resume(self):
        """Resume a paused stream."""
        if self.status == StreamStatus.PAUSED:
            self.status = StreamStatus.ACTIVE
            self.last_active = time.time()

    async def cancel(self):
        """Cancel the stream and clean up resources."""
        self._cancel_requested = True
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
    def is_active(self) -> bool:
        """
        Check if the stream is currently active or paused.

        Returns:
            bool: True if the stream is active or paused, False otherwise.
        """
        return self.status in (StreamStatus.ACTIVE, StreamStatus.PAUSED)

    @property
    def is_complete(self) -> bool:
        """
        Check if the stream has completed.

        Returns:
            bool: True if the stream is complete, False otherwise.
        """
        return self.status == StreamStatus.COMPLETE

    @property
    def has_error(self) -> bool:
        """
        Check if the stream encountered an error.

        Returns:
            bool: True if the stream has an error, False otherwise.
        """
        return self.status == StreamStatus.ERROR

# StreamManager class (unchanged from your original code, included for completeness)
class StreamManager:
    """Manages multiple streaming sessions."""
    
    def __init__(self):
        """Initialize the stream manager."""
        self._sessions = {}
    
    async def create_session(
        self, 
        provider: StreamingProvider, 
        messages: Sequence[Message | str], 
        model: str, 
        config: Optional[GenerationConfig] = None,
        session_id: Optional[str] = None,
        resume_text: Optional[str] = None
    ) -> StreamSession:
        """Create a new streaming session."""
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
            if session.is_active:
                await session.cancel()
            del self._sessions[session_id]
            return True
        return False
    
    async def cleanup_completed_sessions(self, max_age_seconds: int = 3600):
        """Remove completed sessions older than max_age_seconds."""
        # Implementation could track session creation time and clean up old ones
        pass
    
    async def stop_all_sessions(self):
        """Stop all active sessions."""
        for session in self._sessions.values():
            if session.is_active:
                await session.cancel()