"""
Tests for InMemoryStoryRepository
"""
import pytest
from uuid import UUID, uuid4
from src.database.repositories.story.story_in_memory import InMemoryStoryRepository
from src.schemas.story import (
    StoryCreate, StoryUpdate, StoryStatus,
    ChapterCreate, StoryArcCreate, StoryArcUpdate, ArcStatus,
    EnhancedChapterCreate
)


class TestStoryRepository:
    """Test suite for story repository operations"""

    @pytest.mark.asyncio
    async def test_create_story(self, story_repo: InMemoryStoryRepository, test_user_id: UUID):
        """Test creating a new story"""
        story_create = StoryCreate(
            title="Pokemon Adventures",
            author="Ash Ketchum",
            owner_id=test_user_id
        )
        
        story = await story_repo.create_story(story_create)
        
        assert story.title == "Pokemon Adventures"
        assert story.author == "Ash Ketchum"
        assert story.status == StoryStatus.PENDING
        assert story.owner_id == test_user_id
        assert story.id is not None

    @pytest.mark.asyncio
    async def test_get_story_existing(self, story_repo: InMemoryStoryRepository, sample_story):
        """Test retrieving an existing story"""
        story = sample_story
        retrieved_story = await story_repo.get_story(story.id)
        
        assert retrieved_story.id == story.id
        assert retrieved_story.title == story.title
        assert retrieved_story.author == story.author

    @pytest.mark.asyncio
    async def test_get_story_nonexistent(self, story_repo: InMemoryStoryRepository):
        """Test retrieving a non-existent story returns empty story"""
        fake_id = uuid4()
        empty_story = await story_repo.get_story(fake_id)
        
        assert empty_story.id == UUID(int=0)
        assert empty_story.title == ""

    @pytest.mark.asyncio
    async def test_update_story(self, story_repo: InMemoryStoryRepository, sample_story):
        """Test updating an existing story"""
        story = sample_story
        update_data = StoryUpdate(status=StoryStatus.COMPLETED)
        
        updated_story = await story_repo.update_story(story.id, update_data)
        
        assert updated_story is not None
        assert updated_story.status == StoryStatus.COMPLETED
        assert updated_story.title == story.title  # Unchanged

    @pytest.mark.asyncio
    async def test_delete_story(self, story_repo: InMemoryStoryRepository, sample_story):
        """Test deleting a story"""
        story = sample_story
        result = await story_repo.delete_story(story.id)
        assert result is True
        
        # Verify story is gone
        empty_story = await story_repo.get_story(story.id)
        assert empty_story.id == UUID(int=0)

    @pytest.mark.asyncio
    async def test_get_stories_by_owner(self, story_repo: InMemoryStoryRepository, test_user_id: UUID):
        """Test getting stories filtered by owner"""
        # Create multiple stories
        story1 = await story_repo.create_story(StoryCreate(
            title="Story 1", author="Author 1", owner_id=test_user_id
        ))
        story2 = await story_repo.create_story(StoryCreate(
            title="Story 2", author="Author 2", owner_id=test_user_id
        ))
        
        # Create story with different owner
        other_user = uuid4()
        await story_repo.create_story(StoryCreate(
            title="Other Story", author="Other Author", owner_id=other_user
        ))
        
        # Test filtering
        user_stories = await story_repo.get_stories_by_owner(test_user_id)
        assert len(user_stories) == 2
        assert {s.title for s in user_stories} == {"Story 1", "Story 2"}


class TestChapterOperations:
    """Test suite for chapter operations"""

    @pytest.mark.asyncio
    async def test_create_chapter(self, story_repo: InMemoryStoryRepository, sample_story):
        """Test creating a chapter"""
        story = sample_story
        chapter_create = ChapterCreate(
            story_id=story.id,
            chapter_number=1,
            title="The Beginning",
            raw_content="Once upon a time..."
        )
        
        chapter = await story_repo.create_chapter(chapter_create)
        
        assert chapter.story_id == story.id
        assert chapter.chapter_number == 1
        assert chapter.title == "The Beginning"
        assert chapter.raw_content == "Once upon a time..."

    @pytest.mark.asyncio
    async def test_get_chapters_for_story(self, story_repo: InMemoryStoryRepository, sample_story):
        """Test retrieving chapters for a story"""
        story = sample_story
        # Create multiple chapters
        await story_repo.create_chapter(ChapterCreate(
            story_id=story.id, chapter_number=2, title="Chapter 2", raw_content="Content 2"
        ))
        await story_repo.create_chapter(ChapterCreate(
            story_id=story.id, chapter_number=1, title="Chapter 1", raw_content="Content 1"
        ))
        
        chapters = await story_repo.get_chapters(story.id)
        
        assert len(chapters) == 2
        # Should be sorted by chapter number
        assert chapters[0].chapter_number == 1
        assert chapters[1].chapter_number == 2

    @pytest.mark.asyncio
    async def test_get_chapters_basic(self, story_repo: InMemoryStoryRepository, sample_story):
        """Test retrieving chapters for a story"""
        story = sample_story
        await story_repo.create_chapter(ChapterCreate(
            story_id=story.id, chapter_number=1, title="Chapter 1", raw_content="Content 1"
        ))
        await story_repo.create_chapter(ChapterCreate(
            story_id=story.id, chapter_number=2, title="Chapter 2", raw_content="Content 2"
        ))
        await story_repo.create_chapter(ChapterCreate(
            story_id=story.id, chapter_number=3, title="Chapter 3", raw_content="Content 3"
        ))
        
        # Get all chapters
        chapters = await story_repo.get_chapters(story.id)
        
        assert len(chapters) == 3
        assert {c.chapter_number for c in chapters} == {1, 2, 3}


class TestStoryArcOperations:
    """Test suite for story arc operations"""

    @pytest.mark.asyncio
    async def test_create_story_arc(self, story_repo: InMemoryStoryRepository, sample_story):
        """Test creating a story arc"""
        story = sample_story
        arc_create = StoryArcCreate(
            story_id=story.id,
            arc_number=1,
            title="Introduction Arc",
            start_chapter=1,
            end_chapter=5,
            summary="The beginning of the story"
        )
        
        arc = await story_repo.create_story_arc(arc_create)
        
        assert arc.story_id == story.id
        assert arc.arc_number == 1
        assert arc.title == "Introduction Arc"
        assert arc.start_chapter == 1
        assert arc.end_chapter == 5

    @pytest.mark.asyncio
    async def test_get_story_arcs(self, story_repo: InMemoryStoryRepository, sample_story):
        """Test retrieving arcs for a story"""
        story = sample_story
        # Create multiple arcs
        await story_repo.create_story_arc(StoryArcCreate(
            story_id=story.id, arc_number=2, title="Arc 2",
            start_chapter=6, end_chapter=10
        ))
        await story_repo.create_story_arc(StoryArcCreate(
            story_id=story.id, arc_number=1, title="Arc 1",
            start_chapter=1, end_chapter=5
        ))
        
        arcs = await story_repo.get_story_arcs(story.id)
        
        assert len(arcs) == 2
        # Should be sorted by start_chapter
        assert arcs[0].start_chapter == 1
        assert arcs[1].start_chapter == 6

    @pytest.mark.asyncio
    async def test_update_story_arc(self, story_repo: InMemoryStoryRepository, sample_story):
        """Test updating a story arc"""
        story = sample_story
        arc = await story_repo.create_story_arc(StoryArcCreate(
            story_id=story.id, arc_number=1, title="Arc 1",
            start_chapter=1, end_chapter=5
        ))
        
        update_data = StoryArcUpdate(processing_status=ArcStatus.COMPLETED)
        updated_arc = await story_repo.update_story_arc(arc.id, update_data)
        
        assert updated_arc is not None
        assert updated_arc.processing_status == ArcStatus.COMPLETED
        assert updated_arc.title == "Arc 1"  # Unchanged


class TestEnhancedChapterOperations:
    """Test suite for enhanced chapter operations"""

    @pytest.mark.asyncio
    async def test_create_enhanced_chapter(self, story_repo: InMemoryStoryRepository, sample_story):
        """Test creating an enhanced chapter"""
        story = sample_story
        # First create a regular chapter
        chapter = await story_repo.create_chapter(ChapterCreate(
            story_id=story.id, chapter_number=1, title="Chapter 1", raw_content="Content"
        ))
        
        # Create an arc
        arc = await story_repo.create_story_arc(StoryArcCreate(
            story_id=story.id, arc_number=1, title="Arc 1",
            start_chapter=1, end_chapter=5
        ))
        
        # Create enhanced chapter
        enhanced_create = EnhancedChapterCreate(
            chapter_id=chapter.id,
            arc_id=arc.id,
            enhanced_content="Enhanced content with [[links]]",
            link_metadata={"links": ["character1", "location1"]}
        )
        
        enhanced = await story_repo.create_enhanced_chapter(enhanced_create)
        
        assert enhanced is not None
        assert enhanced.chapter_id == chapter.id
        assert enhanced.arc_id == arc.id
        assert enhanced.enhanced_content == "Enhanced content with [[links]]"
        
        assert enhanced.link_metadata is not None
        assert enhanced.link_metadata["links"] == ["character1", "location1"]

    @pytest.mark.asyncio
    async def test_get_enhanced_chapters_by_story(self, story_repo: InMemoryStoryRepository, sample_story):
        """Test retrieving enhanced chapters by story"""
        story = sample_story
        # Create test data
        chapter = await story_repo.create_chapter(ChapterCreate(
            story_id=story.id, chapter_number=1, title="Chapter 1", raw_content="Content"
        ))
        arc = await story_repo.create_story_arc(StoryArcCreate(
            story_id=story.id, arc_number=1, title="Arc 1",
            start_chapter=1, end_chapter=5
        ))
        enhanced = await story_repo.create_enhanced_chapter(EnhancedChapterCreate(
            chapter_id=chapter.id, arc_id=arc.id, enhanced_content="Enhanced content"
        ))
        
        # Test retrieval
        enhanced_chapters = await story_repo.get_enhanced_chapters(story_id=story.id)
        
        assert len(enhanced_chapters) == 1
        assert enhanced_chapters[0].id == enhanced.id

    @pytest.mark.asyncio
    async def test_get_enhanced_chapters_by_arc(self, story_repo: InMemoryStoryRepository, sample_story):
        """Test retrieving enhanced chapters by arc"""
        story = sample_story
        # Create test data
        chapter = await story_repo.create_chapter(ChapterCreate(
            story_id=story.id, chapter_number=1, title="Chapter 1", raw_content="Content"
        ))
        arc = await story_repo.create_story_arc(StoryArcCreate(
            story_id=story.id, arc_number=1, title="Arc 1",
            start_chapter=1, end_chapter=5
        ))
        enhanced = await story_repo.create_enhanced_chapter(EnhancedChapterCreate(
            chapter_id=chapter.id, arc_id=arc.id, enhanced_content="Enhanced content"
        ))

        # Test retrieval by arc
        enhanced_chapters = await story_repo.get_enhanced_chapters(story_id=story.id, arc_id=arc.id)
        
        assert len(enhanced_chapters) == 1
        assert enhanced_chapters[0].id == enhanced.id 