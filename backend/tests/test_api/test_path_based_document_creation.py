"""
Tests for path-based document creation with auto-folder creation
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app 
from src.database.factory import init_repositories, reset_repositories, get_repositories
from src.database.interfaces.models import Project


class TestPathBasedDocumentCreation:
    """Test the new path-based document creation system"""
    
    @pytest.fixture(autouse=True)
    async def setup_repositories(self):
        """Set up memory repositories for each test"""
        reset_repositories()
        init_repositories(backend="memory")
        yield
        reset_repositories()
    
    @pytest.fixture
    def client(self):
        """FastAPI test client with auth disabled for testing"""
        from src.api.dependencies import get_current_user_id
        
        # Override auth dependency to return a test user ID
        def override_get_current_user_id():
            return "test-user-123"
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        
        client = TestClient(app)
        
        yield client
        
        # Clean up dependency override
        app.dependency_overrides.clear()
    
    @pytest.fixture
    async def test_project(self):
        """Create a test project for document tests"""
        repos = get_repositories()
        
        project_data = {
            "id": "path-test-project",
            "title": "Path-Based Document Test Project",
            "description": "A project for testing path-based document creation",
            "word_count": 0,
            "document_count": 0,
            "tags": ["test", "path-based"]
        }
        
        return await repos.project.create(project_data)
    
    async def test_document_creation_with_auto_folder_creation(self, client: TestClient, test_project):
        """Test that documents auto-create folder hierarchy from path"""
        create_request = {
            "project_id": test_project.id,
            "title": "Character Profile: Aria Stormwind",
            "path": "/characters/protagonists/aria-stormwind",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Aria Stormwind"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "A dragon rider from the mountain village of Windmere."}]
                    }
                ]
            },
            "tags": ["character", "protagonist"]
        }
        
        # Create document - should auto-create folders
        response = client.post("/api/v1/documents", json=create_request)
        assert response.status_code == 200
        
        doc_data = response.json()
        assert doc_data["title"] == "Character Profile: Aria Stormwind"
        assert doc_data["path"] == "/characters/protagonists/aria-stormwind"
        assert doc_data["file_tree_id"] is not None  # Should be assigned to deepest folder
        
        # Verify file tree structure was created
        file_tree_response = client.get(f"/api/v1/projects/{test_project.id}/file-tree")
        assert file_tree_response.status_code == 200
        
        file_tree_data = file_tree_response.json()
        
        # Extract file tree items from response
        if isinstance(file_tree_data, dict) and "file_tree" in file_tree_data:
            file_tree_items = file_tree_data["file_tree"]
        else:
            file_tree_items = file_tree_data
        
        # Extract folder paths from file tree (including nested folders)
        def extract_folder_paths(items):
            paths = []
            for item in items:
                if item["type"] == "folder":
                    paths.append(item["path"])
                    # Recursively check children if they exist
                    if item.get("children"):
                        paths.extend(extract_folder_paths(item["children"]))
            return paths
        
        folder_paths = extract_folder_paths(file_tree_items)
        
        # Verify all necessary folders were created
        assert "/characters" in folder_paths
        assert "/characters/protagonists" in folder_paths
    
    async def test_document_creation_root_level(self, client: TestClient, test_project): 
        """Test document creation at root level (no folders needed)"""
        create_request = {
            "project_id": test_project.id,
            "title": "Project Overview",
            "path": "/overview",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph", 
                        "content": [{"type": "text", "text": "This is a root level document."}]
                    }
                ]
            }
        }
        
        response = client.post("/api/v1/documents", json=create_request)
        assert response.status_code == 200
        
        doc_data = response.json()
        assert doc_data["file_tree_id"] is None  # No parent folder
        assert doc_data["path"] == "/overview"
    
    async def test_document_creation_with_existing_folders(self, client: TestClient, test_project):
        """Test document creation when some folders already exist"""
        # First, create a document that will create some folders
        first_doc_request = {
            "project_id": test_project.id,
            "title": "First Character",
            "path": "/characters/protagonists/first-char",
            "content": {"type": "doc", "content": []}
        }
        
        response1 = client.post("/api/v1/documents", json=first_doc_request)
        assert response1.status_code == 200
        
        # Now create another document in the same structure
        second_doc_request = {
            "project_id": test_project.id,
            "title": "Second Character", 
            "path": "/characters/protagonists/second-char",
            "content": {"type": "doc", "content": []}
        }
        
        response2 = client.post("/api/v1/documents", json=second_doc_request)
        assert response2.status_code == 200
        
        doc_data = response2.json()
        assert doc_data["title"] == "Second Character"
        assert doc_data["path"] == "/characters/protagonists/second-char"
        assert doc_data["file_tree_id"] is not None  # Should reuse existing folder
    
    async def test_document_creation_invalid_path(self, client: TestClient, test_project):
        """Test document creation with invalid path"""
        create_request = {
            "project_id": test_project.id,
            "title": "Invalid Path Document",
            "path": "/characters/../invalid",  # Contains ..
            "content": {"type": "doc", "content": []}
        }
        
        response = client.post("/api/v1/documents", json=create_request)
        assert response.status_code == 400  # Bad request due to invalid path
    
    async def test_document_creation_deeply_nested_path(self, client: TestClient, test_project):
        """Test document creation with deeply nested folder structure"""
        create_request = {
            "project_id": test_project.id,
            "title": "Deeply Nested Document",
            "path": "/world/regions/kingdoms/stormlands/cities/windmere/locations/tavern",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "The local tavern in Windmere."}]
                    }
                ]
            }
        }
        
        response = client.post("/api/v1/documents", json=create_request)
        assert response.status_code == 200
        
        doc_data = response.json()
        assert doc_data["path"] == "/world/regions/kingdoms/stormlands/cities/windmere/locations/tavern"
        assert doc_data["file_tree_id"] is not None
        
        # Verify all folders in the hierarchy were created
        file_tree_response = client.get(f"/api/v1/projects/{test_project.id}/file-tree")
        assert file_tree_response.status_code == 200
        
        file_tree_data = file_tree_response.json()
        
        # Extract file tree items from response  
        if isinstance(file_tree_data, dict) and "file_tree" in file_tree_data:
            file_tree_items = file_tree_data["file_tree"]
        else:
            file_tree_items = file_tree_data
        
        # Extract folder paths from file tree (including nested folders)
        def extract_folder_paths(items):
            paths = []
            for item in items:
                if item["type"] == "folder":
                    paths.append(item["path"])
                    # Recursively check children if they exist
                    if item.get("children"):
                        paths.extend(extract_folder_paths(item["children"]))
            return paths
        
        folder_paths = extract_folder_paths(file_tree_items)
        
        expected_folders = [
            "/world",
            "/world/regions", 
            "/world/regions/kingdoms",
            "/world/regions/kingdoms/stormlands",
            "/world/regions/kingdoms/stormlands/cities",
            "/world/regions/kingdoms/stormlands/cities/windmere",
            "/world/regions/kingdoms/stormlands/cities/windmere/locations"
        ]
        
        for expected_folder in expected_folders:
            assert expected_folder in folder_paths, f"Missing folder: {expected_folder}"
    
    async def test_path_validation(self, client: TestClient, test_project):
        """Test various path validation scenarios"""
        invalid_paths = [
            "",  # Empty path
            "/characters/../invalid",  # Contains ..
            "/" + "a" * 101,  # Segment too long
        ]
        
        for invalid_path in invalid_paths:
            create_request = {
                "project_id": test_project.id,
                "title": "Test Document",
                "path": invalid_path,
                "content": {"type": "doc", "content": []}
            }
            
            response = client.post("/api/v1/documents", json=create_request)
            # Accept either 400 (bad request) or 422 (validation error)
            assert response.status_code in [400, 422], f"Path '{invalid_path}' should be invalid, got {response.status_code}"