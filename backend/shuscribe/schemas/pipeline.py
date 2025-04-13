# shuscribe/schemas/pipeline.py

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

from shuscribe.schemas.base import Promptable
from shuscribe.schemas.llm import GenerationConfig, ThinkingConfig
from shuscribe.schemas.provider import ProviderName
from shuscribe.schemas.streaming import StreamChunk, StreamStatus

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
    genres: Optional[List[str]] = None
    additional_tags: Optional[List[str]] = None
    chapter_files: Optional[List[str]] = None # List of chapter file names
    
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
    provider_name: Optional[ProviderName] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    thinking_config: Optional[ThinkingConfig] = None
    max_output_tokens: Optional[int] = None
    
    def to_generation_config(self) -> GenerationConfig:
        return GenerationConfig(
            provider=self.provider_name,
            model=self.model,
            temperature=self.temperature,
            thinking_config=self.thinking_config,
            max_output_tokens=self.max_output_tokens
        )
    
class WikiGenPipelineConfig(BaseModel):
    summary_config: Optional[PipelineStepConfig] = None
    entity_extraction_config: Optional[PipelineStepConfig] = None
    entity_upsert_config: Optional[PipelineStepConfig] = None
    wiki_generation_config: Optional[PipelineStepConfig] = None
    start_chapter_idx: int = Field(default=0, description="The chapter index to start the pipeline from")
    end_chapter_idx: Optional[int] = None
    story_name: str = Field(default="pokemon_amber", description="The name of the story")
    story_dir: Path = Field(default=Path("../tests/resources"), description="The directory to save the story to")
    
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