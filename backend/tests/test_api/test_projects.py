"""
Tests for Project API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from typing import Dict, Any

from src.main import app
from src.database.factory import init_repositories, reset_repositories, get_repositories


class TestProjectAPIEndpoints:
    """Test project API endpoints"""
    
    @pytest.fixture(autouse=True)
    async def setup_repositories(self):
        """Set up memory repositories for each test"""
        reset_repositories()
        init_repositories(backend="memory")
        yield
        reset_repositories()
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    async def test_project_data(self):
        """Create a test project with file tree"""
        repos = get_repositories()
        
        # Create project
        project_data = {
            "id": "test-project-api",
            "title": "API Test Project",
            "description": "A project for testing API endpoints",
            "word_count": 1500,
            "document_count": 3,
            "tags": ["api", "test", "novel"],
            "collaborators": [
                {
                    "user_id": "user_123",
                    "role": "owner",
                    "name": "Test Author",
                    "avatar": "https://example.com/avatar.jpg"
                },
                {
                    "user_id": "user_456",
                    "role": "editor",
                    "name": "Test Editor",
                    "avatar": None
                }
            ],
            "settings": {
                "auto_save_interval": 45000,
                "word_count_target": 75000,
                "backup_enabled": True,
                "export_formats": ["pdf", "epub"]
            }
        }
        project = await repos.project.create(project_data)
        
        # Create file tree structure
        # Root folders
        characters_folder = await repos.file_tree.create({
            "id": "folder-characters",
            "project_id": project.id,
            "name": "Characters",
            "type": "folder",
            "path": "/Characters",
            "parent_id": None,
            "icon": "folder",
            "tags": ["character", "organization"]
        })
        
        chapters_folder = await repos.file_tree.create({
            "id": "folder-chapters",
            "project_id": project.id,
            "name": "Chapters",
            "type": "folder",
            "path": "/Chapters",
            "parent_id": None,
            "icon": "folder",
            "tags": ["story", "content"]
        })
        
        # Subfolder
        protagonists_folder = await repos.file_tree.create({
            "id": "folder-protagonists",
            "project_id": project.id,
            "name": "Protagonists",
            "type": "folder",
            "path": "/Characters/Protagonists",
            "parent_id": characters_folder.id,
            "icon": "folder",
            "tags": ["character", "protagonist"]
        })
        
        # Files
        character_file = await repos.file_tree.create({
            "id": "file-hero",
            "project_id": project.id,
            "name": "hero.md",
            "type": "file",
            "path": "/Characters/Protagonists/hero.md",
            "parent_id": protagonists_folder.id,
            "document_id": "doc-hero",
            "icon": "user",
            "tags": ["character", "protagonist", "main"],
            "word_count": 500
        })
        
        chapter_file = await repos.file_tree.create({
            "id": "file-chapter1",
            "project_id": project.id,
            "name": "chapter_01.md",
            "type": "file",
            "path": "/Chapters/chapter_01.md",
            "parent_id": chapters_folder.id,
            "document_id": "doc-chapter1",
            "icon": "file-text",
            "tags": ["chapter", "story"],
            "word_count": 1000
        })
        
        notes_file = await repos.file_tree.create({
            "id": "file-notes",
            "project_id": project.id,
            "name": "notes.md",
            "type": "file",
            "path": "/notes.md",
            "parent_id": None,
            "document_id": "doc-notes",
            "icon": "sticky-note",
            "tags": ["notes", "planning"],
            "word_count": 250
        })
        
        return {
            "project": project,
            "file_tree_items": [
                characters_folder,
                chapters_folder,
                protagonists_folder,
                character_file,
                chapter_file,
                notes_file
            ]
        }
    
    async def test_get_project_success(self, client: TestClient, test_project_data):
        """Test successful project retrieval"""
        project = test_project_data["project"]
        
        response = client.get(f"/api/v1/projects/{project.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify project details
        assert data["id"] == project.id
        assert data["title"] == "API Test Project"
        assert data["description"] == "A project for testing API endpoints"
        assert data["word_count"] == 1500
        assert data["document_count"] == 3
        assert data["tags"] == ["api", "test", "novel"]
        
        # Verify timestamps are ISO format strings
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
        # Should be valid ISO format
        datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        
        # Verify collaborators
        assert len(data["collaborators"]) == 2
        
        owner = next(c for c in data["collaborators"] if c["role"] == "owner")
        assert owner["user_id"] == "user_123"
        assert owner["name"] == "Test Author"
        assert owner["avatar"] == "https://example.com/avatar.jpg"
        
        editor = next(c for c in data["collaborators"] if c["role"] == "editor")
        assert editor["user_id"] == "user_456"
        assert editor["name"] == "Test Editor"
        assert editor["avatar"] is None
        
        # Verify settings
        settings = data["settings"]
        assert settings["auto_save_interval"] == 45000
        assert settings["word_count_target"] == 75000
        assert settings["backup_enabled"] is True
    
    async def test_get_project_not_found(self, client: TestClient, test_project_data):
        """Test project not found error"""
        response = client.get("/api/v1/projects/nonexistent-project-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    async def test_get_project_with_minimal_data(self, client: TestClient):
        """Test project with minimal data"""
        repos = get_repositories()
        
        # Create minimal project
        minimal_project = await repos.project.create({
            "id": "minimal-project",
            "title": "Minimal Project"
        })
        
        response = client.get(f"/api/v1/projects/{minimal_project.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == "minimal-project"
        assert data["title"] == "Minimal Project"
        assert data["description"] == ""
        assert data["word_count"] == 0
        assert data["document_count"] == 0
        assert data["tags"] == []
        assert data["collaborators"] == []
        
        # Verify default settings
        settings = data["settings"]
        assert settings["auto_save_interval"] == 30000  # Default
        assert settings["word_count_target"] == 0       # Default
        assert settings["backup_enabled"] is True       # Default
    
    async def test_get_file_tree_success(self, client: TestClient, test_project_data):
        """Test successful file tree retrieval"""
        project = test_project_data["project"]
        
        response = client.get(f"/api/v1/projects/{project.id}/file-tree")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "file_tree" in data
        assert "metadata" in data
        
        # Verify metadata
        metadata = data["metadata"]
        assert metadata["total_files"] == 3
        assert metadata["total_folders"] == 3
        assert isinstance(metadata["last_updated"], str)
        
        # Verify hierarchical structure
        file_tree = data["file_tree"]
        assert len(file_tree) == 3  # 2 root folders + 1 root file
        
        # Find root items
        characters_folder = next(item for item in file_tree if item["name"] == "Characters")
        chapters_folder = next(item for item in file_tree if item["name"] == "Chapters")
        notes_file = next(item for item in file_tree if item["name"] == "notes.md")
        
        # Verify Characters folder structure
        assert characters_folder["type"] == "folder"
        assert characters_folder["path"] == "/Characters"
        assert characters_folder["parent_id"] is None
        assert characters_folder["children"] is not None
        assert len(characters_folder["children"]) == 1
        
        # Verify nested structure
        protagonists_folder = characters_folder["children"][0]
        assert protagonists_folder["name"] == "Protagonists"
        assert protagonists_folder["type"] == "folder"
        assert protagonists_folder["parent_id"] == characters_folder["id"]
        assert protagonists_folder["children"] is not None
        assert len(protagonists_folder["children"]) == 1
        
        # Verify file in nested folder
        hero_file = protagonists_folder["children"][0]
        assert hero_file["name"] == "hero.md"
        assert hero_file["type"] == "file"
        assert hero_file["document_id"] == "doc-hero"
        assert hero_file["word_count"] == 500
        assert hero_file["tags"] == ["character", "protagonist", "main"]
        assert hero_file["children"] is None  # Files don't have children
        
        # Verify Chapters folder
        assert chapters_folder["type"] == "folder"
        assert chapters_folder["children"] is not None
        assert len(chapters_folder["children"]) == 1
        
        chapter_file = chapters_folder["children"][0]
        assert chapter_file["name"] == "chapter_01.md"
        assert chapter_file["document_id"] == "doc-chapter1"
        assert chapter_file["word_count"] == 1000
        
        # Verify root file
        assert notes_file["type"] == "file"
        assert notes_file["parent_id"] is None
        assert notes_file["document_id"] == "doc-notes"
        assert notes_file["word_count"] == 250
        assert notes_file["children"] is None
    
    async def test_get_file_tree_empty_project(self, client: TestClient):
        """Test file tree for project with no files"""
        repos = get_repositories()
        
        # Create empty project
        empty_project = await repos.project.create({
            "id": "empty-project",
            "title": "Empty Project"
        })
        
        response = client.get(f"/api/v1/projects/{empty_project.id}/file-tree")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify empty file tree
        assert data["file_tree"] == []
        
        # Verify metadata
        metadata = data["metadata"]
        assert metadata["total_files"] == 0
        assert metadata["total_folders"] == 0
        assert isinstance(metadata["last_updated"], str)
    
    async def test_get_file_tree_project_not_found(self, client: TestClient, test_project_data):
        """Test file tree for nonexistent project"""
        response = client.get("/api/v1/projects/nonexistent-project/file-tree")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    async def test_file_tree_timestamp_format(self, client: TestClient, test_project_data):
        """Test that all timestamps in file tree are properly formatted"""
        project = test_project_data["project"]
        
        response = client.get(f"/api/v1/projects/{project.id}/file-tree")
        
        assert response.status_code == 200
        data = response.json()
        
        def verify_timestamps_recursive(items):
            """Recursively verify all timestamp formats"""
            for item in items:
                # Verify timestamp format
                assert isinstance(item["created_at"], str)
                assert isinstance(item["updated_at"], str)
                
                # Should be valid ISO format
                datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
                datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
                
                # Check children recursively
                if item.get("children"):
                    verify_timestamps_recursive(item["children"])
        
        verify_timestamps_recursive(data["file_tree"])
    
    async def test_file_tree_data_consistency(self, client: TestClient, test_project_data):
        """Test data consistency in file tree response"""
        project = test_project_data["project"]
        
        response = client.get(f"/api/v1/projects/{project.id}/file-tree")
        
        assert response.status_code == 200
        data = response.json()
        
        def collect_all_items(items, collected=None):
            """Recursively collect all items from hierarchical structure"""
            if collected is None:
                collected = []
            
            for item in items:
                collected.append(item)
                if item.get("children"):
                    collect_all_items(item["children"], collected)
            
            return collected
        
        all_items = collect_all_items(data["file_tree"])
        
        # Count files and folders
        files = [item for item in all_items if item["type"] == "file"]
        folders = [item for item in all_items if item["type"] == "folder"]
        
        # Verify metadata matches actual counts
        assert len(files) == data["metadata"]["total_files"]
        assert len(folders) == data["metadata"]["total_folders"]
        
        # Verify file properties
        for file_item in files:
            assert file_item["document_id"] is not None
            assert file_item["word_count"] is not None
            assert file_item["children"] is None
        
        # Verify folder properties
        for folder_item in folders:
            assert folder_item["document_id"] is None
            assert folder_item["word_count"] is None
            # Children can be None or a list, but should exist in structure


class TestProjectAPIErrorHandling:
    """Test error handling in project API endpoints"""
    
    @pytest.fixture(autouse=True)
    async def setup_repositories(self):
        """Set up memory repositories for each test"""
        reset_repositories()
        init_repositories(backend="memory")
        yield
        reset_repositories()
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    async def test_get_project_invalid_id_format(self, client: TestClient):
        """Test project retrieval with various invalid ID formats"""
        invalid_ids = [
            "",  # Empty string
            " ",  # Whitespace
            "project with spaces",  # Spaces
            "project/with/slashes",  # Slashes
            "very-long-" + "x" * 1000 + "-id",  # Very long ID
        ]
        
        for invalid_id in invalid_ids:
            response = client.get(f"/api/v1/projects/{invalid_id}")
            # Should either be 404 (not found) or other error, but not 200
            assert response.status_code != 200
    
    async def test_get_file_tree_invalid_id_format(self, client: TestClient):
        """Test file tree retrieval with invalid project ID formats"""
        invalid_ids = [
            "",  # Empty string
            " ",  # Whitespace
            "project with spaces",  # Spaces
        ]
        
        for invalid_id in invalid_ids:
            response = client.get(f"/api/v1/projects/{invalid_id}/file-tree")
            # Should either be 404 (not found) or other error, but not 200
            assert response.status_code != 200


class TestProjectAPIResponseModels:
    """Test response model validation and structure"""
    
    @pytest.fixture(autouse=True)
    async def setup_repositories(self):
        """Set up memory repositories for each test"""
        reset_repositories()
        init_repositories(backend="memory")
        yield
        reset_repositories()
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    async def test_project_response_model_structure(self, client: TestClient):
        """Test that project response matches expected model structure"""
        repos = get_repositories()
        
        # Create project with complex data
        project = await repos.project.create({
            "id": "model-test",
            "title": "Response Model Test",
            "description": "Testing response model structure",
            "word_count": 2000,
            "document_count": 5,
            "tags": ["test", "model", "validation"],
            "collaborators": [
                {
                    "user_id": "user1",
                    "role": "owner",
                    "name": "Owner User",
                    "avatar": "https://example.com/avatar.jpg"
                }
            ],
            "settings": {
                "auto_save_interval": 15000,
                "word_count_target": 50000,
                "backup_enabled": False
            }
        })
        
        response = client.get(f"/api/v1/projects/{project.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        required_fields = [
            "id", "title", "description", "word_count", "document_count",
            "created_at", "updated_at", "tags", "collaborators", "settings"
        ]
        
        for field in required_fields:
            assert field in data, f"Required field '{field}' missing from response"
        
        # Verify field types
        assert isinstance(data["id"], str)
        assert isinstance(data["title"], str)
        assert isinstance(data["description"], str)
        assert isinstance(data["word_count"], int)
        assert isinstance(data["document_count"], int)
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
        assert isinstance(data["tags"], list)
        assert isinstance(data["collaborators"], list)
        assert isinstance(data["settings"], dict)
        
        # Verify collaborator structure
        collaborator = data["collaborators"][0]
        assert "user_id" in collaborator
        assert "role" in collaborator
        assert "name" in collaborator
        assert "avatar" in collaborator
        
        # Verify settings structure
        settings = data["settings"]
        assert "auto_save_interval" in settings
        assert "word_count_target" in settings
        assert "backup_enabled" in settings
        assert isinstance(settings["auto_save_interval"], int)
        assert isinstance(settings["word_count_target"], int)
        assert isinstance(settings["backup_enabled"], bool)
    
    async def test_file_tree_response_model_structure(self, client: TestClient):
        """Test that file tree response matches expected model structure"""
        repos = get_repositories()
        
        # Create project and basic file tree
        project = await repos.project.create({
            "id": "tree-model-test",
            "title": "File Tree Model Test"
        })
        
        folder = await repos.file_tree.create({
            "id": "test-folder",
            "project_id": project.id,
            "name": "Test Folder",
            "type": "folder",
            "path": "/Test Folder",
            "parent_id": None,
            "icon": "folder",
            "tags": ["test"]
        })
        
        file_item = await repos.file_tree.create({
            "id": "test-file",
            "project_id": project.id,
            "name": "test.md",
            "type": "file",
            "path": "/Test Folder/test.md",
            "parent_id": folder.id,
            "document_id": "doc-123",
            "icon": "file-text",
            "tags": ["test", "file"],
            "word_count": 100
        })
        
        response = client.get(f"/api/v1/projects/{project.id}/file-tree")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify top-level structure
        assert "file_tree" in data
        assert "metadata" in data
        assert isinstance(data["file_tree"], list)
        assert isinstance(data["metadata"], dict)
        
        # Verify metadata structure
        metadata = data["metadata"]
        required_metadata_fields = ["total_files", "total_folders", "last_updated"]
        for field in required_metadata_fields:
            assert field in metadata
        
        assert isinstance(metadata["total_files"], int)
        assert isinstance(metadata["total_folders"], int)
        assert isinstance(metadata["last_updated"], str)
        
        # Verify file tree item structure
        folder_item = data["file_tree"][0]
        required_item_fields = [
            "id", "name", "type", "path", "parent_id", "children",
            "document_id", "icon", "tags", "word_count",
            "created_at", "updated_at"
        ]
        
        for field in required_item_fields:
            assert field in folder_item
        
        # Verify children structure
        assert isinstance(folder_item["children"], list)
        assert len(folder_item["children"]) == 1
        
        file_item_response = folder_item["children"][0]
        for field in required_item_fields:
            assert field in file_item_response
        
        # Files should have null children
        assert file_item_response["children"] is None