"""
Story Domain Models

Handles all story content: chapters, drafts, story metadata, and publication status.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Iterator, Tuple
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from src.utils import count_tokens


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
    
    @classmethod
    def create_empty(cls) -> 'ChapterBase':
        """Create an empty chapter instance"""
        return cls(
            chapter_number=0,
            title="",
            content=""
        )


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
    updated_at: datetime
    
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
    workspace_id: UUID
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


class FullStoryBase(BaseModel):
    """Base model for complete story with chapters"""
    metadata: StoryMetadata
    chapters: List[Chapter] = Field(default_factory=list)
    
    def __init__(self, **data):
        super().__init__(**data)
        self._cached_total_tokens: Optional[int] = None
    
    @property
    def total_chapters(self) -> int:
        """Get total number of chapters"""
        return len(self.chapters)
    
    @property
    def word_count(self) -> int:
        """Calculate total word count across all chapters"""
        return sum(chapter.word_count for chapter in self.chapters)
    
    @property
    def total_tokens(self) -> int:
        """Calculate total token count across all chapters (cached)"""
        if not hasattr(self, '_cached_total_tokens') or self._cached_total_tokens is None:
            full_content = self.get_full_content()
            self._cached_total_tokens = count_tokens(full_content)
        return self._cached_total_tokens
    
    @property
    def is_short_story(self) -> bool:
        """Determine if this is a short story (< 15,000 words)"""
        return self.word_count < 15000
    
    def get_content_chunks(self, chunk_token_limit: int) -> Iterator[Tuple[List[Chapter], str, int]]:
        """
        Yield chunks of chapters that fit within the token limit.
        
        Args:
            chunk_token_limit: Maximum tokens per chunk
            
        Yields:
            Tuple of (chapters_in_chunk, formatted_content, actual_token_count)
        """
        if not self.chapters:
            return
            
        sorted_chapters = sorted(self.chapters, key=lambda c: c.chapter_number)
        current_chunk_chapters = []
        current_chunk_tokens = 0
        
        for chapter in sorted_chapters:
            chapter_content = f"# Chapter {chapter.chapter_number}: {chapter.title}\n\n{chapter.content}"
            chapter_tokens = count_tokens(chapter_content)
            
            if current_chunk_tokens + chapter_tokens > chunk_token_limit and current_chunk_chapters:
                chunk_content = "\n\n".join([
                    f"# Chapter {c.chapter_number}: {c.title}\n\n{c.content}" 
                    for c in current_chunk_chapters
                ])
                yield (current_chunk_chapters, chunk_content, current_chunk_tokens)
                
                current_chunk_chapters = [chapter]
                current_chunk_tokens = chapter_tokens
            else:
                current_chunk_chapters.append(chapter)
                current_chunk_tokens += chapter_tokens
        
        if current_chunk_chapters:
            chunk_content = "\n\n".join([
                f"# Chapter {c.chapter_number}: {c.title}\n\n{c.content}" 
                for c in current_chunk_chapters
            ])
            yield (current_chunk_chapters, chunk_content, current_chunk_tokens)
    
    def get_full_content(self) -> str:
        """
        Get the complete story content formatted with chapter headers.
        
        Returns:
            Concatenated content of all chapters with chapter headers
        """
        if not self.chapters:
            return ""
        
        content_parts = []
        for chapter in sorted(self.chapters, key=lambda c: c.chapter_number):
            chapter_header = f"# Chapter {chapter.chapter_number}"
            if chapter.title:
                chapter_header += f": {chapter.title}"
            
            content_parts.append(f"{chapter_header}\n\n{chapter.content}")
        
        return "\n\n".join(content_parts)
    
    def get_chapter_content_range(self, start: int, count: int) -> str:
        """Get concatenated content for a range of chapters"""
        selected_chapters = [ch for ch in self.chapters if start <= ch.chapter_number < start + count]
        return "\n\n".join([f"# Chapter {ch.chapter_number}: {ch.title}\n\n{ch.content}" for ch in selected_chapters])
    
    @classmethod
    def create_empty(cls, workspace_id: UUID) -> 'FullStoryBase':
        """Create an empty story instance"""
        empty_metadata = StoryMetadata(
            id=UUID('00000000-0000-0000-0000-000000000000'),  # Placeholder for unpersisted
            workspace_id=workspace_id,
            title="Untitled Story",
            author="Unknown Author",
            created_at=datetime.now()
        )
        return cls(metadata=empty_metadata, chapters=[])
    
    @classmethod
    def from_file_data(cls, workspace_id: UUID, title: str, author: str, chapters_data: List[dict]) -> 'FullStoryBase':
        """Create story from file loading data"""
        chapters = [Chapter(**ch_data) for ch_data in chapters_data]
        metadata = StoryMetadata(
            id=UUID('00000000-0000-0000-0000-000000000000'),  # Placeholder for unpersisted
            workspace_id=workspace_id,
            title=title,
            author=author,
            created_at=datetime.now()
        )
        return cls(metadata=metadata, chapters=chapters) 