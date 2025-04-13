# shuscribe/services/llm/pipeline/base_pipeline.py

from abc import ABC, abstractmethod
import traceback
from typing import AsyncGenerator, Optional
import logging

from shuscribe.schemas.pipeline import WikiGenPipelineConfig, PipelineStepInfo, StreamPipelineChunk, StreamStatus

logger = logging.getLogger(__name__)
    
class Pipeline(ABC):
    """Base class for all pipeline implementations"""
    
    def __init__(self, session_id: str, pipeline_id: str, config: WikiGenPipelineConfig):
        self.session_id = session_id
        self.pipeline_id = pipeline_id
        self.config = config
        self.current_step = PipelineStepInfo.INITIALIZE()
        self.current_chapter_idx = config.start_chapter_idx
        self.error = None
        self.is_running = False
        self.results = {}
    
    @abstractmethod
    async def run(self) -> AsyncGenerator[StreamPipelineChunk, None]:
        """Run the pipeline and yield stream chunks for progress updates"""
        pass
        
    async def update_step(self, step: PipelineStepInfo, chapter_idx: Optional[int] = None, 
                          message: Optional[str] = None) -> StreamPipelineChunk:
        """Update the current step and return a chunk for progress reporting"""
        self.current_step = step
        if chapter_idx is not None:
            self.current_chapter_idx = chapter_idx
            
        progress = {"current": self.current_chapter_idx, 
                    "total": self.config.end_chapter_idx}
        
        chunk = StreamPipelineChunk.create_step_update(
            session_id=self.session_id,
            pipeline_id=self.pipeline_id,
            step=step,
            chapter=self.current_chapter_idx,
            message=message,
            progress=progress
        )
        
        return chunk
        
    async def handle_error(self, error: Exception) -> StreamPipelineChunk:
        """Handle pipeline error and return an error chunk"""
        self.error = error
        self.is_running = False
        
        logger.error(f"Pipeline error: {error}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Create error chunk
        return StreamPipelineChunk(
            text=str(error),
            accumulated_text="",
            status=StreamStatus.ERROR,
            session_id=self.session_id,
            pipeline_id=self.pipeline_id,
            step=PipelineStepInfo.ERROR(error),
            chapter=self.current_chapter_idx,
            step_message=f"Error during {self.current_step.name}: {str(error)}\nTraceback: {traceback.format_exc()}"
        )
    