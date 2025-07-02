"""
Root conftest.py for ShuScribe backend tests

Shared fixtures and utilities for all test modules.
"""

import asyncio
import pytest
import shutil
from pathlib import Path
from typing import Iterator, AsyncIterator, Dict, Any
from uuid import uuid4

from src.database.factory import RepositoryContainer

# Async test support
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """Create a temporary directory in backend/temp that's cleaned up after test."""
    backend_root = Path(__file__).parent.parent
    temp_root = backend_root / "temp"
    temp_root.mkdir(exist_ok=True)
    
    # Create unique temp directory
    temp_name = f"test_temp_{uuid4().hex[:8]}"
    temp_path = temp_root / temp_name
    temp_path.mkdir()
    
    yield temp_path
    
    # Cleanup after test
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def temp_workspace_path() -> Iterator[Path]:
    """Create a temporary workspace path in temp/ directory."""
    backend_root = Path(__file__).parent.parent
    temp_root = backend_root / "temp"
    temp_root.mkdir(exist_ok=True)
    
    # Create unique workspace path
    workspace_name = f"test_workspace_{uuid4().hex[:8]}"
    workspace_path = temp_root / workspace_name
    
    yield workspace_path
    
    # Cleanup after test
    if workspace_path.exists():
        shutil.rmtree(workspace_path)


@pytest.fixture(scope="session", autouse=True)
def cleanup_temp_workspaces():
    """Clean up any leftover temp workspaces and directories at start and end of test session."""
    backend_root = Path(__file__).parent.parent
    temp_root = backend_root / "temp"
    
    def cleanup():
        if temp_root.exists():
            for item in temp_root.iterdir():
                if item.is_dir() and (item.name.startswith("test_workspace_") or item.name.startswith("test_temp_")):
                    try:
                        shutil.rmtree(item)
                    except:
                        pass  # Ignore cleanup errors
    
    # Clean up at start of session
    cleanup()
    
    yield
    
    # Clean up at end of session
    cleanup()


# Repository fixtures
@pytest.fixture
async def repository_container() -> RepositoryContainer:
    """Provide a RepositoryContainer with memory repositories for testing."""
    from src.database.factory import get_repositories
    return get_repositories(backend="memory")


@pytest.fixture
async def populated_repositories(repository_container: RepositoryContainer) -> Dict[str, Any]:
    """Provide repositories with sample data for integration tests."""
    from src.schemas.db.user import UserCreate
    from src.schemas.db.workspace import WorkspaceCreate, Arc
    from src.schemas.db.story import ChapterCreate, ChapterStatus, StoryMetadataCreate
    
    # Create test user
    user = await repository_container.user.create_user(UserCreate(
        email="test@example.com",
        display_name="Test User"
    ))
    
    # Create test workspace with arcs
    workspace = await repository_container.workspace.create_workspace(WorkspaceCreate(
        owner_id=user.id,
        name="Test Story",
        description="Test workspace for story",
        arcs=[Arc(
            name="First Arc",
            description="The beginning",
            start_chapter=1,
            end_chapter=10
        )]
    ))
    
    # Create test chapters (mix of published and draft)
    chapters = []
    for i in range(1, 6):
        chapter = await repository_container.story.create_chapter(ChapterCreate(
            workspace_id=workspace.id,
            title=f"Chapter {i}",
            content=f"Content for chapter {i}. " * 100,  # ~100 words
            chapter_number=i,
            status=ChapterStatus.PUBLISHED if i <= 3 else ChapterStatus.DRAFT
        ))
        chapters.append(chapter)
    
    # Create story metadata
    metadata = await repository_container.story.create_story_metadata(StoryMetadataCreate(
        workspace_id=workspace.id,
        title="Test Story",
        author="Test Author",
        synopsis="A test story for unit testing",
        genres=["Fantasy", "Adventure"],
        total_chapters=10
    ))
    
    return {
        "container": repository_container,
        "user": user,
        "workspace": workspace,
        "chapters": chapters,
        "metadata": metadata
    }


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "medium: marks tests as medium speed")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
