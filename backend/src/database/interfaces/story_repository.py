from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.schemas.db.story import (
    Chapter,
    ChapterCreate,
    ChapterUpdate,
    ChapterStatus,
    StoryMetadata,
    StoryMetadataCreate,
    StoryMetadataUpdate,
)


class IStoryRepository(ABC):
    """Abstract interface for story repository - pure CRUD + simple queries"""

    # Chapter CRUD
    @abstractmethod
    async def create_chapter(self, chapter_data: ChapterCreate) -> Chapter:
        """Create a new chapter"""
        pass

    @abstractmethod
    async def get_chapter(self, chapter_id: UUID) -> Optional[Chapter]:
        """Get a specific chapter by ID"""
        pass

    @abstractmethod
    async def update_chapter(
        self, chapter_id: UUID, chapter_data: ChapterUpdate
    ) -> Chapter:
        """Update an existing chapter"""
        pass

    @abstractmethod
    async def delete_chapter(self, chapter_id: UUID) -> bool:
        """Delete a chapter"""
        pass

    # Simple Chapter Queries
    @abstractmethod
    async def get_chapters_by_workspace(
        self,
        workspace_id: UUID,
        status: Optional[ChapterStatus] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Chapter]:
        """Get chapters for a workspace, optionally filtered by status"""
        pass

    @abstractmethod
    async def get_chapter_by_number(
        self, workspace_id: UUID, chapter_number: int
    ) -> Optional[Chapter]:
        """Get a chapter by its number within a workspace"""
        pass

    @abstractmethod
    async def get_chapters_by_status(
        self, workspace_id: UUID, status: ChapterStatus
    ) -> List[Chapter]:
        """Get chapters filtered by status"""
        pass

    @abstractmethod
    async def get_chapters_by_number_range(
        self, workspace_id: UUID, start_chapter: int, end_chapter: int
    ) -> List[Chapter]:
        """Get chapters within a specific number range"""
        pass

    @abstractmethod
    async def get_chapters_by_ids(self, chapter_ids: List[UUID]) -> List[Chapter]:
        """Get multiple chapters by their IDs"""
        pass

    @abstractmethod
    async def search_chapters(
        self, workspace_id: UUID, query: str
    ) -> List[Chapter]:
        """Search chapters by content and title"""
        pass

    # Story Metadata CRUD
    @abstractmethod
    async def create_story_metadata(
        self, metadata_data: StoryMetadataCreate
    ) -> StoryMetadata:
        """Create story metadata"""
        pass

    @abstractmethod
    async def get_story_metadata(self, workspace_id: UUID) -> Optional[StoryMetadata]:
        """Get story metadata for a workspace"""
        pass

    @abstractmethod
    async def update_story_metadata(
        self, workspace_id: UUID, metadata_data: StoryMetadataUpdate
    ) -> StoryMetadata:
        """Update story metadata"""
        pass

    @abstractmethod
    async def delete_story_metadata(self, workspace_id: UUID) -> bool:
        """Delete story metadata"""
        pass

    # Bulk Operations
    @abstractmethod
    async def bulk_create_chapters(
        self, chapters: List[ChapterCreate]
    ) -> List[Chapter]:
        """Create multiple chapters in one operation"""
        pass

    @abstractmethod
    async def bulk_update_chapter_status(
        self, chapter_ids: List[UUID], status: ChapterStatus
    ) -> List[Chapter]:
        """Update status for multiple chapters"""
        pass