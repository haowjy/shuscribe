"""
Tests for Document API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from typing import Dict, Any

from src.main import app
from src.database.factory import init_repositories, reset_repositories, get_repositories


class TestDocumentAPIEndpoints:
    """Test document API endpoints"""
    
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
    async def test_project(self):
        """Create a test project for document tests"""
        repos = get_repositories()
        
        project_data = {
            "id": "doc-test-project",
            "title": "Document Test Project",
            "description": "A project for testing document API endpoints",
            "word_count": 0,
            "document_count": 0,
            "tags": ["test", "api"]
        }
        
        return await repos.project.create(project_data)
    
    @pytest.fixture
    async def test_document(self, test_project):
        """Create a test document"""
        repos = get_repositories()
        
        document_data = {
            "id": "test-document-123",
            "project_id": test_project.id,
            "title": "Test Document",
            "path": "/test_document.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This is a test document with some content for testing purposes."
                            }
                        ]
                    }
                ]
            },
            "tags": ["test", "sample"],
            "word_count": 12,
            "version": "1.0.0",
            "is_locked": False
        }
        
        return await repos.document.create(document_data)
    
    async def test_get_document_success(self, client: TestClient, test_document):
        """Test successful document retrieval"""
        response = client.get(f"/api/v1/documents/{test_document.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify document details
        assert data["id"] == test_document.id
        assert data["title"] == "Test Document"
        assert data["path"] == "/test_document.md"
        assert data["project_id"] == test_document.project_id
        assert data["tags"] == ["test", "sample"]
        assert data["word_count"] == 12
        assert data["version"] == "1.0.0"
        assert data["is_locked"] is False
        assert data["locked_by"] is None
        
        # Verify content structure
        content = data["content"]
        assert content["type"] == "doc"
        assert isinstance(content["content"], list)
        assert len(content["content"]) == 1
        
        paragraph = content["content"][0]
        assert paragraph["type"] == "paragraph"
        assert paragraph["content"][0]["text"] == "This is a test document with some content for testing purposes."
        
        # Verify timestamps
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
        datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
    
    async def test_get_document_not_found(self, client: TestClient):
        """Test document not found error"""
        response = client.get("/api/v1/documents/nonexistent-document-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    async def test_create_document_success(self, client: TestClient, test_project):
        """Test successful document creation"""
        create_request = {
            "project_id": test_project.id,
            "title": "New Test Document",
            "path": "/new_document.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [
                            {
                                "type": "text",
                                "text": "Chapter One"
                            }
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This is the beginning of our story. It was a dark and stormy night."
                            }
                        ]
                    }
                ]
            },
            "tags": ["chapter", "beginning"],
            "file_tree_parent_id": "parent-folder-id"
        }
        
        response = client.post("/api/v1/documents", json=create_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify created document
        assert data["title"] == "New Test Document"
        assert data["path"] == "/new_document.md"
        assert data["project_id"] == test_project.id
        assert data["tags"] == ["chapter", "beginning"]
        assert data["version"] == "1.0.0"
        assert data["is_locked"] is False
        assert data["file_tree_id"] == "parent-folder-id"
        
        # Verify word count calculation
        assert data["word_count"] == 16  # "Chapter One" (2) + "This is..." (14)
        
        # Verify content structure
        content = data["content"]
        assert content["type"] == "doc"
        assert len(content["content"]) == 2
        assert content["content"][0]["type"] == "heading"
        assert content["content"][1]["type"] == "paragraph"
        
        # Verify project counts were updated
        repos = get_repositories()
        updated_project = await repos.project.get_by_id(test_project.id)
        assert updated_project is not None
        assert updated_project.document_count == 1
        assert updated_project.word_count == 16
    
    async def test_create_document_minimal(self, client: TestClient, test_project):
        """Test creating document with minimal data"""
        create_request = {
            "project_id": test_project.id,
            "title": "Minimal Document",
            "path": "/minimal.md"
        }
        
        response = client.post("/api/v1/documents", json=create_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == "Minimal Document"
        assert data["tags"] == []
        assert data["word_count"] == 0  # Empty content
        assert data["content"]["type"] == "doc"
        assert data["content"]["content"] == []
        assert data["file_tree_id"] is None
    
    async def test_create_document_project_not_found(self, client: TestClient):
        """Test creating document for nonexistent project"""
        create_request = {
            "project_id": "nonexistent-project",
            "title": "Document for Missing Project",
            "path": "/missing.md"
        }
        
        response = client.post("/api/v1/documents", json=create_request)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    async def test_update_document_success(self, client: TestClient, test_document, test_project):
        """Test successful document update"""
        update_request = {
            "title": "Updated Test Document",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This is updated content with much more text to test word count calculation properly."
                            }
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "A second paragraph with additional content."
                            }
                        ]
                    }
                ]
            },
            "tags": ["updated", "test", "content"],
            "version": "1.1.0"
        }
        
        response = client.put(f"/api/v1/documents/{test_document.id}", json=update_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify updates
        assert data["title"] == "Updated Test Document"
        assert data["tags"] == ["updated", "test", "content"]
        assert data["version"] == "1.1.0"
        assert data["word_count"] == 20  # Updated word count
        
        # Verify content was updated
        content = data["content"]
        assert len(content["content"]) == 2
        assert "updated content" in content["content"][0]["content"][0]["text"]
        
        # Verify project word count was updated
        repos = get_repositories()
        updated_project = await repos.project.get_by_id(test_project.id)
        assert updated_project is not None
        assert updated_project.word_count == 8  # Should reflect word count delta (20 - 12 = 8)
    
    async def test_update_document_partial(self, client: TestClient, test_document):
        """Test partial document update"""
        update_request = {
            "title": "Partially Updated Title"
            # Only updating title, leaving content and tags unchanged
        }
        
        response = client.put(f"/api/v1/documents/{test_document.id}", json=update_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify only title was updated
        assert data["title"] == "Partially Updated Title"
        assert data["tags"] == ["test", "sample"]  # Should remain unchanged
        assert data["word_count"] == 12  # Should remain unchanged
        assert data["version"] == "1.0.0"  # Should remain unchanged
    
    async def test_update_document_not_found(self, client: TestClient):
        """Test updating nonexistent document"""
        update_request = {
            "title": "Updated Title"
        }
        
        response = client.put("/api/v1/documents/nonexistent-doc", json=update_request)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    async def test_delete_document_success(self, client: TestClient, test_document, test_project):
        """Test successful document deletion"""
        # First update project counts to simulate existing documents
        repos = get_repositories()
        await repos.project.update(test_project.id, {
            "document_count": 1,
            "word_count": 12
        })
        
        response = client.delete(f"/api/v1/documents/{test_document.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        
        # Verify document was deleted
        repos = get_repositories()
        deleted_doc = await repos.document.get_by_id(test_document.id)
        assert deleted_doc is None
        
        # Verify project counts were updated
        updated_project = await repos.project.get_by_id(test_project.id)
        assert updated_project is not None
        assert updated_project.document_count == 0
        assert updated_project.word_count == 0
    
    async def test_delete_document_not_found(self, client: TestClient):
        """Test deleting nonexistent document"""
        response = client.delete("/api/v1/documents/nonexistent-doc")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestDocumentWordCountCalculation:
    """Test word count calculation from ProseMirror content"""
    
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
    async def test_project(self):
        """Create a test project"""
        repos = get_repositories()
        return await repos.project.create({
            "id": "word-count-project",
            "title": "Word Count Test Project"
        })
    
    async def test_word_count_simple_text(self, client: TestClient, test_project):
        """Test word count with simple text"""
        create_request = {
            "project_id": test_project.id,
            "title": "Simple Text Document",
            "path": "/simple.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Hello world test"
                            }
                        ]
                    }
                ]
            }
        }
        
        response = client.post("/api/v1/documents", json=create_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["word_count"] == 3
    
    async def test_word_count_complex_content(self, client: TestClient, test_project):
        """Test word count with complex ProseMirror content"""
        create_request = {
            "project_id": test_project.id,
            "title": "Complex Content Document",
            "path": "/complex.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [
                            {
                                "type": "text",
                                "text": "Chapter Title"
                            }
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This is a "
                            },
                            {
                                "type": "text",
                                "marks": [{"type": "strong"}],
                                "text": "bold word"
                            },
                            {
                                "type": "text",
                                "text": " and this is "
                            },
                            {
                                "type": "text",
                                "marks": [{"type": "em"}],
                                "text": "italic text"
                            },
                            {
                                "type": "text",
                                "text": "."
                            }
                        ]
                    },
                    {
                        "type": "blockquote",
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "This is a quote with five words."
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "bullet_list",
                        "content": [
                            {
                                "type": "list_item",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "First item"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "list_item",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "Second item"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        response = client.post("/api/v1/documents", json=create_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Expected words:
        # "Chapter Title" (2) + "This is a bold word and this is italic text." (11) + 
        # "This is a quote with five words." (7) + "First item" (2) + "Second item" (2) = 24
        assert data["word_count"] == 24
    
    async def test_word_count_empty_content(self, client: TestClient, test_project):
        """Test word count with empty content"""
        create_request = {
            "project_id": test_project.id,
            "title": "Empty Document",
            "path": "/empty.md",
            "content": {
                "type": "doc",
                "content": []
            }
        }
        
        response = client.post("/api/v1/documents", json=create_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["word_count"] == 0
    
    async def test_word_count_whitespace_handling(self, client: TestClient, test_project):
        """Test word count with various whitespace scenarios"""
        create_request = {
            "project_id": test_project.id,
            "title": "Whitespace Test Document",
            "path": "/whitespace.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "  word1   word2    word3  "
                            }
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "\n\nword4\t\tword5\n"
                            }
                        ]
                    }
                ]
            }
        }
        
        response = client.post("/api/v1/documents", json=create_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["word_count"] == 5  # Should ignore extra whitespace


class TestDocumentAPIErrorHandling:
    """Test error handling in document API endpoints"""
    
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
    
    async def test_create_document_invalid_content_structure(self, client: TestClient):
        """Test creating document with invalid content structure"""
        repos = get_repositories()
        project = await repos.project.create({
            "id": "error-test-project",
            "title": "Error Test Project"
        })
        
        # Test with malformed content
        create_request = {
            "project_id": project.id,
            "title": "Invalid Content Document",
            "path": "/invalid.md",
            "content": {
                "type": "doc",
                "content": "invalid_content_structure"  # Should be a list
            }
        }
        
        response = client.post("/api/v1/documents", json=create_request)
        
        # Should handle gracefully and create document with corrected content
        assert response.status_code == 200
        data = response.json()
        assert data["word_count"] == 0  # Should default to 0 for invalid content
    
    async def test_document_api_invalid_id_formats(self, client: TestClient):
        """Test document API with invalid ID formats"""
        invalid_ids = [
            "",  # Empty string
            " ",  # Whitespace
            "id with spaces",  # Spaces
            "id/with/slashes",  # Slashes
        ]
        
        for invalid_id in invalid_ids:
            # Test GET
            response = client.get(f"/api/v1/documents/{invalid_id}")
            assert response.status_code != 200
            
            # Test PUT
            response = client.put(f"/api/v1/documents/{invalid_id}", json={"title": "Test"})
            assert response.status_code != 200
            
            # Test DELETE
            response = client.delete(f"/api/v1/documents/{invalid_id}")
            assert response.status_code != 200


class TestDocumentAPIResponseModels:
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
    
    @pytest.fixture
    async def test_setup(self):
        """Create test project and document"""
        repos = get_repositories()
        
        project = await repos.project.create({
            "id": "response-test-project",
            "title": "Response Test Project"
        })
        
        document = await repos.document.create({
            "id": "response-test-doc",
            "project_id": project.id,
            "title": "Response Test Document",
            "path": "/response_test.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Test content"}]
                    }
                ]
            },
            "tags": ["test", "response"],
            "word_count": 2,
            "version": "1.0.0",
            "is_locked": False,
            "locked_by": None,
            "file_tree_id": "tree-item-123"
        })
        
        return {"project": project, "document": document}
    
    async def test_document_response_model_structure(self, client: TestClient, test_setup):
        """Test that document response matches expected model structure"""
        document = test_setup["document"]
        
        response = client.get(f"/api/v1/documents/{document.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        required_fields = [
            "id", "project_id", "title", "path", "content", "tags",
            "word_count", "created_at", "updated_at", "version",
            "is_locked", "locked_by", "file_tree_id"
        ]
        
        for field in required_fields:
            assert field in data, f"Required field '{field}' missing from response"
        
        # Verify field types
        assert isinstance(data["id"], str)
        assert isinstance(data["project_id"], str)
        assert isinstance(data["title"], str)
        assert isinstance(data["path"], str)
        assert isinstance(data["content"], dict)
        assert isinstance(data["tags"], list)
        assert isinstance(data["word_count"], int)
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["is_locked"], bool)
        assert data["locked_by"] is None or isinstance(data["locked_by"], str)
        assert data["file_tree_id"] is None or isinstance(data["file_tree_id"], str)
        
        # Verify content structure
        content = data["content"]
        assert "type" in content
        assert "content" in content
        assert isinstance(content["type"], str)
        assert isinstance(content["content"], list)
    
    async def test_create_document_response_model(self, client: TestClient, test_setup):
        """Test create document response model"""
        project = test_setup["project"]
        
        create_request = {
            "project_id": project.id,
            "title": "Model Test Document",
            "path": "/model_test.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Model test content"}]
                    }
                ]
            },
            "tags": ["model", "test"]
        }
        
        response = client.post("/api/v1/documents", json=create_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure matches document model
        assert data["title"] == "Model Test Document"
        assert data["path"] == "/model_test.md"
        assert data["project_id"] == project.id
        assert data["tags"] == ["model", "test"]
        assert data["word_count"] == 3  # "Model test content"
        assert data["version"] == "1.0.0"
        assert data["is_locked"] is False
        assert data["locked_by"] is None
        
        # Verify auto-generated fields
        assert "id" in data
        assert len(data["id"]) > 0
        assert "created_at" in data
        assert "updated_at" in data
    
    async def test_delete_response_model(self, client: TestClient, test_setup):
        """Test delete document response model"""
        document = test_setup["document"]
        
        response = client.delete(f"/api/v1/documents/{document.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify delete response structure
        assert "success" in data
        assert isinstance(data["success"], bool)
        assert data["success"] is True