"""
Story Domain Models

Handles all story content: chapters, drafts, story metadata, and publication status.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class ChapterStatus(str, Enum):
    """Chapter publication status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ChapterBase(BaseModel):
    """Base chapter schema"""
    title: str
    content: str
    chapter_number: int = Field(..., description="Chapter number (1-based)")
    word_count: int = Field(default=0, description="Automatically calculated word count")
    status: ChapterStatus = ChapterStatus.DRAFT
    summary: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def calculate_word_count(self) -> int:
        """Calculate word count from content"""
        # Simple word count - could be enhanced
        return len(self.content.split()) if self.content else 0


class ChapterCreate(ChapterBase):
    """Schema for creating chapters"""
    workspace_id: UUID


class ChapterUpdate(BaseModel):
    """Schema for updating chapters (all fields optional)"""
    title: Optional[str] = None
    content: Optional[str] = None
    chapter_number: Optional[int] = None
    status: Optional[ChapterStatus] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class Chapter(ChapterBase):
    """Complete chapter model"""
    id: UUID
    workspace_id: UUID
    version: int = Field(default=1, description="Chapter version for tracking edits")
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @property
    def is_published(self) -> bool:
        """Check if chapter is published"""
        return self.status == ChapterStatus.PUBLISHED
    
    def model_post_init(self, __context) -> None:
        """Calculate word count after model creation"""
        if self.content:
            self.word_count = self.calculate_word_count()
    
    model_config = ConfigDict(from_attributes=True)


class StoryMetadataCreate(BaseModel):
    """Schema for creating story metadata"""
    title: str = Field(..., min_length=1, description="Story title")
    author: str = Field(..., min_length=1, description="Story author")
    synopsis: Optional[str] = None
    genres: List[str] = Field(default_factory=list, description="Story genres")
    tags: List[str] = Field(default_factory=list, description="Story tags")
    total_chapters: int = Field(default=0, ge=0, description="Total planned chapters")
    publication_status: str = Field(default="draft", description="Overall publication status")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Story-specific settings")
    
    model_config = ConfigDict(from_attributes=True)


class StoryMetadataUpdate(BaseModel):
    """Schema for updating story metadata (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, description="Story title")
    author: Optional[str] = Field(None, min_length=1, description="Story author")
    synopsis: Optional[str] = None
    genres: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    total_chapters: Optional[int] = Field(None, ge=0, description="Total planned chapters")
    publication_status: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


class StoryMetadata(BaseModel):
    """Story-level metadata and information"""
    id: UUID
    workspace_id: UUID
    title: str
    author: str
    synopsis: Optional[str] = None
    genres: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    # Chapter tracking
    total_chapters: int = Field(default=0, description="Total planned chapters")
    published_chapters: int = Field(default=0, description="Currently published chapters")
    total_word_count: int = Field(default=0, description="Total story word count")
    
    # Publication info
    publication_status: str = Field(default="draft", description="Overall publication status")
    first_published_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None
    
    # Settings
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @property
    def completion_percentage(self) -> float:
        """Calculate story completion percentage"""
        if self.total_chapters == 0:
            return 0.0
        return (self.published_chapters / self.total_chapters) * 100
    
    @property
    def is_complete(self) -> bool:
        """Check if story is complete"""
        return self.total_chapters > 0 and self.published_chapters >= self.total_chapters
    
    def update_chapter_stats(self, chapters: List[Chapter]) -> None:
        """Update metadata based on current chapters"""
        published = [c for c in chapters if c.is_published]
        self.published_chapters = len(published)
        self.total_word_count = sum(c.word_count for c in chapters)
        
        if published:
            self.first_published_at = min(c.published_at for c in published if c.published_at)
            self.last_updated_at = max(c.updated_at for c in chapters if c.updated_at) or datetime.now()
    
    model_config = ConfigDict(from_attributes=True) 