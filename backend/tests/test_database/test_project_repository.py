"""
Tests for ProjectRepository implementations
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.database.factory import create_repositories
from src.database.interfaces import ProjectRepository


class TestProjectRepositoryInterface:
    """Test the ProjectRepository interface contract"""
    
    @pytest.fixture(params=["memory", "database"])
    async def project_repo(self, request) -> ProjectRepository:
        """Provide both memory and database repository implementations"""
        if request.param == "database":
            # Initialize database for database backend tests
            from src.database.connection import init_database, create_tables, close_database
            
            # Initialize database connection
            init_database()
            
            # Create tables
            await create_tables()
            
            repos = create_repositories(backend=request.param)
            
            yield repos.project
            
            # Cleanup
            await close_database()
        else:
            repos = create_repositories(backend=request.param)
            yield repos.project
    
    async def test_create_project(self, project_repo: ProjectRepository):
        """Test creating a new project"""
        project_data = {
            "id": "test-create-123",
            "title": "Test Create Project",
            "description": "A project for testing creation",
            "word_count": 100,
            "document_count": 2,
            "tags": ["test", "create"],
            "collaborators": [
                {
                    "user_id": "user_1",
                    "role": "owner",
                    "name": "Test Owner"
                }
            ],
            "settings": {
                "auto_save_interval": 30000,
                "word_count_target": 50000,
                "backup_enabled": True
            }
        }
        
        project = await project_repo.create(project_data)
        
        assert project is not None
        assert project.id == "test-create-123"
        assert project.title == "Test Create Project"
        assert project.description == "A project for testing creation"
        assert project.word_count == 100
        assert project.document_count == 2
        assert project.tags == ["test", "create"]
        assert len(project.collaborators) == 1
        assert project.collaborators[0]["role"] == "owner"
        assert project.settings["auto_save_interval"] == 30000
        assert isinstance(project.created_at, datetime)
        assert isinstance(project.updated_at, datetime)
    
    async def test_get_project_by_id(self, project_repo: ProjectRepository):
        """Test retrieving a project by ID"""
        # Create project first
        project_data = {
            "id": "test-get-456",
            "title": "Test Get Project",
            "description": "A project for testing retrieval"
        }
        created_project = await project_repo.create(project_data)
        
        # Retrieve the project
        retrieved_project = await project_repo.get_by_id("test-get-456")
        
        assert retrieved_project is not None
        assert retrieved_project.id == created_project.id
        assert retrieved_project.title == created_project.title
        assert retrieved_project.description == created_project.description
        assert retrieved_project.created_at == created_project.created_at
    
    async def test_get_nonexistent_project(self, project_repo: ProjectRepository):
        """Test retrieving a project that doesn't exist"""
        result = await project_repo.get_by_id("nonexistent-id")
        assert result is None
    
    async def test_update_project(self, project_repo: ProjectRepository):
        """Test updating an existing project"""
        # Create project first
        project_data = {
            "id": "test-update-789",
            "title": "Original Title",
            "description": "Original description",
            "word_count": 100,
            "tags": ["original"]
        }
        created_project = await project_repo.create(project_data)
        original_created_at = created_project.created_at
        
        # Update the project
        updates = {
            "title": "Updated Title",
            "description": "Updated description",
            "word_count": 200,
            "tags": ["updated", "modified"]
        }
        updated_project = await project_repo.update("test-update-789", updates)
        
        assert updated_project is not None
        assert updated_project.id == "test-update-789"
        assert updated_project.title == "Updated Title"
        assert updated_project.description == "Updated description"
        assert updated_project.word_count == 200
        assert updated_project.tags == ["updated", "modified"]
        assert updated_project.created_at == original_created_at  # Should not change
        assert updated_project.updated_at > original_created_at   # Should be updated
    
    async def test_update_nonexistent_project(self, project_repo: ProjectRepository):
        """Test updating a project that doesn't exist"""
        updates = {"title": "New Title"}
        result = await project_repo.update("nonexistent-id", updates)
        assert result is None
    
    async def test_delete_project(self, project_repo: ProjectRepository):
        """Test deleting an existing project"""
        # Create project first
        project_data = {
            "id": "test-delete-101",
            "title": "To Be Deleted",
            "description": "This project will be deleted"
        }
        await project_repo.create(project_data)
        
        # Verify it exists
        project = await project_repo.get_by_id("test-delete-101")
        assert project is not None
        
        # Delete the project
        delete_result = await project_repo.delete("test-delete-101")
        assert delete_result is True
        
        # Verify it's gone
        deleted_project = await project_repo.get_by_id("test-delete-101")
        assert deleted_project is None
    
    async def test_delete_nonexistent_project(self, project_repo: ProjectRepository):
        """Test deleting a project that doesn't exist"""
        result = await project_repo.delete("nonexistent-id")
        assert result is False


class TestProjectRepositoryEdgeCases:
    """Test edge cases and data validation"""
    
    @pytest.fixture
    def memory_project_repo(self) -> ProjectRepository:
        """Memory repository for edge case testing"""
        repos = create_repositories(backend="memory")
        return repos.project
    
    async def test_create_project_with_minimal_data(self, memory_project_repo: ProjectRepository):
        """Test creating a project with only required fields"""
        project_data = {
            "title": "Minimal Project"
        }
        
        project = await memory_project_repo.create(project_data)
        
        assert project is not None
        assert project.title == "Minimal Project"
        assert project.description == ""  # Default empty
        assert project.word_count == 0   # Default zero
        assert project.document_count == 0  # Default zero
        assert project.tags == []        # Default empty
        assert project.collaborators == []  # Default empty
        assert project.settings == {}    # Default empty
    
    async def test_create_project_with_auto_generated_id(self, memory_project_repo: ProjectRepository):
        """Test creating a project without providing an ID"""
        project_data = {
            "title": "Auto ID Project",
            "description": "Project with auto-generated ID"
        }
        
        project = await memory_project_repo.create(project_data)
        
        assert project is not None
        assert project.id is not None
        assert len(project.id) > 0
        assert project.title == "Auto ID Project"
    
    async def test_create_project_with_complex_collaborators(self, memory_project_repo: ProjectRepository):
        """Test creating a project with complex collaborator data"""
        project_data = {
            "title": "Collaborative Project",
            "collaborators": [
                {
                    "user_id": "owner_123",
                    "role": "owner",
                    "name": "Project Owner",
                    "avatar": "https://example.com/avatar1.jpg"
                },
                {
                    "user_id": "editor_456",
                    "role": "editor",
                    "name": "Content Editor",
                    "avatar": None
                },
                {
                    "user_id": "viewer_789",
                    "role": "viewer",
                    "name": "Guest Viewer"
                }
            ]
        }
        
        project = await memory_project_repo.create(project_data)
        
        assert project is not None
        assert len(project.collaborators) == 3
        
        # Verify owner
        owner = next(c for c in project.collaborators if c["role"] == "owner")
        assert owner["user_id"] == "owner_123"
        assert owner["name"] == "Project Owner"
        assert owner["avatar"] == "https://example.com/avatar1.jpg"
        
        # Verify editor
        editor = next(c for c in project.collaborators if c["role"] == "editor")
        assert editor["user_id"] == "editor_456"
        assert editor["avatar"] is None
        
        # Verify viewer
        viewer = next(c for c in project.collaborators if c["role"] == "viewer")
        assert viewer["user_id"] == "viewer_789"
    
    async def test_create_project_with_complex_settings(self, memory_project_repo: ProjectRepository):
        """Test creating a project with complex settings"""
        project_data = {
            "title": "Settings Test Project",
            "settings": {
                "auto_save_interval": 15000,
                "word_count_target": 80000,
                "backup_enabled": True,
                "backup_frequency": "daily",
                "export_formats": ["pdf", "epub", "docx"],
                "writing_goals": {
                    "daily_words": 500,
                    "weekly_words": 3500
                },
                "editor_preferences": {
                    "spell_check": True,
                    "grammar_check": False,
                    "auto_complete": True
                }
            }
        }
        
        project = await memory_project_repo.create(project_data)
        
        assert project is not None
        assert project.settings["auto_save_interval"] == 15000
        assert project.settings["word_count_target"] == 80000
        assert project.settings["backup_enabled"] is True
        assert project.settings["export_formats"] == ["pdf", "epub", "docx"]
        assert project.settings["writing_goals"]["daily_words"] == 500
        assert project.settings["editor_preferences"]["spell_check"] is True
    
    async def test_update_partial_fields(self, memory_project_repo: ProjectRepository):
        """Test updating only some fields of a project"""
        # Create project
        project_data = {
            "id": "partial-update-test",
            "title": "Original Title",
            "description": "Original description",
            "word_count": 100,
            "tags": ["original", "test"]
        }
        created_project = await memory_project_repo.create(project_data)
        
        # Update only title and word_count
        updates = {
            "title": "New Title",
            "word_count": 250
        }
        updated_project = await memory_project_repo.update("partial-update-test", updates)
        
        assert updated_project is not None
        assert updated_project.title == "New Title"
        assert updated_project.word_count == 250
        # These should remain unchanged
        assert updated_project.description == "Original description"
        assert updated_project.tags == ["original", "test"]
    
    async def test_multiple_projects_independence(self, memory_project_repo: ProjectRepository):
        """Test that multiple projects don't interfere with each other"""
        # Create multiple projects
        projects_data = [
            {
                "id": "project-a",
                "title": "Project A",
                "word_count": 100,
                "tags": ["a", "first"]
            },
            {
                "id": "project-b", 
                "title": "Project B",
                "word_count": 200,
                "tags": ["b", "second"]
            },
            {
                "id": "project-c",
                "title": "Project C", 
                "word_count": 300,
                "tags": ["c", "third"]
            }
        ]
        
        created_projects = []
        for data in projects_data:
            project = await memory_project_repo.create(data)
            created_projects.append(project)
        
        # Verify all projects exist and have correct data
        for i, project in enumerate(created_projects):
            assert project.id == projects_data[i]["id"]
            assert project.title == projects_data[i]["title"]
            assert project.word_count == projects_data[i]["word_count"]
            assert project.tags == projects_data[i]["tags"]
        
        # Update one project and verify others are unaffected
        await memory_project_repo.update("project-b", {"title": "Modified Project B"})
        
        project_a = await memory_project_repo.get_by_id("project-a")
        project_b = await memory_project_repo.get_by_id("project-b")
        project_c = await memory_project_repo.get_by_id("project-c")
        
        assert project_a.title == "Project A"  # Unchanged
        assert project_b.title == "Modified Project B"  # Changed
        assert project_c.title == "Project C"  # Unchanged
        
        # Delete one project and verify others still exist
        await memory_project_repo.delete("project-a")
        
        assert await memory_project_repo.get_by_id("project-a") is None
        assert await memory_project_repo.get_by_id("project-b") is not None
        assert await memory_project_repo.get_by_id("project-c") is not None