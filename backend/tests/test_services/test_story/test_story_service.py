"""
Comprehensive tests for StoryService with memory repositories
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime
from typing import Tuple

from src.schemas.db.story import (
    Chapter, ChapterCreate, ChapterUpdate, ChapterStatus,
    StoryMetadata, StoryMetadataCreate, StoryMetadataUpdate
)
from src.schemas.db.workspace import Workspace
from src.services.story.story_service import StoryService

from .utils import (
    assert_chapter_equal, 
    create_chapter_data, 
    create_chapters_batch,
    calculate_expected_statistics
)


class TestChapterCRUD:
    """Test basic CRUD operations for chapters"""
    
    async def test_create_chapter_success(self, story_service: StoryService, empty_workspace: Workspace):
        """Test creating a valid chapter"""
        chapter_data = ChapterCreate(
            workspace_id=empty_workspace.id,
            title="Test Chapter",
            content="This is test content for the chapter.",
            chapter_number=1,
            status=ChapterStatus.DRAFT,
            summary="A test chapter",
            tags=["test", "chapter"]
        )
        
        chapter = await story_service.create_chapter(chapter_data)
        
        assert chapter.id is not None
        assert chapter.workspace_id == empty_workspace.id
        assert chapter.title == "Test Chapter"
        assert chapter.content == "This is test content for the chapter."
        assert chapter.chapter_number == 1
        assert chapter.status == ChapterStatus.DRAFT
        assert chapter.word_count == 7  # 7 words in content
        assert chapter.version == 1
        assert chapter.published_at is None
        assert isinstance(chapter.created_at, datetime)
    
    async def test_create_chapter_workspace_not_found(self, story_service: StoryService):
        """Test error when creating chapter for non-existent workspace"""
        fake_workspace_id = uuid4()
        chapter_data = create_chapter_data(fake_workspace_id, 1)
        
        with pytest.raises(ValueError) as exc_info:
            await story_service.create_chapter(chapter_data)
        
        assert f"Workspace {fake_workspace_id} not found" in str(exc_info.value)
    
    async def test_create_chapter_duplicate_number(self, story_service: StoryService, empty_workspace: Workspace):
        """Test error when creating chapter with duplicate number"""
        # Create first chapter
        chapter_data = create_chapter_data(empty_workspace.id, 1)
        await story_service.create_chapter(chapter_data)
        
        # Try to create another chapter with same number
        duplicate_data = create_chapter_data(empty_workspace.id, 1)
        
        with pytest.raises(ValueError) as exc_info:
            await story_service.create_chapter(duplicate_data)
        
        assert "Chapter 1 already exists in workspace" in str(exc_info.value)
    
    async def test_get_chapter_exists(self, story_service: StoryService, empty_workspace: Workspace):
        """Test retrieving an existing chapter by ID"""
        # Create a chapter
        chapter_data = create_chapter_data(empty_workspace.id, 1)
        created_chapter = await story_service.create_chapter(chapter_data)
        
        # Retrieve it
        retrieved_chapter = await story_service.get_chapter(created_chapter.id)
        
        assert retrieved_chapter is not None
        assert retrieved_chapter.id == created_chapter.id
        assert retrieved_chapter.title == created_chapter.title
    
    async def test_get_chapter_not_found(self, story_service: StoryService):
        """Test retrieving non-existent chapter returns None"""
        fake_chapter_id = uuid4()
        chapter = await story_service.get_chapter(fake_chapter_id)
        assert chapter is None
    
    async def test_get_chapter_by_number(self, story_service: StoryService, empty_workspace: Workspace):
        """Test retrieving chapter by number within workspace"""
        # Create chapters
        await create_chapters_batch(story_service, empty_workspace.id, 3)
        
        # Get chapter 2
        chapter = await story_service.get_chapter_by_number(empty_workspace.id, 2)
        
        assert chapter is not None
        assert chapter.chapter_number == 2
        assert chapter.title == "Chapter 2"
    
    async def test_update_chapter_success(self, story_service: StoryService, empty_workspace: Workspace):
        """Test updating various chapter fields"""
        # Create a chapter
        chapter_data = create_chapter_data(empty_workspace.id, 1)
        chapter = await story_service.create_chapter(chapter_data)
        original_created_at = chapter.created_at
        
        # Update it
        update_data = ChapterUpdate(
            title="Updated Title",
            content="Updated content with more words than before.",
            summary="Updated summary",
            tags=["updated", "test"]
        )
        
        updated_chapter = await story_service.update_chapter(chapter.id, update_data)
        
        assert updated_chapter.title == "Updated Title"
        assert updated_chapter.content == "Updated content with more words than before."
        assert updated_chapter.word_count == 7  # 7 words in new content
        assert updated_chapter.summary == "Updated summary"
        assert updated_chapter.tags == ["updated", "test"]
        assert updated_chapter.version == 2  # Version incremented
        assert updated_chapter.created_at == original_created_at
        assert updated_chapter.updated_at > original_created_at
    
    async def test_update_chapter_not_found(self, story_service: StoryService):
        """Test error when updating non-existent chapter"""
        fake_chapter_id = uuid4()
        update_data = ChapterUpdate(title="New Title")
        
        with pytest.raises(ValueError) as exc_info:
            await story_service.update_chapter(fake_chapter_id, update_data)
        
        assert f"Chapter {fake_chapter_id} not found" in str(exc_info.value)
    
    async def test_update_chapter_change_number_conflict(self, story_service: StoryService, empty_workspace: Workspace):
        """Test error when changing chapter number to existing one"""
        # Create two chapters
        chapter1 = await story_service.create_chapter(
            create_chapter_data(empty_workspace.id, 1)
        )
        chapter2 = await story_service.create_chapter(
            create_chapter_data(empty_workspace.id, 2)
        )
        
        # Try to change chapter 2's number to 1
        update_data = ChapterUpdate(chapter_number=1)
        
        with pytest.raises(ValueError) as exc_info:
            await story_service.update_chapter(chapter2.id, update_data)
        
        assert "Chapter 1 already exists in workspace" in str(exc_info.value)
    
    async def test_delete_chapter_success(self, story_service: StoryService, empty_workspace: Workspace):
        """Test deleting an existing chapter"""
        # Create a chapter
        chapter_data = create_chapter_data(empty_workspace.id, 1)
        chapter = await story_service.create_chapter(chapter_data)
        
        # Delete it
        result = await story_service.delete_chapter(chapter.id)
        assert result is True
        
        # Verify it's gone
        retrieved = await story_service.get_chapter(chapter.id)
        assert retrieved is None
    
    async def test_delete_chapter_not_found(self, story_service: StoryService):
        """Test deleting non-existent chapter returns False"""
        fake_chapter_id = uuid4()
        result = await story_service.delete_chapter(fake_chapter_id)
        assert result is False


class TestChapterQueries:
    """Test chapter query operations"""
    
    async def test_get_chapters_by_workspace_all(self, story_service: StoryService, empty_workspace: Workspace):
        """Test getting all chapters for a workspace"""
        # Create 5 chapters
        await create_chapters_batch(story_service, empty_workspace.id, 5)
        
        # Get all chapters
        chapters = await story_service.get_chapters_by_workspace(empty_workspace.id)
        
        assert len(chapters) == 5
        # Should be sorted by chapter number
        assert [c.chapter_number for c in chapters] == [1, 2, 3, 4, 5]
    
    async def test_get_chapters_by_workspace_published_only(self, story_service: StoryService, empty_workspace: Workspace):
        """Test filtering chapters by published status"""
        # Create mix of published and draft chapters
        for i in range(1, 6):
            chapter_data = create_chapter_data(
                empty_workspace.id, 
                i,
                status=ChapterStatus.PUBLISHED if i <= 3 else ChapterStatus.DRAFT
            )
            await story_service.create_chapter(chapter_data)
        
        # Get published only
        published_chapters = await story_service.get_chapters_by_workspace(
            empty_workspace.id, 
            published_only=True
        )
        
        assert len(published_chapters) == 3
        assert all(c.status == ChapterStatus.PUBLISHED for c in published_chapters)
    
    async def test_search_chapters_in_title(self, story_service: StoryService, empty_workspace: Workspace):
        """Test searching chapters by title"""
        # Create chapters with different titles
        await story_service.create_chapter(create_chapter_data(
            empty_workspace.id, 1, title="The Beginning"
        ))
        await story_service.create_chapter(create_chapter_data(
            empty_workspace.id, 2, title="The Middle"
        ))
        await story_service.create_chapter(create_chapter_data(
            empty_workspace.id, 3, title="The End"
        ))
        
        # Search for "Beginning"
        results = await story_service.search_chapters(empty_workspace.id, "Beginning")
        
        assert len(results) == 1
        assert results[0].title == "The Beginning"
    
    async def test_search_chapters_in_content(self, story_service: StoryService, empty_workspace: Workspace):
        """Test searching chapters by content"""
        # Create chapters with specific content
        await story_service.create_chapter(create_chapter_data(
            empty_workspace.id, 1, content="The hero finds a magic sword."
        ))
        await story_service.create_chapter(create_chapter_data(
            empty_workspace.id, 2, content="The villain steals the crown."
        ))
        
        # Search for "magic"
        results = await story_service.search_chapters(empty_workspace.id, "magic")
        
        assert len(results) == 1
        assert "magic sword" in results[0].content
    
    async def test_get_chapters_by_number_range(self, story_service: StoryService, empty_workspace: Workspace):
        """Test getting chapters within a specific range"""
        # Create 10 chapters
        await create_chapters_batch(story_service, empty_workspace.id, 10)
        
        # Get chapters 3-7
        chapters = await story_service.get_chapters_by_number_range(
            empty_workspace.id, 3, 7
        )
        
        assert len(chapters) == 5
        assert [c.chapter_number for c in chapters] == [3, 4, 5, 6, 7]


class TestBusinessLogic:
    """Test business logic and convenience methods"""
    
    async def test_publish_chapter(self, story_service: StoryService, empty_workspace: Workspace):
        """Test publishing a chapter"""
        # Create draft chapter
        chapter = await story_service.create_chapter(
            create_chapter_data(empty_workspace.id, 1, status=ChapterStatus.DRAFT)
        )
        
        assert chapter.status == ChapterStatus.DRAFT
        assert chapter.published_at is None
        
        # Publish it
        published = await story_service.publish_chapter(chapter.id)
        
        assert published.status == ChapterStatus.PUBLISHED
        assert published.published_at is not None
        assert published.version == 2
    
    async def test_unpublish_chapter(self, story_service: StoryService, empty_workspace: Workspace):
        """Test unpublishing a chapter"""
        # Create published chapter
        chapter = await story_service.create_chapter(
            create_chapter_data(empty_workspace.id, 1, status=ChapterStatus.PUBLISHED)
        )
        
        # Unpublish it
        unpublished = await story_service.unpublish_chapter(chapter.id)
        
        assert unpublished.status == ChapterStatus.DRAFT
        # Note: published_at is not cleared, it remains as historical data
    
    async def test_update_chapter_content_only(self, story_service: StoryService, empty_workspace: Workspace):
        """Test convenience method for updating only content"""
        # Create chapter
        chapter = await story_service.create_chapter(
            create_chapter_data(empty_workspace.id, 1)
        )
        original_title = chapter.title
        
        # Update content only
        new_content = "This is completely new content."
        updated = await story_service.update_chapter_content(chapter.id, new_content)
        
        assert updated.content == new_content
        assert updated.title == original_title  # Title unchanged
        assert updated.word_count == 5  # Word count updated
    
    async def test_word_count_calculation(self, story_service: StoryService, empty_workspace: Workspace):
        """Test that word count is correctly calculated"""
        test_cases = [
            ("Single word", 2),
            ("Two words here", 3),
            ("This is a longer sentence with seven words.", 8),
            ("", 0),
            ("   Spaces   around   words   ", 3),
        ]
        
        for i, (content, expected_count) in enumerate(test_cases, 1):
            chapter = await story_service.create_chapter(
                create_chapter_data(empty_workspace.id, i, content=content)
            )
            assert chapter.word_count == expected_count, f"Failed for content: {content}"


class TestStoryMetadata:
    """Test story metadata operations"""
    
    async def test_create_story_metadata_success(self, story_service: StoryService, empty_workspace: Workspace):
        """Test creating story metadata"""
        metadata_data = StoryMetadataCreate(
            workspace_id=empty_workspace.id,
            title="Epic Fantasy Story",
            author="Test Author",
            synopsis="A tale of adventure and magic",
            genres=["Fantasy", "Adventure"],
            tags=["magic", "quest", "dragons"],
            total_chapters=50,
            publication_status="in_progress"
        )
        
        metadata = await story_service.create_story_metadata(metadata_data)
        
        assert metadata.id is not None
        assert metadata.workspace_id == empty_workspace.id
        assert metadata.title == "Epic Fantasy Story"
        assert metadata.author == "Test Author"
        assert metadata.genres == ["Fantasy", "Adventure"]
        assert metadata.total_chapters == 50
        assert metadata.published_chapters == 0
        assert metadata.total_word_count == 0
    
    async def test_create_story_metadata_workspace_not_found(self, story_service: StoryService):
        """Test error when creating metadata for non-existent workspace"""
        fake_workspace_id = uuid4()
        metadata_data = StoryMetadataCreate(
            workspace_id=fake_workspace_id,
            title="Test",
            author="Test"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await story_service.create_story_metadata(metadata_data)
        
        assert f"Workspace {fake_workspace_id} not found" in str(exc_info.value)
    
    async def test_create_story_metadata_duplicate(self, story_service: StoryService, workspace_with_metadata: Tuple[Workspace, StoryMetadata]):
        """Test error when creating duplicate metadata for workspace"""
        workspace, existing_metadata = workspace_with_metadata
        
        # Try to create another metadata for same workspace
        duplicate_data = StoryMetadataCreate(
            workspace_id=workspace.id,
            title="Another Story",
            author="Another Author"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await story_service.create_story_metadata(duplicate_data)
        
        assert f"Story metadata already exists for workspace {workspace.id}" in str(exc_info.value)
    
    async def test_get_story_metadata_by_workspace(self, story_service: StoryService, workspace_with_metadata: Tuple[Workspace, StoryMetadata]):
        """Test retrieving story metadata by workspace"""
        workspace, created_metadata = workspace_with_metadata
        
        metadata = await story_service.get_story_metadata_by_workspace(workspace.id)
        
        assert metadata is not None
        assert metadata.id == created_metadata.id
        assert metadata.title == created_metadata.title
    
    async def test_update_story_metadata(self, story_service: StoryService, workspace_with_metadata: Tuple[Workspace, StoryMetadata]):
        """Test updating story metadata"""
        workspace, metadata = workspace_with_metadata
        
        update_data = StoryMetadataUpdate(
            author="Test Author",
            title="Updated Title",
            synopsis="Updated synopsis with more detail",
            genres=["Fantasy", "Romance"],
            total_chapters=75
        )
        
        updated = await story_service.update_story_metadata(workspace.id, update_data)
        
        assert updated.title == "Updated Title"
        assert updated.synopsis == "Updated synopsis with more detail"
        assert updated.genres == ["Fantasy", "Romance"]
        assert updated.total_chapters == 75
        assert updated.author == metadata.author  # Unchanged
    
    async def test_update_story_metadata_not_found(self, story_service: StoryService, empty_workspace: Workspace):
        """Test error when updating non-existent metadata"""
        update_data = StoryMetadataUpdate(
            title="New Title",
            author="Test Author",
            total_chapters=10
        )
        
        with pytest.raises(ValueError) as exc_info:
            await story_service.update_story_metadata(empty_workspace.id, update_data)
        
        assert f"Story metadata for workspace {empty_workspace.id} not found" in str(exc_info.value)
    
    async def test_delete_story_metadata(self, story_service: StoryService, workspace_with_metadata: Tuple[Workspace, StoryMetadata]):
        """Test deleting story metadata"""
        workspace, metadata = workspace_with_metadata
        
        # Delete it
        result = await story_service.delete_story_metadata(workspace.id)
        assert result is True
        
        # Verify it's gone
        retrieved = await story_service.get_story_metadata_by_workspace(workspace.id)
        assert retrieved is None


class TestComplexOperations:
    """Test complex operations and statistics"""
    
    async def test_get_story_statistics(self, story_service: StoryService, empty_workspace: Workspace):
        """Test comprehensive story statistics calculation"""
        # Create metadata
        await story_service.create_story_metadata(StoryMetadataCreate(
            workspace_id=empty_workspace.id,
            title="Test Story",
            author="Test Author",
            total_chapters=10
        ))
        
        # Create chapters with varying states
        chapters = []
        for i in range(1, 6):
            chapter = await story_service.create_chapter(create_chapter_data(
                empty_workspace.id,
                i,
                content="Word " * (i * 10),  # 10, 20, 30, 40, 50 words
                status=ChapterStatus.PUBLISHED if i <= 3 else ChapterStatus.DRAFT
            ))
            chapters.append(chapter)
        
        # Get statistics
        stats = await story_service.get_story_statistics(empty_workspace.id)
        
        assert stats["workspace_id"] == empty_workspace.id
        assert stats["total_chapters"] == 5
        assert stats["published_chapters"] == 3
        assert stats["total_word_count"] == 150  # 10+20+30+40+50
        assert stats["published_word_count"] == 60  # 10+20+30
        assert stats["average_chapter_length"] == 30  # 150/5
        assert stats["latest_chapter_number"] == 5
        assert stats["story_metadata"] is not None
    
    async def test_get_story_statistics_empty_story(self, story_service: StoryService, empty_workspace: Workspace):
        """Test statistics for story with no chapters"""
        stats = await story_service.get_story_statistics(empty_workspace.id)
        
        assert stats["total_chapters"] == 0
        assert stats["published_chapters"] == 0
        assert stats["total_word_count"] == 0
        assert stats["average_chapter_length"] == 0
        assert stats["latest_chapter_number"] == 0
        assert stats["first_published"] is None
        assert stats["last_published"] is None
    
    async def test_reorder_chapters(self, story_service: StoryService, empty_workspace: Workspace):
        """Test reordering chapters by updating their numbers"""
        # Create 3 chapters
        ch1 = await story_service.create_chapter(
            create_chapter_data(empty_workspace.id, 1, title="First")
        )
        ch2 = await story_service.create_chapter(
            create_chapter_data(empty_workspace.id, 2, title="Second")
        )
        ch3 = await story_service.create_chapter(
            create_chapter_data(empty_workspace.id, 3, title="Third")
        )
        
        # Reorder: 3, 1, 2
        new_order = [ch3.id, ch1.id, ch2.id]
        reordered = await story_service.reorder_chapters(empty_workspace.id, new_order)
        
        # Verify new order
        assert len(reordered) == 3
        assert reordered[0].id == ch3.id and reordered[0].chapter_number == 1
        assert reordered[1].id == ch1.id and reordered[1].chapter_number == 2
        assert reordered[2].id == ch2.id and reordered[2].chapter_number == 3
    
    async def test_reorder_chapters_invalid_id(self, story_service: StoryService, empty_workspace: Workspace):
        """Test error when reordering with invalid chapter ID"""
        ch1 = await story_service.create_chapter(
            create_chapter_data(empty_workspace.id, 1)
        )
        
        fake_id = uuid4()
        with pytest.raises(ValueError) as exc_info:
            await story_service.reorder_chapters(empty_workspace.id, [ch1.id, fake_id])
        
        assert f"Chapter {fake_id} not found in workspace" in str(exc_info.value)
    
    async def test_validate_chapter_sequence_valid(self, story_service: StoryService, empty_workspace: Workspace):
        """Test validation of proper chapter sequence"""
        # Create sequential chapters
        await create_chapters_batch(story_service, empty_workspace.id, 5)
        
        validation = await story_service.validate_chapter_sequence(empty_workspace.id)
        
        assert validation["is_valid"] is True
        assert validation["total_chapters"] == 5
        assert validation["chapter_numbers"] == [1, 2, 3, 4, 5]
        assert len(validation["issues"]) == 0
    
    async def test_validate_chapter_sequence_gaps(self, story_service: StoryService, empty_workspace: Workspace):
        """Test detection of gaps in chapter numbering"""
        # Create chapters with gaps
        await story_service.create_chapter(
            create_chapter_data(empty_workspace.id, 1)
        )
        await story_service.create_chapter(
            create_chapter_data(empty_workspace.id, 3)
        )
        await story_service.create_chapter(
            create_chapter_data(empty_workspace.id, 6)
        )
        
        validation = await story_service.validate_chapter_sequence(empty_workspace.id)
        
        assert validation["is_valid"] is False
        assert validation["chapter_numbers"] == [1, 3, 6]
        assert len(validation["issues"]) == 2
        assert "Gap between chapters 1 and 3" in validation["issues"]
        assert "Gap between chapters 3 and 6" in validation["issues"]


class TestIntegration:
    """Integration tests for complete workflows"""
    
    async def test_full_story_workflow(self, story_service: StoryService, empty_workspace: Workspace):
        """Test a complete story creation and publication workflow"""
        # 1. Create story metadata
        metadata = await story_service.create_story_metadata(StoryMetadataCreate(
            workspace_id=empty_workspace.id,
            title="Complete Story Test",
            author="Integration Tester",
            total_chapters=5,
            genres=["Fantasy"]
        ))
        
        # 2. Create 5 chapters as drafts
        chapters = await create_chapters_batch(
            story_service, 
            empty_workspace.id, 
            5,
            status=ChapterStatus.DRAFT
        )
        
        # 3. Publish first 3 chapters
        for chapter in chapters[:3]:
            await story_service.publish_chapter(chapter.id)
        
        # 4. Get updated statistics
        stats = await story_service.get_story_statistics(empty_workspace.id)
        
        assert stats["total_chapters"] == 5
        assert stats["published_chapters"] == 3
        assert stats["story_metadata"].title == "Complete Story Test"
        
        # 5. Search for content
        results = await story_service.search_chapters(empty_workspace.id, "chapter 2")
        assert len(results) >= 1
        
        # 6. Validate sequence
        validation = await story_service.validate_chapter_sequence(empty_workspace.id)
        assert validation["is_valid"] is True
    
    async def test_concurrent_chapter_operations(self, story_service: StoryService, empty_workspace: Workspace):
        """Test that multiple operations don't interfere with each other"""
        # Create multiple chapters
        chapters = await create_chapters_batch(story_service, empty_workspace.id, 3)
        
        # Perform different operations
        await story_service.publish_chapter(chapters[0].id)
        await story_service.update_chapter_content(chapters[1].id, "New content")
        await story_service.delete_chapter(chapters[2].id)
        
        # Verify state
        final_chapters = await story_service.get_chapters_by_workspace(empty_workspace.id)
        assert len(final_chapters) == 2
        
        ch0 = next(c for c in final_chapters if c.id == chapters[0].id)
        ch1 = next(c for c in final_chapters if c.id == chapters[1].id)
        
        assert ch0.status == ChapterStatus.PUBLISHED
        assert ch1.content == "New content"