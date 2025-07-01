"""
Database-specific conftest.py for ShuScribe database tests

Fixtures and utilities specific to database layer testing.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import AsyncIterator, Dict, Any, Tuple
from uuid import UUID

import pytest

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from src.database.factory import get_repositories
from src.database.models.repositories import FileRepositories, Repositories
from src.database.models.user import UserCreate, UserAPIKeyCreate, SubscriptionTier
from src.database.models.workspace import WorkspaceCreate  
from src.database.models.story import ChapterCreate, ChapterStatus, StoryMetadataCreate
from src.database.models.wiki import WikiArticleCreate, WikiArticleType
from src.database.file.user import FileUserRepository
from typing import cast


@pytest.fixture
async def file_repos(temp_workspace_path: Path) -> AsyncIterator[Repositories]:
    """Create file-based repositories for testing."""
    repos = get_repositories(backend="file", workspace_path=temp_workspace_path)
    yield repos


@pytest.fixture
async def user_repo(file_repos: Repositories):
    """Get user repository from file repos."""
    return file_repos.user


@pytest.fixture
async def workspace_repo(file_repos: Repositories):
    """Get workspace repository from file repos."""
    return file_repos.workspace


@pytest.fixture
async def story_repo(file_repos: Repositories):
    """Get story repository from file repos."""
    return file_repos.story


@pytest.fixture
async def wiki_repo(file_repos: Repositories):
    """Get wiki repository from file repos."""
    return file_repos.wiki


@pytest.fixture
async def current_user(user_repo):
    """Get the current user (created automatically by file repos)."""
    return await cast(FileUserRepository, user_repo).get_current_user()


@pytest.fixture
async def sample_workspace(workspace_repo, current_user):
    """Create a sample workspace for testing."""
    workspace_data = WorkspaceCreate(
        name="Test Workspace",
        description="A workspace for testing",
        owner_id=current_user.id
    )
    return await workspace_repo.create(workspace_data)


@pytest.fixture
async def sample_chapters(story_repo, sample_workspace):
    """Create sample chapters for testing."""
    chapters = []
    for i in range(1, 4):
        chapter_data = ChapterCreate(
            workspace_id=sample_workspace.id,
            title=f"Chapter {i}: Test Chapter",
            content=f"This is the content of chapter {i}. It contains {i*100} words of exciting story content.",
            chapter_number=i,
            status=ChapterStatus.PUBLISHED
        )
        chapter = await story_repo.create_chapter(chapter_data)
        chapters.append(chapter)
    return chapters


@pytest.fixture
async def sample_wiki_articles(wiki_repo, sample_workspace):
    """Create sample wiki articles for testing."""
    articles = []
    
    # Character article
    character_data = WikiArticleCreate(
        title="Test Character",
        article_type=WikiArticleType.CHARACTER,
        content="A mysterious character who appears in the story.",
        safe_through_chapter=1
    )
    character = await wiki_repo.create_article(sample_workspace.id, character_data)
    articles.append(character)
    
    # Location article
    location_data = WikiArticleCreate(
        title="Test Location",
        article_type=WikiArticleType.LOCATION,
        content="A mystical place where adventures happen.",
        safe_through_chapter=2
    )
    location = await wiki_repo.create_article(sample_workspace.id, location_data)
    articles.append(location)
    
    return articles


@pytest.fixture
def sample_api_keys():
    """Sample API keys for testing."""
    return [
        UserAPIKeyCreate(
            provider="openai",
            api_key="sk-test-openai-123456",
            provider_metadata={"model": "gpt-4", "max_tokens": 4000}
        ),
        UserAPIKeyCreate(
            provider="anthropic", 
            api_key="sk-ant-test-456789",
            provider_metadata={"model": "claude-3-sonnet", "max_tokens": 8000}
        ),
        UserAPIKeyCreate(
            provider="google",
            api_key="goog-test-789012",
            provider_metadata={"model": "gemini-2.0-flash-001"}
        )
    ]


@pytest.fixture(scope="session")
async def pokemon_amber_workspace() -> AsyncIterator[Tuple[Path, Dict[str, Any]]]:
    """Import Pokemon Amber story once per test session for integration tests."""
    backend_root = Path(__file__).parent.parent.parent
    temp_root = backend_root / "temp" 
    temp_root.mkdir(exist_ok=True)
    
    workspace_path = temp_root / "pokemon_amber_test"
    
    # Import Pokemon Amber using the StoryImporter from utils
    try:
        # Import StoryImporter directly from the utils module
        import sys
        sys.path.insert(0, str(backend_root))
        from src.utils.test.import_story import StoryImporter
        
        importer = StoryImporter(workspace_path)
        pokemon_dir = backend_root / "tests" / "resources" / "pokemon_amber" / "story"
        
        if pokemon_dir.exists():
            # Import real Pokemon Amber data
            result = await importer.import_story_from_directory(pokemon_dir)
            yield workspace_path, result
        else:
            # Fallback to mock data if Pokemon Amber resources not available
            repos = cast(FileRepositories, get_repositories(backend="file", workspace_path=workspace_path))
            user = await cast(FileUserRepository, repos.user).get_current_user()
            
            workspace = await repos.workspace.create(WorkspaceCreate(
                name="Mock Pokemon Story",
                description="Mock story for testing",
                owner_id=user.id
            ))
            
            # Create mock chapters
            for i in range(1, 6):
                await repos.story.create_chapter(ChapterCreate(
                    workspace_id=workspace.id,
                    title=f"Mock Chapter {i}",
                    content=f"Mock content for chapter {i} " * 50,  # ~250 words
                    chapter_number=i,
                    status=ChapterStatus.PUBLISHED
                ))
            
            # Create story metadata
            await repos.story.create_story_metadata(
                workspace_id=workspace.id,
                title="Mock Pokemon Story",
                author="Mock Author",
                synopsis="A mock story for testing purposes",
                genres=["Adventure", "Fantasy"],
                tags=["pokemon", "test", "mock"],
                total_chapters=5
            )
            
            # Refresh stats to update published_chapters and word_count
            await repos.story.refresh_chapter_stats(workspace.id)
            
            result = {
                "workspace_id": str(workspace.id),
                "story_title": "Mock Pokemon Story", 
                "chapters_imported": 5,
                "workspace_path": str(workspace_path)
            }
            yield workspace_path, result
        
    finally:
        # Cleanup
        if workspace_path.exists():
            import shutil
            shutil.rmtree(workspace_path)


@pytest.fixture
async def wiki_with_versions(wiki_repo, sample_workspace):
    """Create wiki article with multiple chapter versions for spoiler testing."""
    # Create base article
    article_data = WikiArticleCreate(
        title="Evolving Character",
        article_type=WikiArticleType.CHARACTER,
        content="Full character description with all spoilers revealed.",
        safe_through_chapter=5
    )
    article = await wiki_repo.create_article(sample_workspace.id, article_data)
    
    # Create chapter-specific versions
    versions = []
    
    # Version 1: Basic introduction
    version1 = await wiki_repo.create_chapter_version(
        article.id,
        content="A mysterious stranger appears in town.",
        safe_through_chapter=1
    )
    versions.append(version1)
    
    # Version 2: More details revealed
    version2 = await wiki_repo.create_chapter_version(
        article.id,
        content="A mysterious stranger with magical abilities appears in town.",
        safe_through_chapter=2
    )
    versions.append(version2)
    
    # Version 3: Background revealed
    version3 = await wiki_repo.create_chapter_version(
        article.id,
        content="A mysterious stranger with magical abilities appears in town. They are actually the lost prince of the realm.",
        safe_through_chapter=3
    )
    versions.append(version3)
    
    return article, versions


@pytest.fixture
def workspace_factory(temp_workspace_path):
    """Factory for creating test workspaces with custom configurations."""
    created_workspaces = []
    
    async def create_workspace(
        name: str = "Factory Workspace",
        chapter_count: int = 0,
        wiki_count: int = 0,
        with_api_keys: bool = False
    ) -> Tuple[Path, FileRepositories, UUID]:
        """Create a workspace with specified content."""
        # Create unique path
        from uuid import uuid4
        workspace_path = temp_workspace_path.parent / f"{temp_workspace_path.name}_{uuid4().hex[:8]}"
        created_workspaces.append(workspace_path)
        
        repos = cast(FileRepositories, get_repositories(backend="file", workspace_path=workspace_path))
        user = await cast(FileUserRepository, repos.user).get_current_user()
        
        # Create workspace
        workspace = await repos.workspace.create(WorkspaceCreate(
            name=name,
            owner_id=user.id
        ))
        
        # Add chapters if requested
        if chapter_count > 0:
            for i in range(1, chapter_count + 1):
                await repos.story.create_chapter(ChapterCreate(
                    workspace_id=workspace.id,
                    title=f"Chapter {i}",
                    content=f"Content for chapter {i} " * 20,
                    chapter_number=i,
                    status=ChapterStatus.PUBLISHED
                ))
        
        # Add wiki articles if requested
        if wiki_count > 0:
            for i in range(wiki_count):
                await repos.wiki.create_article(workspace.id, WikiArticleCreate(
                    title=f"Wiki Article {i+1}",
                    article_type=WikiArticleType.CHARACTER,
                    content=f"Content for wiki article {i+1}",
                    safe_through_chapter=1
                ))
        
        # Add API keys if requested
        if with_api_keys:
            await repos.user.store_api_key(user.id, UserAPIKeyCreate(
                provider="test", api_key="test-key-123"
            ))
        
        return workspace_path, repos, workspace.id
    
    yield create_workspace
    
    # Cleanup created workspaces
    import shutil
    for workspace_path in created_workspaces:
        if workspace_path.exists():
            shutil.rmtree(workspace_path)


@pytest.fixture
def config_checker():
    """Utility for checking configuration file contents."""
    def check_config(workspace_path: Path) -> Dict[str, Any]:
        """Check configuration file contents."""
        config_file = workspace_path / ".shuscribe" / "config.json"
        if config_file.exists():
            return json.loads(config_file.read_text())
        return {}
    
    return check_config
