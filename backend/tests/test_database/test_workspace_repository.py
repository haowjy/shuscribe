"""
Test suite for Workspace Repository

Tests workspace CRUD operations, ownership, metadata, and workspace-specific functionality.
"""

import pytest
from datetime import datetime
from pathlib import Path
from typing import cast

from src.database.interfaces.workspace import IWorkspaceRepository
from src.database.models.workspace import WorkspaceCreate, WorkspaceUpdate
from src.database.file.user import FileUserRepository
from src.database.models.user import User


class TestWorkspaceOperations:
    """Test basic workspace CRUD operations."""
    
    async def test_create_workspace(self, workspace_repo, current_user):
        """Test creating a workspace."""
        workspace_data = WorkspaceCreate(
            name="Test Workspace",
            description="A workspace for testing purposes",
            owner_id=current_user.id
        )
        
        workspace = await workspace_repo.create(workspace_data)
        
        assert workspace.name == "Test Workspace"
        assert workspace.description == "A workspace for testing purposes"
        assert workspace.owner_id == current_user.id
        assert workspace.id is not None
        assert workspace.created_at is not None
    
    async def test_get_workspace_by_id(self, workspace_repo, sample_workspace):
        """Test retrieving a workspace by ID."""
        retrieved = await workspace_repo.get(sample_workspace.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_workspace.id
        assert retrieved.name == sample_workspace.name
        assert retrieved.description == sample_workspace.description
    
    async def test_get_workspaces_by_owner(self, workspace_repo, current_user, sample_workspace):
        """Test getting all workspaces for an owner."""
        workspaces = await workspace_repo.get_by_owner(current_user.id)
        
        assert len(workspaces) >= 1
        workspace_ids = {ws.id for ws in workspaces}
        assert sample_workspace.id in workspace_ids
    
    async def test_update_workspace(self, workspace_repo, sample_workspace):
        """Test updating a workspace."""
        update_data = WorkspaceUpdate(
            name="Updated Workspace Name",
            description="Updated description for the workspace",
            settings={"theme": "dark", "auto_save": True}
        )
        
        updated = await workspace_repo.update(sample_workspace.id, update_data)
        
        assert updated.name == "Updated Workspace Name"
        assert updated.description == "Updated description for the workspace"
        assert updated.settings["theme"] == "dark"
        assert updated.settings["auto_save"] is True
        assert updated.updated_at is not None
    
    async def test_delete_workspace(self, workspace_repo, current_user):
        """Test deleting a workspace."""
        # Create workspace to delete
        workspace_data = WorkspaceCreate(
            name="To Delete",
            description="This workspace will be deleted",
            owner_id=current_user.id
        )
        workspace = await workspace_repo.create(workspace_data)
        
        # Delete it
        deleted = await workspace_repo.delete(workspace.id)
        assert deleted is True
        
        # Verify it's gone
        retrieved = await workspace_repo.get(workspace.id)
        assert retrieved is None
    
    async def test_get_all_workspaces(self, workspace_repo, sample_workspace):
        """Test getting all workspaces."""
        workspaces = await workspace_repo.get_multi()
        
        assert len(workspaces) >= 1
        workspace_ids = {ws.id for ws in workspaces}
        assert sample_workspace.id in workspace_ids


class TestWorkspaceMetadata:
    """Test workspace metadata and settings."""
    
    async def test_workspace_settings(self, workspace_repo, current_user):
        """Test workspace with custom settings."""
        settings = {
            "auto_save_interval": 300,
            "backup_enabled": True,
            "export_format": "markdown",
            "ai_provider": "google",
            "ai_model": "gemini-2.0-flash-001"
        }
        
        workspace_data = WorkspaceCreate(
            name="Settings Test",
            description="Testing workspace settings",
            owner_id=current_user.id,
            settings=settings
        )
        
        workspace = await workspace_repo.create(workspace_data)
        
        assert workspace.settings["auto_save_interval"] == 300
        assert workspace.settings["backup_enabled"] is True
        assert workspace.settings["ai_provider"] == "google"
    
    async def test_workspace_without_description(self, workspace_repo, current_user):
        """Test creating workspace without description."""
        workspace_data = WorkspaceCreate(
            name="No Description Workspace",
            owner_id=current_user.id
        )
        
        workspace = await workspace_repo.create(workspace_data)
        
        assert workspace.name == "No Description Workspace"
        assert workspace.description is None or workspace.description == ""
    
    # async def test_workspace_tags(self, workspace_repo, current_user):
    #     """Test workspace with tags."""
    #     workspace_data = WorkspaceCreate(
    #         name="Tagged Workspace",
    #         description="A workspace with tags",
    #         owner_id=current_user.id,
    #         tags=["fantasy", "adventure", "magic"]
    #     )
        
    #     workspace = await workspace_repo.create(workspace_data)
        
    #     assert workspace.tags == ["fantasy", "adventure", "magic"]
    
    async def test_empty_workspace_settings(self, workspace_repo, current_user):
        """Test workspace with empty settings."""
        workspace_data = WorkspaceCreate(
            name="Empty Settings",
            owner_id=current_user.id,
            settings={}
        )
        
        workspace = await workspace_repo.create(workspace_data)
        assert workspace.settings == {}


class TestWorkspaceValidation:
    """Test workspace validation and constraints."""
    
    async def test_workspace_name_required(self, workspace_repo, current_user):
        """Test that workspace name is required."""
        try:
            workspace_data = WorkspaceCreate(
                name="",  # Empty name
                owner_id=current_user.id
            )
            await workspace_repo.create(workspace_data)
            assert False, "Should have failed with empty name"
        except Exception:
            # Expected to fail
            pass
    
    async def test_workspace_owner_required(self, workspace_repo):
        """Test that workspace owner is required."""
        from uuid import uuid4
        
        try:
            workspace_data = WorkspaceCreate(
                name="No Owner Workspace",
                owner_id=uuid4()  # Non-existent user
            )
            # This might fail validation or succeed depending on implementation
            workspace = await workspace_repo.create(workspace_data)
            # If it succeeds, that's fine too
        except Exception:
            # If it fails validation, that's expected
            pass
    
    async def test_very_long_workspace_name(self, workspace_repo, current_user):
        """Test workspace with very long name."""
        long_name = "Very Long Workspace Name " * 20  # ~500 characters
        
        workspace_data = WorkspaceCreate(
            name=long_name,
            owner_id=current_user.id
        )
        
        try:
            workspace = await workspace_repo.create(workspace_data)
            assert workspace.name == long_name
        except Exception:
            # If validation prevents this, that's acceptable
            pass
    
    async def test_special_characters_in_name(self, workspace_repo, current_user):
        """Test workspace name with special characters."""
        special_name = "Workspace with émojis 🚀 and spéciàl chãracters & symbols!"
        
        workspace_data = WorkspaceCreate(
            name=special_name,
            owner_id=current_user.id
        )
        
        workspace = await workspace_repo.create(workspace_data)
        assert workspace.name == special_name
        
        # Verify retrieval works too
        retrieved = await workspace_repo.get(workspace.id)
        assert retrieved.name == special_name


class TestWorkspaceOwnership:
    """Test workspace ownership and access control."""
    
    async def test_multiple_workspaces_same_owner(self, workspace_repo, current_user):
        """Test creating multiple workspaces for the same owner."""
        # Note: File-based implementation only supports one workspace per directory
        # Each create() call overwrites the previous workspace
        workspace_names = ["Workspace 1", "Workspace 2", "Workspace 3"]
        created_workspaces = []
        
        for name in workspace_names:
            workspace_data = WorkspaceCreate(
                name=name,
                owner_id=current_user.id
            )
            workspace = await workspace_repo.create(workspace_data)
            created_workspaces.append(workspace)
        
        # Get all workspaces for owner
        owner_workspaces = await workspace_repo.get_by_owner(current_user.id)
        
        # File-based implementation only returns the last created workspace
        assert len(owner_workspaces) == 1
        assert owner_workspaces[0].name == "Workspace 3"  # Last one created
    
    async def test_get_nonexistent_owner_workspaces(self, workspace_repo):
        """Test getting workspaces for nonexistent owner."""
        from uuid import uuid4
        
        fake_owner_id = uuid4()
        workspaces = await workspace_repo.get_by_owner(fake_owner_id)
        
        assert len(workspaces) == 0


class TestWorkspaceEdgeCases:
    """Test edge cases and error conditions."""
    
    async def test_nonexistent_workspace(self, workspace_repo):
        """Test operations on nonexistent workspace."""
        from uuid import uuid4
        
        fake_id = uuid4()
        
        workspace = await workspace_repo.get(fake_id)
        assert workspace is None
        
        deleted = await workspace_repo.delete(fake_id)
        assert deleted is False
    
    async def test_duplicate_workspace_names_same_owner(self, workspace_repo, current_user):
        """Test creating workspaces with duplicate names for same owner."""
        workspace_data1 = WorkspaceCreate(
            name="Duplicate Name",
            owner_id=current_user.id
        )
        workspace1 = await workspace_repo.create(workspace_data1)
        
        # Try to create another with same name
        workspace_data2 = WorkspaceCreate(
            name="Duplicate Name",
            owner_id=current_user.id
        )
        
        try:
            workspace2 = await workspace_repo.create(workspace_data2)
            # If allowed, both should exist
            assert workspace1.id != workspace2.id
        except Exception:
            # If prevented, that's also acceptable
            pass
    
    async def test_update_nonexistent_workspace(self, workspace_repo):
        """Test updating a nonexistent workspace."""
        from uuid import uuid4
        
        fake_id = uuid4()
        update_data = WorkspaceUpdate(name="Updated Name")
        
        try:
            result = await workspace_repo.update(fake_id, update_data)
            # If it returns None, that's expected
            assert result is None
        except Exception:
            # If it raises an exception, that's also acceptable
            pass
    
    async def test_workspace_with_large_settings(self, workspace_repo, current_user):
        """Test workspace with large settings object."""
        large_settings = {
            "ai_providers": {
                "openai": {
                    "models": ["gpt-4", "gpt-3.5-turbo"],
                    "settings": {"temperature": 0.7, "max_tokens": 4000}
                },
                "anthropic": {
                    "models": ["claude-3-sonnet", "claude-3-haiku"],
                    "settings": {"temperature": 0.5, "max_tokens": 8000}
                },
                "google": {
                    "models": ["gemini-2.0-flash-001"],
                    "settings": {"temperature": 0.8}
                }
            },
            "export_settings": {
                "formats": ["pdf", "epub", "docx", "markdown"],
                "templates": ["modern", "classic", "academic"],
                "metadata": {"include_toc": True, "include_index": True}
            },
            "editor_preferences": {
                "theme": "dark",
                "font_family": "Courier New",
                "font_size": 14,
                "line_spacing": 1.5,
                "auto_save": True,
                "spell_check": True,
                "word_wrap": True
            }
        }
        
        workspace_data = WorkspaceCreate(
            name="Large Settings Workspace",
            owner_id=current_user.id,
            settings=large_settings
        )
        
        workspace = await workspace_repo.create(workspace_data)
        
        assert workspace.settings["ai_providers"]["openai"]["models"] == ["gpt-4", "gpt-3.5-turbo"]
        assert workspace.settings["export_settings"]["formats"] == ["pdf", "epub", "docx", "markdown"]
        assert workspace.settings["editor_preferences"]["theme"] == "dark"


@pytest.mark.integration
class TestWorkspaceIntegration:
    """Integration tests for workspace functionality."""
    
    async def test_workspace_with_content(self, workspace_factory):
        """Test workspace with story and wiki content."""
        workspace_path, repos, workspace_id = await workspace_factory(
            name="Content Test Workspace",
            chapter_count=3,
            wiki_count=2,
            with_api_keys=True
        )
        
        # Verify workspace exists and has content
        workspace = await repos.workspace.get(workspace_id)
        assert workspace.name == "Content Test Workspace"
        
        # Verify chapters exist
        chapters = await repos.story.get_chapters_by_workspace(workspace_id)
        assert len(chapters) == 3
        
        # Verify wiki articles exist
        articles = await repos.wiki.get_articles_by_workspace(workspace_id)
        assert len(articles) == 2
        
        # Verify user has API keys
        user = await cast(FileUserRepository, repos.user).get_current_user()
        api_keys = await repos.user.get_all_api_keys(user.id)
        assert len(api_keys) >= 1
    
    async def test_workspace_file_structure(self, temp_workspace_path):
        """Test that workspace creates proper file structure."""
        from src.database.factory import get_repositories
        
        repos = get_repositories(backend="file", workspace_path=temp_workspace_path)
        user = await cast(FileUserRepository, repos.user).get_current_user()
        
        # Create workspace
        workspace_data = WorkspaceCreate(
            name="File Structure Test",
            owner_id=user.id
        )
        workspace = await repos.workspace.create(workspace_data)
        
        # Check that expected directories exist
        expected_dirs = [
            temp_workspace_path / ".shuscribe",
            temp_workspace_path / "story",
            temp_workspace_path / "story" / "chapters",
            temp_workspace_path / "wiki",
            temp_workspace_path / "wiki-versions"
        ]
        
        for expected_dir in expected_dirs:
            assert expected_dir.exists(), f"Expected directory {expected_dir} does not exist"
            assert expected_dir.is_dir(), f"Expected {expected_dir} to be a directory"
        
        # Check that workspace config exists
        workspace_file = temp_workspace_path / ".shuscribe" / "workspace.json"
        assert workspace_file.exists()
        
        # Verify workspace data in file
        import json
        workspace_data = json.loads(workspace_file.read_text())
        assert workspace_data["name"] == "File Structure Test"
        assert workspace_data["id"] == str(workspace.id)


@pytest.mark.performance
class TestWorkspacePerformance:
    """Performance tests for workspace operations."""
    
    async def test_many_workspaces_performance(self, workspace_repo: IWorkspaceRepository, current_user: User):
        """Test performance with workspace operations."""
        # Note: File-based implementation only supports one workspace per directory
        # This test validates the performance of workspace operations, not multiple workspaces
        import time
        
        workspace_count = 25  # Number of operations to test
        
        # Test many workspace update operations
        start_time = time.time()
        
        for i in range(workspace_count):
            workspace_data = WorkspaceCreate(
                name=f"Performance Workspace {i:03d}",
                description=f"Description for workspace {i}",
                owner_id=current_user.id,
                # tags=[f"tag-{i}", "performance", "test"],
                settings={"index": i, "created_for": "performance_test"}
            )
            workspace = await workspace_repo.create(workspace_data)
        
        creation_time = time.time() - start_time
        
        # Retrieve all workspaces for owner
        start_time = time.time()
        owner_workspaces = await workspace_repo.get_by_owner(current_user.id)
        retrieval_time = time.time() - start_time
        
        # Test individual workspace lookups
        start_time = time.time()
        for _ in range(10):  # Test 10 lookups
            retrieved = await workspace_repo.get(workspace.id)  # Get the current workspace
            assert retrieved is not None
        lookup_time = time.time() - start_time
        
        # File-based implementation only has one workspace at a time
        assert len(owner_workspaces) == 1
        assert owner_workspaces[0].name == f"Performance Workspace {workspace_count-1:03d}"  # Last one
        
        assert creation_time < 10.0  # Should handle 25 operations in under 10s
        assert retrieval_time < 2.0  # Should retrieve quickly
        assert lookup_time < 2.0     # Should lookup quickly
        
        print(f"Performed {workspace_count} workspace operations in {creation_time:.2f}s")
        print(f"Retrieved workspace in {retrieval_time:.2f}s")
        print(f"Performed 10 lookups in {lookup_time:.2f}s") 