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

from src.database.factory import RepositoryContainer, create_repositories

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
    return create_repositories(backend="memory")


@pytest.fixture
async def database_setup():
    """Initialize database for database backend tests"""
    from src.database.connection import init_database, create_tables, close_database
    
    # Initialize database connection
    init_database()
    
    # Create tables
    await create_tables()
    
    yield
    
    # Cleanup
    await close_database()


@pytest.fixture
async def populated_repositories(repository_container: RepositoryContainer) -> Dict[str, Any]:
    """Provide repositories with sample data for integration tests."""
    
    # Create test project
    project_data = {
        "id": "test-project-123",
        "title": "Test Fantasy Novel",
        "description": "A test project for integration tests",
        "word_count": 2500,
        "document_count": 3,
        "tags": ["fantasy", "novel", "test"],
        "collaborators": [
            {
                "user_id": "user_1",
                "role": "owner",
                "name": "Test Author",
                "avatar": None
            }
        ],
        "settings": {
            "auto_save_interval": 30000,
            "word_count_target": 80000,
            "backup_enabled": True
        }
    }
    
    project = await repository_container.project.create(project_data)
    
    # Create test file tree structure
    # Root folders
    characters_folder = await repository_container.file_tree.create({
        "id": "folder-characters",
        "project_id": project.id,
        "name": "Characters",
        "type": "folder",
        "path": "/Characters",
        "parent_id": None,
        "tags": ["character"]
    })
    
    chapters_folder = await repository_container.file_tree.create({
        "id": "folder-chapters",
        "project_id": project.id,
        "name": "Chapters",
        "type": "folder",
        "path": "/Chapters",
        "parent_id": None,
        "tags": ["story"]
    })
    
    # Create test documents with different content types
    documents = []
    
    # Character document
    char_doc = await repository_container.document.create({
        "id": "doc-main-character",
        "project_id": project.id,
        "title": "Main Character Profile",
        "path": "/Characters/main_character.md",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Aria Thornfield is a 24-year-old mage with exceptional abilities in elemental magic. Born in the mountain village of Thornwick, she discovered her powers at age 12 when she accidentally froze the village well during a particularly emotional moment."
                        }
                    ]
                }
            ]
        },
        "tags": ["character", "protagonist", "mage"],
        "word_count": 45,
        "version": "1.0.0"
    })
    documents.append(char_doc)
    
    # Chapter documents
    for i in range(1, 3):
        chapter_doc = await repository_container.document.create({
            "id": f"doc-chapter-{i}",
            "project_id": project.id,
            "title": f"Chapter {i}: The Beginning",
            "path": f"/Chapters/chapter_{i:02d}.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [
                            {
                                "type": "text",
                                "text": f"Chapter {i}"
                            }
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": f"This is the content of chapter {i}. " * 50  # ~250 words
                            }
                        ]
                    }
                ]
            },
            "tags": ["chapter", "story"],
            "word_count": 250,
            "version": "1.0.0"
        })
        documents.append(chapter_doc)
    
    # Create file tree items for documents
    char_file = await repository_container.file_tree.create({
        "id": "file-main-character",
        "project_id": project.id,
        "name": "main_character.md",
        "type": "file",
        "path": "/Characters/main_character.md",
        "parent_id": characters_folder.id,
        "document_id": char_doc.id,
        "icon": "user",
        "tags": ["character", "protagonist"],
        "word_count": 45
    })
    
    file_tree_items = [characters_folder, chapters_folder, char_file]
    
    for i, doc in enumerate(documents[1:], 1):  # Skip character doc
        chapter_file = await repository_container.file_tree.create({
            "id": f"file-chapter-{i}",
            "project_id": project.id,
            "name": f"chapter_{i:02d}.md",
            "type": "file",
            "path": f"/Chapters/chapter_{i:02d}.md",
            "parent_id": chapters_folder.id,
            "document_id": doc.id,
            "icon": "file-text",
            "tags": ["chapter", "story"],
            "word_count": 250
        })
        file_tree_items.append(chapter_file)
    
    return {
        "container": repository_container,
        "project": project,
        "documents": documents,
        "file_tree_items": file_tree_items,
        "characters_folder": characters_folder,
        "chapters_folder": chapters_folder
    }


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "medium: marks tests as medium speed")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
