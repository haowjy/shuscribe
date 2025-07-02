"""
Test utilities for story service tests
"""

from typing import List, Dict, Any
from uuid import UUID

from src.schemas.db.story import Chapter, ChapterCreate, ChapterStatus
from src.services.story.story_service import StoryService


def assert_chapter_equal(actual: Chapter, expected: dict):
    """Assert that a chapter matches expected values."""
    for key, value in expected.items():
        if hasattr(actual, key):
            assert getattr(actual, key) == value, f"Chapter.{key} mismatch: {getattr(actual, key)} != {value}"
        else:
            raise AssertionError(f"Chapter has no attribute '{key}'")


def create_chapter_data(
    workspace_id: UUID, 
    number: int, 
    **overrides
) -> ChapterCreate:
    """Factory for creating test chapter data."""
    defaults = {
        "workspace_id": workspace_id,
        "title": f"Chapter {number}",
        "content": f"This is the content for chapter {number}. " * 50,  # ~50 words
        "chapter_number": number,
        "status": ChapterStatus.DRAFT,
        "summary": f"Summary of chapter {number}",
        "tags": ["test", f"chapter-{number}"],
        "metadata": {"test": True, "number": number}
    }
    
    # Apply overrides
    defaults.update(overrides)
    
    return ChapterCreate(**defaults)


async def create_chapters_batch(
    story_service: StoryService, 
    workspace_id: UUID, 
    count: int,
    start_number: int = 1,
    **overrides
) -> List[Chapter]:
    """Create multiple chapters efficiently."""
    chapters = []
    
    for i in range(start_number, start_number + count):
        chapter_data = create_chapter_data(workspace_id, i, **overrides)
        chapter = await story_service.create_chapter(chapter_data)
        chapters.append(chapter)
    
    return chapters


def calculate_expected_statistics(chapters: List[Chapter], metadata: Any = None) -> Dict[str, Any]:
    """Calculate expected statistics for comparison."""
    published_chapters = [c for c in chapters if c.status == ChapterStatus.PUBLISHED]
    total_words = sum(len(c.content.split()) for c in chapters)
    published_words = sum(len(c.content.split()) for c in published_chapters)
    
    stats: Dict[str, Any] = {
        "total_chapters": len(chapters),
        "published_chapters": len(published_chapters),
        "total_word_count": total_words,
        "published_word_count": published_words,
        "average_chapter_length": total_words // len(chapters) if chapters else 0,
        "latest_chapter_number": max((c.chapter_number for c in chapters), default=0),
    }
    
    if published_chapters:
        stats["first_published"] = min(c.published_at for c in published_chapters if c.published_at)
        stats["last_published"] = max(c.published_at for c in published_chapters if c.published_at)
    else:
        stats["first_published"] = None
        stats["last_published"] = None
    
    return stats