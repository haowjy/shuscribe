"""
Schema validation tests for Document API endpoints

These tests specifically validate that API responses match expected schemas
to prevent frontend-backend contract mismatches.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any, List

from src.main import app
from src.database.factory import init_repositories, reset_repositories, get_repositories


class TestDocumentSchemaValidation:
    """Test document API schema validation"""
    
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
    async def test_data(self):
        """Create test project, tags, and document"""
        repos = get_repositories()
        
        # Create project
        project = await repos.project.create({
            "id": "schema-test-project",
            "title": "Schema Test Project",
            "description": "Project for schema validation tests",
            "word_count": 0,
            "document_count": 0,
            "tags": ["project", "test"]
        })
        
        # Create tags with metadata
        tag1 = await repos.tag.create({
            "id": "tag-chapter",
            "name": "chapter",
            "icon": "book-open",
            "color": "#3b82f6",
            "project_id": project.id
        })
        
        tag2 = await repos.tag.create({
            "id": "tag-intro", 
            "name": "intro",
            "icon": "play",
            "color": "#10b981",
            "project_id": project.id
        })
        
        # Create document with tags
        document = await repos.document.create({
            "id": "schema-test-document",
            "project_id": project.id,
            "title": "Schema Test Document",
            "path": "/schema_test.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Schema validation content"}]
                    }
                ]
            },
            "tags": [tag1, tag2],
            "word_count": 3,
            "version": "1.0.0",
            "is_locked": False
        })
        
        return {
            "project": project,
            "document": document,
            "tags": [tag1, tag2]
        }
    
    def validate_tag_info_schema(self, tag_data: Dict[str, Any]) -> bool:
        """Validate TagInfo schema structure"""
        required_fields = ["id", "name"]
        optional_fields = ["icon", "color"]
        
        # Check required fields
        for field in required_fields:
            if field not in tag_data:
                return False
            if not isinstance(tag_data[field], str):
                return False
        
        # Check optional fields if present
        for field in optional_fields:
            if field in tag_data and tag_data[field] is not None:
                if not isinstance(tag_data[field], str):
                    return False
        
        return True
    
    def validate_document_response_schema(self, response_data: Dict[str, Any]) -> bool:
        """Validate DocumentResponse schema structure"""
        required_fields = [
            "id", "project_id", "title", "path", "content", "tags",
            "word_count", "created_at", "updated_at", "version",
            "is_locked", "locked_by", "file_tree_id"
        ]
        
        # Check all required fields exist
        for field in required_fields:
            if field not in response_data:
                return False
        
        # Validate field types
        if not isinstance(response_data["tags"], list):
            return False
        
        # Validate each tag in the list
        for tag in response_data["tags"]:
            if not self.validate_tag_info_schema(tag):
                return False
        
        return True
    
    async def test_document_response_tags_schema(self, client: TestClient, test_data):
        """Test that document response returns TagInfo objects, not strings"""
        document = test_data["document"]
        expected_tags = test_data["tags"]
        
        response = client.get(f"/api/v1/documents/{document.id}")
        
        assert response.status_code == 200
        data = response.json()["data"]
        
        # Validate overall schema
        assert self.validate_document_response_schema(data)
        
        # Validate tags structure specifically
        assert isinstance(data["tags"], list)
        assert len(data["tags"]) == 2
        
        for tag_data in data["tags"]:
            # Must be an object, not a string
            assert isinstance(tag_data, dict), f"Tag should be object, got {type(tag_data)}"
            
            # Must have required TagInfo fields
            assert "id" in tag_data
            assert "name" in tag_data
            assert isinstance(tag_data["id"], str)
            assert isinstance(tag_data["name"], str)
            
            # Should have metadata fields
            if "icon" in tag_data:
                assert isinstance(tag_data["icon"], str) or tag_data["icon"] is None
            if "color" in tag_data:
                assert isinstance(tag_data["color"], str) or tag_data["color"] is None
        
        # Verify specific tag data matches what we created
        tag_names = [tag["name"] for tag in data["tags"]]
        assert "chapter" in tag_names
        assert "intro" in tag_names
        
        chapter_tag = next(tag for tag in data["tags"] if tag["name"] == "chapter")
        intro_tag = next(tag for tag in data["tags"] if tag["name"] == "intro")
        
        assert chapter_tag["icon"] == "book-open"
        assert chapter_tag["color"] == "#3b82f6"
        assert intro_tag["icon"] == "play"
        assert intro_tag["color"] == "#10b981"
    
    async def test_create_document_request_tags_schema(self, client: TestClient, test_data):
        """Test that create document accepts tag names as strings"""
        project = test_data["project"]
        
        create_request = {
            "project_id": project.id,
            "title": "Schema Create Test",
            "path": "/schema_create.md",
            "content": {
                "type": "doc",
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "Create test"}]}
                ]
            },
            "tags": ["chapter", "intro"]  # Should accept strings
        }
        
        response = client.post("/api/v1/documents", json=create_request)
        
        assert response.status_code == 200
        data = response.json()["data"]
        
        # Response should return TagInfo objects
        assert self.validate_document_response_schema(data)
        assert len(data["tags"]) == 2
        
        for tag_data in data["tags"]:
            assert isinstance(tag_data, dict)
            assert "id" in tag_data
            assert "name" in tag_data
        
        tag_names = [tag["name"] for tag in data["tags"]]
        assert "chapter" in tag_names
        assert "intro" in tag_names
    
    async def test_frontend_backend_contract_consistency(self, client: TestClient, test_data):
        """Test that the API contract matches frontend expectations"""
        document = test_data["document"]
        
        response = client.get(f"/api/v1/documents/{document.id}")
        data = response.json()["data"]
        
        # This test documents the expected frontend-backend contract:
        # 1. Requests send tag names as strings
        # 2. Responses return TagInfo objects with metadata
        
        # Verify response structure matches frontend DocumentResponse interface
        expected_structure = {
            "id": str,
            "project_id": str, 
            "title": str,
            "path": str,
            "content": dict,
            "tags": list,  # List of TagInfo objects
            "word_count": int,
            "created_at": str,
            "updated_at": str,
            "version": str,
            "is_locked": bool,
            "locked_by": (str, type(None)),
            "file_tree_id": (str, type(None))
        }
        
        for field, expected_type in expected_structure.items():
            assert field in data, f"Missing field: {field}"
            if isinstance(expected_type, tuple):
                assert isinstance(data[field], expected_type), f"Field {field} should be {expected_type}, got {type(data[field])}"
            else:
                assert isinstance(data[field], expected_type), f"Field {field} should be {expected_type}, got {type(data[field])}"
        
        # Verify tags are TagInfo objects, not strings
        for tag in data["tags"]:
            assert isinstance(tag, dict), "Tags should be objects in responses"
            assert "id" in tag and "name" in tag, "TagInfo must have id and name"