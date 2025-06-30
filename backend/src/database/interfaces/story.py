"""
Story Repository Interface

Abstract interface for story content operations including chapters and metadata.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from uuid import UUID

from src.database.models.story import Chapter, ChapterCreate, ChapterUpdate, StoryMetadata


class IStoryRepository(ABC):
    """Abstract interface for story repository"""

    # Chapter operations
    @abstractmethod
    async def get_chapter(self, id: UUID) -> Optional[Chapter]:
        """Retrieve a chapter by ID"""
        pass

    @abstractmethod
    async def get_chapter_by_number(self, workspace_id: UUID, chapter_number: int) -> Optional[Chapter]:
        """Get chapter by workspace and chapter number"""
        pass

    @abstractmethod
    async def get_chapters_by_workspace(self, workspace_id: UUID) -> List[Chapter]:
        """Get all chapters for a workspace"""
        pass

    @abstractmethod
    async def get_published_chapters(self, workspace_id: UUID) -> List[Chapter]:
        """Get only published chapters for a workspace"""
        pass

    @abstractmethod
    async def create_chapter(self, chapter_data: ChapterCreate) -> Chapter:
        """Create a new chapter"""
        pass
    
    @abstractmethod
    async def update_chapter(self, chapter_id: UUID, chapter_data: ChapterUpdate) -> Chapter:
        """Update an existing chapter"""
        pass

    @abstractmethod
    async def delete_chapter(self, chapter_id: UUID) -> bool:
        """Delete a chapter"""
        pass

    # Story metadata operations
    @abstractmethod
    async def get_story_metadata(self, workspace_id: UUID) -> Optional[StoryMetadata]:
        """Get story metadata for a workspace"""
        pass

    @abstractmethod
    async def create_story_metadata(self, workspace_id: UUID, title: str, author: str, 
                                   synopsis: str = "", genres: Optional[List[str]] = None, tags: Optional[List[str]] = None,
                                   total_chapters: int = 0, publication_status: str = "draft",
                                   settings: Optional[Dict] = None) -> StoryMetadata:
        """Create story metadata for a workspace"""
        pass

    @abstractmethod
    async def update_story_metadata(self, workspace_id: UUID, **updates) -> StoryMetadata:
        """Update story metadata"""
        pass

    @abstractmethod
    async def refresh_chapter_stats(self, workspace_id: UUID) -> StoryMetadata:
        """Refresh chapter statistics in story metadata"""
        pass 