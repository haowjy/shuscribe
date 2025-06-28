"""
Abstract Base Class for Story Repositories
Handles stories, chapters, arcs, and related data
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.schemas.story import (
    Story, StoryCreate, StoryUpdate,
    Chapter, ChapterCreate,
    StoryArc, StoryArcCreate, StoryArcUpdate,
    EnhancedChapter, EnhancedChapterCreate,
    InputStory, StoryProcessingResult
)
# Wiki functionality moved to wikipage repository
# All wiki-related methods have been moved to AbstractWikiPageRepository


class AbstractStoryRepository(ABC):
    """Abstract interface for story repository operations"""

    # Story CRUD operations
    @abstractmethod
    async def get_story(self, story_id: UUID) -> Story:
        """Get a story by ID - returns empty story if not found"""
        ...

    @abstractmethod
    async def get_stories_by_owner(self, owner_id: UUID) -> List[Story]:
        """Get all stories owned by a user"""
        ...

    @abstractmethod
    async def create_story(self, story_create: StoryCreate) -> Story:
        """Create a new story"""
        ...

    @abstractmethod
    async def update_story(self, story_id: UUID, story_update: StoryUpdate) -> Story:
        """Update an existing story - returns empty story if not found"""
        ...

    @abstractmethod
    async def delete_story(self, story_id: UUID) -> bool:
        """Delete a story and all related data"""
        ...

    # Chapter operations
    @abstractmethod
    async def get_chapters(self, story_id: UUID) -> List[Chapter]:
        """Get all chapters for a story"""
        ...

    @abstractmethod
    async def get_chapter(self, chapter_id: UUID) -> Chapter:
        """Get a specific chapter - returns empty chapter if not found"""
        ...

    @abstractmethod
    async def create_chapter(self, chapter_create: ChapterCreate) -> Chapter:
        """Create a new chapter"""
        ...

    @abstractmethod
    async def create_chapters_bulk(self, chapters_create: List[ChapterCreate]) -> List[Chapter]:
        """Create multiple chapters in bulk"""
        ...

    # Story Arc operations
    @abstractmethod
    async def get_story_arcs(self, story_id: UUID) -> List[StoryArc]:
        """Get all arcs for a story"""
        ...

    @abstractmethod
    async def get_story_arc(self, arc_id: UUID) -> StoryArc:
        """Get a specific story arc - returns empty arc if not found"""
        ...

    @abstractmethod
    async def create_story_arc(self, arc_create: StoryArcCreate) -> StoryArc:
        """Create a new story arc"""
        ...

    @abstractmethod
    async def update_story_arc(self, arc_id: UUID, arc_update: StoryArcUpdate) -> StoryArc:
        """Update an existing story arc - returns empty arc if not found"""
        ...

    # Wiki Article operations moved to AbstractWikiPageRepository
    # All wiki-related methods are now handled by the wikipage repository

    # Enhanced Chapter operations
    @abstractmethod
    async def get_enhanced_chapters(self, story_id: UUID, arc_id: Optional[UUID] = None) -> List[EnhancedChapter]:
        """Get enhanced chapters for a story/arc"""
        ...

    @abstractmethod
    async def create_enhanced_chapter(self, enhanced_create: EnhancedChapterCreate) -> EnhancedChapter:
        """Create an enhanced chapter"""
        ...

    @abstractmethod
    async def create_enhanced_chapters_bulk(self, enhanced_creates: List[EnhancedChapterCreate]) -> List[EnhancedChapter]:
        """Create multiple enhanced chapters in bulk"""
        ...

    # User Progress operations removed - handled on frontend

    # High-level operations
    @abstractmethod
    async def store_input_story(self, input_story: InputStory, owner_id: UUID) -> Story:
        """
        Store an InputStory (from file loading) as a persistent Story with Chapters
        
        Args:
            input_story: The loaded story data
            owner_id: The user who owns this story
            
        Returns:
            The created Story object
        """
        ...

    # get_wiki_archive moved to AbstractWikiPageRepository

    @abstractmethod
    async def store_processing_result(self, processing_result: StoryProcessingResult) -> bool:
        """
        Store the complete result of story processing (arcs, articles, enhanced chapters)
        
        Args:
            processing_result: Complete processing result to store
            
        Returns:
            True if successful, False otherwise
        """
        ...

    # Search and filtering operations moved to AbstractWikiPageRepository 