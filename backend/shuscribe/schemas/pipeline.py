# shuscribe/schemas/pipeline.py

import os
from pathlib import Path
from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel, Field, field_validator

from shuscribe.schemas.base import Promptable
from shuscribe.schemas.llm import ThinkingConfig
from shuscribe.schemas.provider import ProviderName
from shuscribe.schemas.streaming import StreamChunk, StreamStatus
from shuscribe.schemas.wikigen.entity import EntitySigLvl

# 
# SHARED INPUTS
#

class Chapter(Promptable):
    title: Optional[str] = Field(default=None, description="Title of the chapter")
    id: int = Field(description="Unique self-incrementing identifier for the chapter")
    content: str = Field(description="Content of the chapter")
    
    def to_prompt(self) -> str:
        if self.title:
            return f"\n### [{self.id}] {self.title}\n<Content>\n{self.content}\n</Content>"
        else:
            return f"\n<Content>\n{self.content}\n</Content>"

class StoryMetadata(Promptable):
    title: str
    description: Optional[str] = None
    author: Optional[str] = None
    word_count: Optional[int] = None
    genres: Optional[List[str]] = None
    additional_tags: Optional[List[str]] = None
    
    def to_prompt(self) -> str:
        p = (
            f"Title: {self.title}\n" +
            (f"Genres: {self.genres}\n" if self.genres else "") +
            (f"Additional Tags: {self.additional_tags}\n" if self.additional_tags else "") +
            (f"Description: |\n{self.description}" if self.description else "")
        )
        return p
    
#
# CONFIG
#

class PipelineStepConfig(BaseModel):
    provider_name: ProviderName
    model: str
    temperature: float = 0.7
    thinking_config: Optional[ThinkingConfig] = None
    max_output_tokens: Optional[int] = None
    
class WikiGenPipelineConfig(BaseModel):
    summary_config: PipelineStepConfig
    entity_extraction_config: PipelineStepConfig
    entity_upsert_config: PipelineStepConfig
    wiki_generation_config: PipelineStepConfig
    start_chapter_idx: int
    end_chapter_idx: int
    story_name: str
    story_dir: Path
    use_cached_responses: Optional[bool] = None  # Falls back to env var if None
    retry_from_chapter_idx: Optional[int] = None  # For restarting failed pipelines
    
    @field_validator('use_cached_responses')
    def set_cached_responses_from_env(cls, v):
        if v is None:
            return os.environ.get('USE_CACHED_RESPONSES', 'false').lower() == 'true'
        return v
    
    @field_validator('retry_from_chapter_idx')
    def validate_retry_chapter(cls, v, info):
        start = info.data.get('start_chapter_idx')
        end = info.data.get('end_chapter_idx')
        
        if v is not None and start is not None and end is not None:
            if v < start or v > end:
                raise ValueError(f"retry_from_chapter_idx must be between start_chapter_idx ({start}) and end_chapter_idx ({end})")
        return v
    
    
    
class PipelineStepInfo(BaseModel):
    """Information about a pipeline step"""
    id: str  # Unique identifier for the step
    name: str  # Display name for the step
    description: str = ""  # Optional description
    
    def __eq__(self, other):
        if isinstance(other, PipelineStepInfo):
            return self.id == other.id
        return self.id == other
    
    def __hash__(self):
        return hash(self.id)
    
    @classmethod
    def INITIALIZE(cls):
        return cls(id="INITIALIZE", name="Initialize", description="Setting up pipeline resources")
    
    @classmethod
    def ERROR(cls, error: Exception):
        return cls(id="ERROR", name="Error", description=f"Error: {error}")
    
    @classmethod
    def COMPLETE(cls):
        return cls(id="COMPLETE", name="Complete", description="Pipeline execution completed")
    

class StreamPipelineChunk(StreamChunk):
    pipeline_id: str
    step: PipelineStepInfo
    chapter: Optional[int] = None
    progress: Optional[dict] = None  # For tracking progress (e.g., {"current": 2, "total": 5})
    step_message: Optional[str] = None  # Additional context about the current step
    
    @classmethod
    def create_step_update(cls, session_id: str, pipeline_id: str, step: PipelineStepInfo, chapter: Optional[int] = None, 
                          message: Optional[str] = None, progress: Optional[dict] = None):
        """Create a step update chunk with minimal information"""
        return cls(
            text="",
            accumulated_text="",
            status=StreamStatus.ACTIVE,
            session_id=session_id,
            pipeline_id=pipeline_id,
            step=step,
            chapter=chapter,
            step_message=message,
            progress=progress
        )