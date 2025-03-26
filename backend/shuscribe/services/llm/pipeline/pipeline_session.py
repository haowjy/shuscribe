from datetime import datetime as dt
import asyncio

from shuscribe.schemas.pipeline import StreamStatus
from shuscribe.services.llm.pipeline.base_pipeline import Pipeline

class PipelineSession:
    """Manages a single pipeline execution session"""
    
    def __init__(self, session_id: str, pipeline_id: str, pipeline: Pipeline, user_id: str):
        self.session_id = session_id
        self.pipeline_id = pipeline_id
        self.pipeline = pipeline
        self.user_id = user_id
        self.created_at = dt.now()
        self.last_active = dt.now()
        self.status = StreamStatus.INITIALIZING
        self._generator = None
        self._lock = asyncio.Lock()
        
    async def start(self):
        """Start the pipeline execution"""
        async with self._lock:
            if self._generator is None:
                # Store the generator itself, not the coroutine
                generator_coroutine = self.pipeline.run()
                # Await the coroutine to get the actual generator
                self._generator = await generator_coroutine
                self.status = StreamStatus.ACTIVE
    
    def __aiter__(self):
        """Allow this session to be used as an async iterator"""
        return self
        
    async def __anext__(self):
        """Get the next chunk from the pipeline"""
        if self._generator is None:
            raise StopAsyncIteration
            
        try:
            # Now we can iterate over the generator directly
            chunk = await self._generator.__anext__()
            self.last_active = dt.now()
            
            if chunk.status in (StreamStatus.COMPLETE, StreamStatus.ERROR):
                self.status = chunk.status
                
            return chunk
        except StopAsyncIteration:
            self.status = StreamStatus.COMPLETE
            raise
        except Exception as e:
            self.status = StreamStatus.ERROR
            # Re-raise as a StopAsyncIteration to end the iteration
            raise StopAsyncIteration from e
        
    async def cancel(self):
        """Cancel the pipeline execution"""
        if self._generator is not None:
            await self._generator.aclose()
            self._generator = None
            self.status = StreamStatus.ERROR
            raise StopAsyncIteration
        
    @property
    def is_running(self) -> bool:
        """Check if the pipeline is running"""
        return self._generator is not None
    
    @property
    def is_complete(self) -> bool:
        """Check if the pipeline is complete"""
        return self.status == StreamStatus.COMPLETE
    
    @property
    def has_error(self) -> bool:
        """Check if the pipeline has an error"""
        return self.status == StreamStatus.ERROR
    