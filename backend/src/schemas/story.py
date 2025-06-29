"""
Story schemas for ShuScribe
Defines schemas for input stories, processed stories, and story processing workflow
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any, Iterator, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema, TimestampSchema, UUIDSchema
from src.utils import count_tokens


class StoryStatus(str, Enum):
    """Story processing status"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING" 
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ProcessingMode(str, Enum):
    """Story processing mode"""
    FRESH = "fresh"        # New story, create everything from scratch
    UPDATE = "update"      # Existing story, add new chapters/arcs
    REPROCESS = "reprocess"  # Reprocess entire story


# Input Story Schemas (from file upload or directory loading)
class RawChapter(BaseSchema):
    """Raw chapter data from input source"""
    chapter_number: int
    title: str = ""
    content: str = ""
    ref: Optional[str] = Field(None, description="File reference (e.g., '1.xml')")


class RawStoryMetadata(BaseSchema):
    """Raw story metadata from input source (_meta.xml)"""
    title: str = ""
    author: str = ""
    synopsis: str = ""
    status: str = ""
    date_created: Optional[str] = None
    last_updated: Optional[str] = None
    copyright: Optional[str] = None
    genres: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    @classmethod
    def create_empty(cls) -> 'RawStoryMetadata':
        """Create an empty metadata instance"""
        return cls(
            title="Untitled Story",
            author="Unknown Author"
        )


class InputStory(BaseSchema):
    """Complete input story with metadata and chapters"""
    metadata: RawStoryMetadata
    chapters: List[RawChapter] = Field(default_factory=list)
    source_path: Optional[str] = Field(None, description="Original source directory or file")
    
    def __init__(self, **data):
        super().__init__(**data)
        self._cached_total_tokens: Optional[int] = None
    
    @property
    def total_chapters(self) -> int:
        return len(self.chapters)
    
    @property
    def word_count(self) -> int:
        """Calculate total word count across all chapters."""
        return sum(len(chapter.content.split()) for chapter in self.chapters)
    
    @property
    def total_tokens(self) -> int:
        """Calculate total token count across all chapters (cached)."""
        if not hasattr(self, '_cached_total_tokens') or self._cached_total_tokens is None:
            full_content = self.get_full_content()
            self._cached_total_tokens = count_tokens(full_content)
        return self._cached_total_tokens
    
    @property
    def is_short_story(self) -> bool:
        """Determine if this is a short story (< 15,000 words)."""
        return self.word_count < 15000
    
    def get_content_chunks(self, chunk_token_limit: int) -> Iterator[Tuple[List[RawChapter], str, int]]:
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
            # Format chapter content
            chapter_content = f"# Chapter {chapter.chapter_number}: {chapter.title}\n\n{chapter.content}"
            chapter_tokens = count_tokens(chapter_content)
            
            # Check if adding this chapter would exceed the limit
            if current_chunk_tokens + chapter_tokens > chunk_token_limit and current_chunk_chapters:
                # Yield current chunk and start a new one
                chunk_content = "\n\n".join([
                    f"# Chapter {c.chapter_number}: {c.title}\n\n{c.content}" 
                    for c in current_chunk_chapters
                ])
                yield (current_chunk_chapters, chunk_content, current_chunk_tokens)
                
                # Start new chunk with current chapter
                current_chunk_chapters = [chapter]
                current_chunk_tokens = chapter_tokens
            else:
                # Add chapter to current chunk
                current_chunk_chapters.append(chapter)
                current_chunk_tokens += chapter_tokens
        
        # Yield the final chunk if it has content
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
        """Get concatenated content for a range of chapters (more efficient than full_content)"""
        selected_chapters = [ch for ch in self.chapters if start <= ch.chapter_number < start + count]
        return "\n\n".join([f"# Chapter {ch.chapter_number}: {ch.title}\n\n{ch.content}" for ch in selected_chapters])

    @classmethod
    def create_empty(cls, source_path: Optional[str] = None) -> 'InputStory':
        """Create an empty story instance"""
        return cls(
            metadata=RawStoryMetadata.create_empty(),
            chapters=[],
            source_path=source_path
        )


# Database/Processed Story Schemas
class StoryBase(BaseSchema):
    """Base story schema for database storage"""
    title: str = ""
    author: str = ""
    status: StoryStatus = StoryStatus.PENDING


class StoryCreate(StoryBase):
    """Schema for creating a new story"""
    owner_id: UUID
    processing_plan: Optional[Dict[str, Any]] = None


class StoryUpdate(BaseSchema):
    """Schema for updating a story"""
    status: StoryStatus
    processing_plan: Optional[Dict[str, Any]] = None


class Story(StoryBase, UUIDSchema, TimestampSchema):
    """Complete processed story with database fields"""
    owner_id: UUID
    processing_plan: Optional[Dict[str, Any]] = None

    @classmethod
    def create_empty(cls, owner_id: UUID) -> 'Story':
        """Create an empty story instance"""
        return cls(
            title="",
            author="",
            status=StoryStatus.PENDING,
            owner_id=owner_id,
            id=UUID(int=0),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )


class ChapterBase(BaseSchema):
    """Base chapter schema for database storage"""
    chapter_number: int
    title: str
    raw_content: str


class ChapterCreate(ChapterBase):
    """Schema for creating a new chapter"""
    story_id: UUID


class Chapter(ChapterBase, UUIDSchema, TimestampSchema):
    """Complete chapter with database fields"""
    story_id: UUID
    
    @classmethod
    def create_empty(cls) -> 'Chapter':
        """Create an empty chapter instance"""
        return cls(
            id=UUID(int=0),
            story_id=UUID(int=0),
            chapter_number=0,
            title="",
            raw_content="",
            created_at=datetime.now(timezone.utc)
        )


# Arc Processing Schemas
class ArcStatus(str, Enum):
    """Arc processing status"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED" 
    FAILED = "FAILED"


class StoryArcBase(BaseSchema):
    """Base story arc schema"""
    arc_number: int
    title: str
    start_chapter: int
    end_chapter: int
    summary: str = ""
    key_events: Optional[Dict[str, Any]] = None
    token_count: Optional[int] = None
    processing_status: ArcStatus = ArcStatus.PENDING


class StoryArcCreate(StoryArcBase):
    """Schema for creating a new story arc"""
    story_id: UUID


class StoryArcUpdate(BaseSchema):
    """Schema for updating a story arc"""
    processing_status: Optional[ArcStatus] = None
    summary: Optional[str] = None
    key_events: Optional[Dict[str, Any]] = None
    token_count: Optional[int] = None


class StoryArc(StoryArcBase, UUIDSchema, TimestampSchema):
    """Complete story arc with database fields"""
    story_id: UUID


# Enhanced Chapter Schema  
class EnhancedChapterBase(BaseSchema):
    """Base enhanced chapter with wiki links"""
    enhanced_content: str
    link_metadata: Optional[Dict[str, Any]] = None


class EnhancedChapterCreate(EnhancedChapterBase):
    """Schema for creating enhanced chapter"""
    chapter_id: UUID
    arc_id: UUID


class EnhancedChapter(EnhancedChapterBase, UUIDSchema, TimestampSchema):
    """Complete enhanced chapter with database fields"""
    chapter_id: UUID
    arc_id: UUID


# Processing Result Schemas (without wiki dependencies)
class ArcProcessingResult(BaseSchema):
    """Result of processing a single arc"""
    arc: StoryArc
    enhanced_chapters: List[EnhancedChapter]
    article_count: int = Field(0, description="Number of wiki articles generated for this arc")
    processing_metadata: Optional[Dict[str, Any]] = None


class StoryProcessingResult(BaseSchema):
    """Result of processing an entire story"""
    story: Story
    arcs: List[ArcProcessingResult]
    total_processing_time: Optional[float] = None
    processing_metadata: Optional[Dict[str, Any]] = None


# WikiPage Association Schema (for linking stories to their wiki pages)
class WikiPageAssociationBase(BaseSchema):
    """Base schema for associating a story with its wiki page"""
    story_id: UUID
    wiki_page_id: UUID  # References a wiki page that contains articles
    is_primary: bool = Field(True, description="Whether this is the primary wiki page for the story")


class WikiPageAssociationCreate(WikiPageAssociationBase):
    """Schema for creating a story-wiki page association"""
    pass


class WikiPageAssociation(WikiPageAssociationBase, UUIDSchema, TimestampSchema):
    """Complete story-wiki page association with database fields"""
    pass
