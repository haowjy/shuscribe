"""
Pytest configuration and fixtures for ShuScribe tests
"""
import asyncio
from pathlib import Path
from typing import Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from uuid import UUID

from src.database.repositories.story.story_in_memory import InMemoryStoryRepository
from src.database.repositories.wikipage.wikipage_in_memory import InMemoryWikiPageRepository
from src.schemas.story import StoryCreate, ChapterCreate, StoryArcCreate, StoryStatus, ArcStatus
from src.schemas.wiki import (
    WikiPageCreate, ArticleCreate, ArticleSnapshotCreate, 
    ArticleStoryAssociationCreate, WikiPageArticleLinkCreate,
    ArticleType
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_user_id() -> UUID:
    """Standard test user ID"""
    return uuid4()


@pytest.fixture
def story_repo() -> InMemoryStoryRepository:
    """Fresh story repository for each test"""
    return InMemoryStoryRepository()


@pytest.fixture
def wiki_repo() -> InMemoryWikiPageRepository:
    """Fresh wiki repository for each test"""
    return InMemoryWikiPageRepository()


@pytest.fixture
def pokemon_story_path() -> Path:
    """Path to Pokemon Amber test story"""
    return Path(__file__).parent / "resources" / "pokemon_amber" / "story"


# Sample data factories
@pytest_asyncio.fixture
async def sample_story(story_repo: InMemoryStoryRepository, test_user_id: UUID):
    """Create a sample story for testing"""
    story_create = StoryCreate(
        title="Test Story",
        author="Test Author",
        status=StoryStatus.PENDING,
        owner_id=test_user_id
    )
    return await story_repo.create_story(story_create)


@pytest_asyncio.fixture
async def sample_wiki_page(wiki_repo: InMemoryWikiPageRepository, test_user_id: UUID):
    """Create a sample wiki page for testing"""
    wiki_create = WikiPageCreate(
        title="Test Wiki",
        description="Test wiki description",
        is_public=False,
        safe_through_chapter=0,
        creator_id=test_user_id
    )
    return await wiki_repo.create_wiki_page(wiki_create)


@pytest_asyncio.fixture
async def sample_article(wiki_repo: InMemoryWikiPageRepository, test_user_id: UUID):
    """Create a sample base article for testing"""
    article_create = ArticleCreate(
        title="Test Character",
        slug="test-character",
        article_type=ArticleType.CHARACTER,
        canonical_name="Test Character",
        aliases=["TC", "Tester"],
        tags=["main", "protagonist"],
        creator_id=test_user_id
    )
    return await wiki_repo.create_article(article_create)
