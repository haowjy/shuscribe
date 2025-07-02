"""
Tests for RepositoryFactory and RepositoryContainer
"""

import pytest
from unittest.mock import patch
from uuid import uuid4
from typing import Dict, Any

from src.database.factory import RepositoryFactory, RepositoryContainer, get_repositories
from src.database.interfaces import (
    IUserRepository,
    IWorkspaceRepository,
    IStoryRepository,
    IWikiRepository,
    IWritingRepository,
    IAgentRepository,
)


class TestRepositoryContainer:
    """Test the RepositoryContainer dataclass"""
    
    def test_repository_container_immutable(self, repository_container: RepositoryContainer):
        """Verify that RepositoryContainer is immutable (frozen)"""
        with pytest.raises(AttributeError):
            repository_container.user = None
    
    def test_repository_container_attribute_access(self, repository_container: RepositoryContainer):
        """Test that all repositories are accessible via attributes"""
        assert hasattr(repository_container, 'user')
        assert hasattr(repository_container, 'workspace')
        assert hasattr(repository_container, 'story')
        assert hasattr(repository_container, 'wiki')
        assert hasattr(repository_container, 'writing')
        assert hasattr(repository_container, 'agent')
        
        # Verify they're not None
        assert repository_container.user is not None
        assert repository_container.workspace is not None
        assert repository_container.story is not None
        assert repository_container.wiki is not None
        assert repository_container.writing is not None
        assert repository_container.agent is not None
    
    def test_repository_container_all_repositories_present(self, repository_container: RepositoryContainer):
        """Verify all 6 repository types are present and implement their interfaces"""
        assert isinstance(repository_container.user, IUserRepository)
        assert isinstance(repository_container.workspace, IWorkspaceRepository)
        assert isinstance(repository_container.story, IStoryRepository)
        assert isinstance(repository_container.wiki, IWikiRepository)
        assert isinstance(repository_container.writing, IWritingRepository)
        assert isinstance(repository_container.agent, IAgentRepository)


class TestMemoryBackend:
    """Test memory backend repository creation"""
    
    def test_memory_backend_creates_all_repositories(self):
        """Verify memory backend creates all 6 repository types"""
        repos = RepositoryFactory.create_repositories(backend="memory")
        
        # Check all repositories exist
        assert repos.user is not None
        assert repos.workspace is not None
        assert repos.story is not None
        assert repos.wiki is not None
        assert repos.writing is not None
        assert repos.agent is not None
    
    def test_memory_backend_repositories_are_independent(self):
        """Each factory call should create new repository instances"""
        repos1 = RepositoryFactory.create_repositories(backend="memory")
        repos2 = RepositoryFactory.create_repositories(backend="memory")
        
        # They should be different instances
        assert repos1.user is not repos2.user
        assert repos1.workspace is not repos2.workspace
        assert repos1.story is not repos2.story
        assert repos1.wiki is not repos2.wiki
        assert repos1.writing is not repos2.writing
        assert repos1.agent is not repos2.agent
    
    async def test_memory_backend_data_isolation(self):
        """Data in one container should not affect another"""
        from src.schemas.db.user import UserCreate
        
        repos1 = RepositoryFactory.create_repositories(backend="memory")
        repos2 = RepositoryFactory.create_repositories(backend="memory")
        
        # Create user in first repository
        user_data = UserCreate(email="test1@example.com", display_name="Test User 1")
        user1 = await repos1.user.create_user(user_data)
        
        # Verify user doesn't exist in second repository
        user2_check = await repos2.user.get_user(user1.id)
        assert user2_check is None
        
        # Verify user exists in first repository
        user1_check = await repos1.user.get_user(user1.id)
        assert user1_check is not None
        assert user1_check.email == "test1@example.com"
    
    def test_memory_repositories_implement_interfaces(self):
        """Verify each memory repository implements its interface correctly"""
        repos = RepositoryFactory.create_repositories(backend="memory")
        
        # Check that each repository has the expected interface methods
        # User repository
        assert hasattr(repos.user, 'create_user')
        assert hasattr(repos.user, 'get_user')
        assert hasattr(repos.user, 'update_user')
        assert hasattr(repos.user, 'delete_user')
        
        # Workspace repository
        assert hasattr(repos.workspace, 'create_workspace')
        assert hasattr(repos.workspace, 'get_workspace')
        assert hasattr(repos.workspace, 'update_workspace')
        assert hasattr(repos.workspace, 'delete_workspace')
        
        # Story repository
        assert hasattr(repos.story, 'create_chapter')
        assert hasattr(repos.story, 'get_chapter')
        assert hasattr(repos.story, 'update_chapter')
        assert hasattr(repos.story, 'delete_chapter')
        
        # Wiki repository
        assert hasattr(repos.wiki, 'create_article')
        assert hasattr(repos.wiki, 'get_article')
        assert hasattr(repos.wiki, 'update_article')
        assert hasattr(repos.wiki, 'delete_article')
        
        # Writing repository
        assert hasattr(repos.writing, 'create_author_note')
        assert hasattr(repos.writing, 'get_author_note')
        assert hasattr(repos.writing, 'update_author_note')
        assert hasattr(repos.writing, 'delete_author_note')
        
        # Agent repository
        assert hasattr(repos.agent, 'create_conversation')
        assert hasattr(repos.agent, 'get_conversation')
        assert hasattr(repos.agent, 'update_conversation')
        assert hasattr(repos.agent, 'delete_conversation')


class TestFactoryErrors:
    """Test error handling in the factory"""
    
    def test_unknown_backend_raises_error(self):
        """Test that invalid backend type raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            RepositoryFactory.create_repositories(backend="invalid_backend")
        
        assert "Unknown backend type: invalid_backend" in str(exc_info.value)
    
    @patch('src.database.factory.settings')
    def test_default_backend_from_settings(self, mock_settings):
        """Verify factory uses settings.DATABASE_BACKEND when not specified"""
        mock_settings.DATABASE_BACKEND = "memory"
        
        repos = RepositoryFactory.create_repositories()
        
        # Should create memory repositories
        assert repos is not None
        assert repos.user is not None


class TestGetRepositoriesFunction:
    """Test the convenience function get_repositories"""
    
    def test_get_repositories_convenience_function(self):
        """Test that get_repositories works correctly"""
        repos = get_repositories(backend="memory")
        
        assert isinstance(repos, RepositoryContainer)
        assert repos.user is not None
        assert repos.workspace is not None
        assert repos.story is not None
        assert repos.wiki is not None
        assert repos.writing is not None
        assert repos.agent is not None
    
    def test_get_repositories_passes_kwargs(self):
        """Verify additional parameters are passed through"""
        # For memory backend, kwargs are ignored, but let's test they don't cause errors
        repos = get_repositories(
            backend="memory",
            some_param="value",
            another_param=123
        )
        
        assert isinstance(repos, RepositoryContainer)


class TestIntegration:
    """Integration tests using multiple repositories together"""
    
    async def test_cross_repository_workflow(self, repository_container: RepositoryContainer):
        """Test a workflow that uses multiple repositories"""
        from src.schemas.db.user import UserCreate
        from src.schemas.db.workspace import WorkspaceCreate
        from src.schemas.db.story import ChapterCreate, ChapterStatus
        
        # Create a user
        user = await repository_container.user.create_user(UserCreate(
            email="workflow@example.com",
            display_name="Workflow Test"
        ))
        
        # Create a workspace for the user
        workspace = await repository_container.workspace.create_workspace(WorkspaceCreate(
            owner_id=user.id,
            name="Test Workspace",
            description="Testing cross-repository workflow"
        ))
        
        # Create a chapter in the workspace
        chapter = await repository_container.story.create_chapter(ChapterCreate(
            workspace_id=workspace.id,
            title="Chapter 1",
            content="Test content",
            chapter_number=1,
            status=ChapterStatus.DRAFT
        ))
        
        # Verify relationships
        assert chapter.workspace_id == workspace.id
        assert workspace.owner_id == user.id
        
        # Verify data persistence within the container
        retrieved_user = await repository_container.user.get_user(user.id)
        retrieved_workspace = await repository_container.workspace.get_workspace(workspace.id)
        retrieved_chapter = await repository_container.story.get_chapter(chapter.id)
        
        assert retrieved_user is not None
        assert retrieved_workspace is not None
        assert retrieved_chapter is not None
        assert retrieved_user.email == "workflow@example.com"
        assert retrieved_workspace.name == "Test Workspace"
        assert retrieved_chapter.title == "Chapter 1"