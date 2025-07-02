"""
Story Service - Business logic for chapter and story metadata management.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from src.database.interfaces.story_repository import IStoryRepository
from src.database.interfaces.workspace_repository import IWorkspaceRepository
from src.schemas.db.story import (
    Chapter, ChapterCreate, ChapterStatus, ChapterUpdate,
    StoryMetadata, StoryMetadataCreate, StoryMetadataUpdate
)


class StoryService:
    """Service layer for story and chapter management with business logic."""
    
    def __init__(
        self, 
        story_repository: IStoryRepository,
        workspace_repository: IWorkspaceRepository
    ):
        self.story_repository = story_repository
        self.workspace_repository = workspace_repository
    
    # Chapter Management
    async def create_chapter(self, chapter_data: ChapterCreate) -> Chapter:
        """Create a new chapter with validation."""
        # Verify workspace exists
        workspace = await self.workspace_repository.get_workspace(chapter_data.workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {chapter_data.workspace_id} not found")
        
        # Check for duplicate chapter numbers within workspace
        existing_chapter = await self.story_repository.get_chapter_by_number(
            chapter_data.workspace_id, chapter_data.chapter_number
        )
        if existing_chapter:
            raise ValueError(
                f"Chapter {chapter_data.chapter_number} already exists in workspace"
            )
        
        return await self.story_repository.create_chapter(chapter_data)
    
    async def get_chapter(self, chapter_id: UUID) -> Optional[Chapter]:
        """Get chapter by ID."""
        return await self.story_repository.get_chapter(chapter_id)
    
    async def get_chapter_by_number(self, workspace_id: UUID, chapter_number: int) -> Optional[Chapter]:
        """Get chapter by number within workspace."""
        return await self.story_repository.get_chapter_by_number(workspace_id, chapter_number)
    
    async def update_chapter(self, chapter_id: UUID, chapter_data: ChapterUpdate) -> Chapter:
        """Update chapter with validation."""
        # Verify chapter exists
        existing_chapter = await self.story_repository.get_chapter(chapter_id)
        if not existing_chapter:
            raise ValueError(f"Chapter {chapter_id} not found")
        
        # Check for chapter number conflicts if number is being changed
        if (chapter_data.chapter_number is not None and 
            chapter_data.chapter_number != existing_chapter.chapter_number):
            
            existing_by_number = await self.story_repository.get_chapter_by_number(
                existing_chapter.workspace_id, chapter_data.chapter_number
            )
            if existing_by_number:
                raise ValueError(
                    f"Chapter {chapter_data.chapter_number} already exists in workspace"
                )
        
        return await self.story_repository.update_chapter(chapter_id, chapter_data)
    
    async def delete_chapter(self, chapter_id: UUID) -> bool:
        """Delete chapter."""
        # Verify chapter exists
        existing_chapter = await self.story_repository.get_chapter(chapter_id)
        if not existing_chapter:
            return False
        
        # TODO: Add cleanup logic for wiki articles that reference this chapter
        
        return await self.story_repository.delete_chapter(chapter_id)
    
    async def get_chapters_by_workspace(
        self, workspace_id: UUID, published_only: bool = False
    ) -> List[Chapter]:
        """Get chapters for a workspace, optionally filtered by publication status."""
        # Map published_only to status filter
        status = None
        if published_only:
            from src.schemas.db.story import ChapterStatus
            status = ChapterStatus.PUBLISHED
            
        return await self.story_repository.get_chapters_by_workspace(
            workspace_id, status=status
        )
    
    async def search_chapters(self, workspace_id: UUID, query: str) -> List[Chapter]:
        """Search chapters by title and content."""
        return await self.story_repository.search_chapters(workspace_id, query)
    
    async def get_chapters_by_number_range(
        self, workspace_id: UUID, start_chapter: int, end_chapter: int
    ) -> List[Chapter]:
        """Get chapters within a specific number range."""
        return await self.story_repository.get_chapters_by_number_range(
            workspace_id, start_chapter, end_chapter
        )
    
    # Chapter Content Management
    async def update_chapter_content(self, chapter_id: UUID, content: str) -> Chapter:
        """Update only the content of a chapter."""
        chapter_update = ChapterUpdate(content=content)
        return await self.update_chapter(chapter_id, chapter_update)
    
    async def publish_chapter(self, chapter_id: UUID) -> Chapter:
        """Mark a chapter as published."""
        chapter_update = ChapterUpdate(status=ChapterStatus.PUBLISHED)
        return await self.update_chapter(chapter_id, chapter_update)
    
    async def unpublish_chapter(self, chapter_id: UUID) -> Chapter:
        """Mark a chapter as unpublished."""
        chapter_update = ChapterUpdate(status=ChapterStatus.DRAFT)
        return await self.update_chapter(chapter_id, chapter_update)
    
    # Story Metadata Management
    async def create_story_metadata(self, metadata_data: StoryMetadataCreate) -> StoryMetadata:
        """Create story metadata with validation."""
        # Verify workspace exists
        workspace = await self.workspace_repository.get_workspace(metadata_data.workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {metadata_data.workspace_id} not found")
        
        # Check if metadata already exists for this workspace
        existing_metadata = await self.story_repository.get_story_metadata(
            metadata_data.workspace_id
        )
        if existing_metadata:
            raise ValueError(f"Story metadata already exists for workspace {metadata_data.workspace_id}")
        
        return await self.story_repository.create_story_metadata(metadata_data)
    
    async def get_story_metadata_by_workspace(self, workspace_id: UUID) -> Optional[StoryMetadata]:
        """Get story metadata for a workspace."""
        return await self.story_repository.get_story_metadata(workspace_id)
    
    async def update_story_metadata(
        self, workspace_id: UUID, metadata_data: StoryMetadataUpdate
    ) -> StoryMetadata:
        """Update story metadata."""
        # Verify metadata exists
        existing_metadata = await self.story_repository.get_story_metadata(workspace_id)
        if not existing_metadata:
            raise ValueError(f"Story metadata for workspace {workspace_id} not found")
        
        return await self.story_repository.update_story_metadata(workspace_id, metadata_data)
    
    async def delete_story_metadata(self, workspace_id: UUID) -> bool:
        """Delete story metadata."""
        return await self.story_repository.delete_story_metadata(workspace_id)
    
    # Story Statistics and Analytics
    async def get_story_statistics(self, workspace_id: UUID) -> Dict[str, Any]:
        """Get comprehensive statistics for a story."""
        # Get all chapters
        chapters = await self.story_repository.get_chapters_by_workspace(workspace_id)
        published_chapters = [c for c in chapters if c.is_published]
        
        # Calculate word counts
        total_words = sum(len(c.content.split()) for c in chapters)
        published_words = sum(len(c.content.split()) for c in published_chapters)
        
        # Get story metadata
        metadata = await self.story_repository.get_story_metadata(workspace_id)
        
        return {
            "workspace_id": workspace_id,
            "total_chapters": len(chapters),
            "published_chapters": len(published_chapters),
            "total_word_count": total_words,
            "published_word_count": published_words,
            "average_chapter_length": total_words // len(chapters) if chapters else 0,
            "story_metadata": metadata,
            "latest_chapter_number": max((c.chapter_number for c in chapters), default=0),
            "first_published": min((c.published_at for c in published_chapters if c.published_at), default=None),
            "last_published": max((c.published_at for c in published_chapters if c.published_at), default=None)
        }
    
    async def get_chapter_range(
        self, workspace_id: UUID, start_chapter: int, end_chapter: int
    ) -> List[Chapter]:
        """Get chapters within a specific range."""
        return await self.story_repository.get_chapters_by_number_range(
            workspace_id, start_chapter, end_chapter
        )
    
    async def reorder_chapters(self, workspace_id: UUID, chapter_order: List[UUID]) -> List[Chapter]:
        """Reorder chapters by updating their chapter numbers."""
        # Get existing chapters
        chapters = {c.id: c for c in await self.story_repository.get_chapters_by_workspace(workspace_id)}
        
        # Validate all chapter IDs exist
        for chapter_id in chapter_order:
            if chapter_id not in chapters:
                raise ValueError(f"Chapter {chapter_id} not found in workspace")
        
        # Update chapter numbers
        updated_chapters = []
        for i, chapter_id in enumerate(chapter_order, 1):
            chapter_update = ChapterUpdate(chapter_number=i)
            updated_chapter = await self.story_repository.update_chapter(chapter_id, chapter_update)
            updated_chapters.append(updated_chapter)
        
        return updated_chapters
    
    async def validate_chapter_sequence(self, workspace_id: UUID) -> Dict[str, Any]:
        """Validate that chapter numbers form a proper sequence."""
        chapters = await self.story_repository.get_chapters_by_workspace(workspace_id)
        chapter_numbers = sorted(c.chapter_number for c in chapters)
        
        issues = []
        
        # Check for gaps
        for i in range(len(chapter_numbers) - 1):
            if chapter_numbers[i + 1] - chapter_numbers[i] > 1:
                issues.append(f"Gap between chapters {chapter_numbers[i]} and {chapter_numbers[i + 1]}")
        
        # Check for duplicates
        seen = set()
        for num in chapter_numbers:
            if num in seen:
                issues.append(f"Duplicate chapter number: {num}")
            seen.add(num)
        
        return {
            "workspace_id": workspace_id,
            "total_chapters": len(chapters),
            "chapter_numbers": chapter_numbers,
            "is_valid": len(issues) == 0,
            "issues": issues
        }