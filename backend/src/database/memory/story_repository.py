"""Memory-based story repository implementation for testing and development."""
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from datetime import UTC, datetime

from src.database.interfaces.story_repository import IStoryRepository
from src.schemas.db.story import (
    Chapter,
    ChapterCreate,
    ChapterUpdate,
    ChapterStatus,
    StoryMetadata,
    StoryMetadataCreate,
    StoryMetadataUpdate,
)


class MemoryStoryRepository(IStoryRepository):
    """In-memory implementation of story repository for testing."""
    
    def __init__(self):
        self._chapters: Dict[UUID, Chapter] = {}
        self._story_metadata: Dict[UUID, StoryMetadata] = {}  # workspace_id -> metadata
    
    # Chapter CRUD
    async def create_chapter(self, chapter_data: ChapterCreate) -> Chapter:
        """Create a new chapter"""
        chapter_id = uuid4()
        now = datetime.now(UTC)
        
        # Calculate word count
        word_count = len(chapter_data.content.split()) if chapter_data.content else 0
        
        chapter = Chapter(
            id=chapter_id,
            workspace_id=chapter_data.workspace_id,
            title=chapter_data.title,
            content=chapter_data.content,
            chapter_number=chapter_data.chapter_number,
            word_count=word_count,
            status=chapter_data.status,
            summary=chapter_data.summary,
            tags=chapter_data.tags,
            metadata=chapter_data.metadata,
            version=1,
            published_at=None,
            created_at=now,
            updated_at=now
        )
        
        self._chapters[chapter_id] = chapter
        return chapter
    
    async def get_chapter(self, chapter_id: UUID) -> Optional[Chapter]:
        """Get a specific chapter by ID"""
        return self._chapters.get(chapter_id)
    
    async def update_chapter(
        self, chapter_id: UUID, chapter_data: ChapterUpdate
    ) -> Chapter:
        """Update an existing chapter"""
        chapter = self._chapters.get(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")
        
        update_dict = chapter_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        # Recalculate word count if content changed
        if 'content' in update_dict:
            update_dict['word_count'] = len(update_dict['content'].split()) if update_dict['content'] else 0
        
        # Update publication timestamp if status changed to published
        if update_dict.get('status') == ChapterStatus.PUBLISHED and chapter.status != ChapterStatus.PUBLISHED:
            update_dict['published_at'] = datetime.now(UTC)
        
        # Increment version
        update_dict['version'] = chapter.version + 1
        
        updated_chapter = chapter.model_copy(update=update_dict)
        self._chapters[chapter_id] = updated_chapter
        return updated_chapter
    
    async def delete_chapter(self, chapter_id: UUID) -> bool:
        """Delete a chapter"""
        if chapter_id in self._chapters:
            del self._chapters[chapter_id]
            return True
        return False
    
    # Simple Chapter Queries
    async def get_chapters_by_workspace(
        self,
        workspace_id: UUID,
        status: Optional[ChapterStatus] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Chapter]:
        """Get chapters for a workspace, optionally filtered by status"""
        chapters = []
        for chapter in self._chapters.values():
            if chapter.workspace_id == workspace_id:
                if status is None or chapter.status == status:
                    chapters.append(chapter)
        
        # Sort by chapter number
        chapters.sort(key=lambda c: c.chapter_number)
        return chapters[offset:offset + limit]
    
    async def get_chapter_by_number(
        self, workspace_id: UUID, chapter_number: int
    ) -> Optional[Chapter]:
        """Get a chapter by its number within a workspace"""
        for chapter in self._chapters.values():
            if (chapter.workspace_id == workspace_id and 
                chapter.chapter_number == chapter_number):
                return chapter
        return None
    
    async def get_chapters_by_status(
        self, workspace_id: UUID, status: ChapterStatus
    ) -> List[Chapter]:
        """Get chapters filtered by status"""
        chapters = []
        for chapter in self._chapters.values():
            if (chapter.workspace_id == workspace_id and 
                chapter.status == status):
                chapters.append(chapter)
        
        chapters.sort(key=lambda c: c.chapter_number)
        return chapters
    
    async def get_chapters_by_number_range(
        self, workspace_id: UUID, start_chapter: int, end_chapter: int
    ) -> List[Chapter]:
        """Get chapters within a specific number range"""
        chapters = []
        for chapter in self._chapters.values():
            if (chapter.workspace_id == workspace_id and 
                start_chapter <= chapter.chapter_number <= end_chapter):
                chapters.append(chapter)
        
        chapters.sort(key=lambda c: c.chapter_number)
        return chapters
    
    async def get_chapters_by_ids(self, chapter_ids: List[UUID]) -> List[Chapter]:
        """Get multiple chapters by their IDs"""
        chapters = []
        for chapter_id in chapter_ids:
            chapter = self._chapters.get(chapter_id)
            if chapter:
                chapters.append(chapter)
        
        chapters.sort(key=lambda c: c.chapter_number)
        return chapters
    
    async def search_chapters(
        self, workspace_id: UUID, query: str
    ) -> List[Chapter]:
        """Search chapters by content and title"""
        query_lower = query.lower()
        matching_chapters = []
        
        for chapter in self._chapters.values():
            if chapter.workspace_id == workspace_id:
                # Search in title and content
                if (query_lower in chapter.title.lower() or 
                    query_lower in chapter.content.lower()):
                    matching_chapters.append(chapter)
        
        matching_chapters.sort(key=lambda c: c.chapter_number)
        return matching_chapters
    
    # Story Metadata CRUD
    async def create_story_metadata(
        self, metadata_data: StoryMetadataCreate
    ) -> StoryMetadata:
        """Create story metadata"""
        metadata_id = uuid4()
        now = datetime.now(UTC)
        
        # Note: workspace_id needs to be provided separately since it's not in the create schema
        # For now, we'll assume it's passed in the metadata_data somehow
        workspace_id = getattr(metadata_data, 'workspace_id', uuid4())
        
        metadata = StoryMetadata(
            id=metadata_id,
            workspace_id=workspace_id,
            title=metadata_data.title,
            author=metadata_data.author,
            synopsis=metadata_data.synopsis,
            genres=metadata_data.genres,
            tags=metadata_data.tags,
            total_chapters=metadata_data.total_chapters,
            publication_status=metadata_data.publication_status,
            settings=metadata_data.settings,
            published_chapters=0,
            total_word_count=0,
            first_published_at=None,
            last_updated_at=None,
            created_at=now,
            updated_at=now
        )
        
        self._story_metadata[workspace_id] = metadata
        return metadata
    
    async def get_story_metadata(self, workspace_id: UUID) -> Optional[StoryMetadata]:
        """Get story metadata for a workspace"""
        return self._story_metadata.get(workspace_id)
    
    async def update_story_metadata(
        self, workspace_id: UUID, metadata_data: StoryMetadataUpdate
    ) -> StoryMetadata:
        """Update story metadata"""
        metadata = self._story_metadata.get(workspace_id)
        if not metadata:
            raise ValueError(f"Story metadata not found for workspace {workspace_id}")
        
        update_dict = metadata_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        updated_metadata = metadata.model_copy(update=update_dict)
        self._story_metadata[workspace_id] = updated_metadata
        return updated_metadata
    
    async def delete_story_metadata(self, workspace_id: UUID) -> bool:
        """Delete story metadata"""
        if workspace_id in self._story_metadata:
            del self._story_metadata[workspace_id]
            return True
        return False
    
    # Bulk Operations
    async def bulk_create_chapters(
        self, chapters: List[ChapterCreate]
    ) -> List[Chapter]:
        """Create multiple chapters in one operation"""
        created_chapters = []
        for chapter_data in chapters:
            chapter = await self.create_chapter(chapter_data)
            created_chapters.append(chapter)
        return created_chapters
    
    async def bulk_update_chapter_status(
        self, chapter_ids: List[UUID], status: ChapterStatus
    ) -> List[Chapter]:
        """Update status for multiple chapters"""
        updated_chapters = []
        now = datetime.now(UTC)
        
        for chapter_id in chapter_ids:
            chapter = self._chapters.get(chapter_id)
            if chapter:
                update_dict = {
                    'status': status,
                    'updated_at': now,
                    'version': chapter.version + 1
                }
                
                # Set published_at if changing to published
                if status == ChapterStatus.PUBLISHED and chapter.status != ChapterStatus.PUBLISHED:
                    update_dict['published_at'] = now
                
                updated_chapter = chapter.model_copy(update=update_dict)
                self._chapters[chapter_id] = updated_chapter
                updated_chapters.append(updated_chapter)
        
        return updated_chapters