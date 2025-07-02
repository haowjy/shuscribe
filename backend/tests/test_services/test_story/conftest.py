"""
Story service specific test fixtures
"""

import pytest
from uuid import UUID
from typing import Tuple

from src.schemas.db.user import UserCreate
from src.schemas.db.workspace import WorkspaceCreate, Workspace
from src.schemas.db.story import StoryMetadata
from src.services.story.story_service import StoryService
from src.database.factory import RepositoryContainer


@pytest.fixture
async def story_service(repository_container: RepositoryContainer) -> StoryService:
    """Provide StoryService with memory repositories."""
    return StoryService(
        story_repository=repository_container.story,
        workspace_repository=repository_container.workspace
    )


@pytest.fixture
async def empty_workspace(repository_container: RepositoryContainer) -> Workspace:
    """Create an empty workspace for testing."""
    # Create user first
    user = await repository_container.user.create_user(UserCreate(
        email="empty@example.com",
        display_name="Empty User"
    ))
    
    # Create workspace
    workspace = await repository_container.workspace.create_workspace(WorkspaceCreate(
        owner_id=user.id,
        name="Empty Story",
        description="Empty workspace for testing"
    ))
    
    return workspace


@pytest.fixture
async def workspace_with_metadata(repository_container: RepositoryContainer, empty_workspace: Workspace) -> Tuple[Workspace, StoryMetadata]:
    """Create a workspace with story metadata but no chapters."""
    from src.schemas.db.story import StoryMetadataCreate
    
    metadata = await repository_container.story.create_story_metadata(StoryMetadataCreate(
        workspace_id=empty_workspace.id,
        title="Test Story with Metadata",
        author="Test Author",
        synopsis="A story created for testing",
        genres=["Fantasy", "Adventure"],
        total_chapters=20
    ))
    
    return empty_workspace, metadata