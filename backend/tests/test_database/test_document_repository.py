"""
Tests for DocumentRepository implementations
"""

import pytest
from datetime import datetime
from typing import Dict, Any, List

from src.database.factory import create_repositories
from src.database.interfaces import DocumentRepository, ProjectRepository


class TestDocumentRepositoryInterface:
    """Test the DocumentRepository interface contract"""
    
    @pytest.fixture(params=["memory", "database"])
    async def repos(self, request):
        """Provide both memory and database repository implementations"""
        if request.param == "database":
            # Initialize database for database backend tests
            from src.database.connection import init_database, create_tables, close_database
            
            # Initialize database connection
            init_database()
            
            # Create tables
            await create_tables()
            
            repos = create_repositories(backend=request.param)
            
            yield repos
            
            # Cleanup
            await close_database()
        else:
            repos = create_repositories(backend=request.param)
            yield repos
    
    @pytest.fixture
    async def document_repo(self, repos) -> DocumentRepository:
        """Document repository from the repos fixture"""
        resolved_repos = await repos if hasattr(repos, '__aiter__') else repos
        return resolved_repos.document
    
    @pytest.fixture
    async def project_repo(self, repos) -> ProjectRepository:
        """Project repository from the same repos fixture (for relationships)"""
        resolved_repos = await repos if hasattr(repos, '__aiter__') else repos
        return resolved_repos.project
    
    @pytest.fixture
    async def test_project(self, project_repo: ProjectRepository):
        """Create a test project for document tests"""
        project_data = {
            "id": "test-project-for-docs",
            "title": "Test Project for Documents",
            "description": "A project to test document operations"
        }
        return await project_repo.create(project_data)
    
    async def test_create_document(self, document_repo: DocumentRepository, test_project):
        """Test creating a new document"""
        document_data = {
            "id": "test-doc-create",
            "project_id": test_project.id,
            "title": "Test Document Creation",
            "path": "/test_create.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This is a test document for creation testing."
                            }
                        ]
                    }
                ]
            },
            "tags": ["test", "creation"],
            "word_count": 10,
            "version": "1.0.0",
            "is_locked": False,
            "file_tree_id": "some-file-tree-id"
        }
        
        document = await document_repo.create(document_data)
        
        assert document is not None
        assert document.id == "test-doc-create"
        assert document.project_id == test_project.id
        assert document.title == "Test Document Creation"
        assert document.path == "/test_create.md"
        assert document.content["type"] == "doc"
        assert len(document.content["content"]) == 1
        assert document.tags == ["test", "creation"]
        assert document.word_count == 10
        assert document.version == "1.0.0"
        assert document.is_locked is False
        assert document.locked_by is None
        assert document.file_tree_id == "some-file-tree-id"
        assert isinstance(document.created_at, datetime)
        assert isinstance(document.updated_at, datetime)
    
    async def test_get_document_by_id(self, document_repo: DocumentRepository, test_project):
        """Test retrieving a document by ID"""
        # Create document first
        document_data = {
            "id": "test-doc-get",
            "project_id": test_project.id,
            "title": "Test Document Get",
            "path": "/test_get.md",
            "content": {"type": "doc", "content": []}
        }
        created_document = await document_repo.create(document_data)
        
        # Retrieve the document
        retrieved_document = await document_repo.get_by_id("test-doc-get")
        
        assert retrieved_document is not None
        assert retrieved_document.id == created_document.id
        assert retrieved_document.title == created_document.title
        assert retrieved_document.project_id == created_document.project_id
        assert retrieved_document.path == created_document.path
        assert retrieved_document.created_at == created_document.created_at
    
    async def test_get_nonexistent_document(self, document_repo: DocumentRepository):
        """Test retrieving a document that doesn't exist"""
        result = await document_repo.get_by_id("nonexistent-doc-id")
        assert result is None
    
    async def test_get_documents_by_project_id(self, document_repo: DocumentRepository, test_project):
        """Test retrieving all documents for a specific project"""
        # Create multiple documents for the project
        documents_data = [
            {
                "id": "project-doc-1",
                "project_id": test_project.id,
                "title": "Document 1",
                "path": "/doc1.md",
                "content": {"type": "doc", "content": []},
                "word_count": 100
            },
            {
                "id": "project-doc-2",
                "project_id": test_project.id,
                "title": "Document 2",
                "path": "/doc2.md",
                "content": {"type": "doc", "content": []},
                "word_count": 200
            },
            {
                "id": "project-doc-3",
                "project_id": test_project.id,
                "title": "Document 3",
                "path": "/doc3.md",
                "content": {"type": "doc", "content": []},
                "word_count": 300
            }
        ]
        
        created_docs = []
        for doc_data in documents_data:
            doc = await document_repo.create(doc_data)
            created_docs.append(doc)
        
        # Retrieve all documents for the project
        project_docs = await document_repo.get_by_project_id(test_project.id)
        
        assert len(project_docs) == 3
        
        # Verify all documents belong to the project
        doc_ids = [doc.id for doc in project_docs]
        assert "project-doc-1" in doc_ids
        assert "project-doc-2" in doc_ids
        assert "project-doc-3" in doc_ids
        
        for doc in project_docs:
            assert doc.project_id == test_project.id
    
    async def test_update_document(self, document_repo: DocumentRepository, test_project):
        """Test updating an existing document"""
        # Create document first
        document_data = {
            "id": "test-doc-update",
            "project_id": test_project.id,
            "title": "Original Title",
            "path": "/original.md",
            "content": {"type": "doc", "content": []},
            "tags": ["original"],
            "word_count": 50,
            "version": "1.0.0"
        }
        created_document = await document_repo.create(document_data)
        original_created_at = created_document.created_at
        
        # Update the document
        updates = {
            "title": "Updated Title",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Updated content with more text for word count testing."
                            }
                        ]
                    }
                ]
            },
            "tags": ["updated", "modified"],
            "word_count": 100,
            "version": "1.1.0"
        }
        updated_document = await document_repo.update("test-doc-update", updates)
        
        assert updated_document is not None
        assert updated_document.id == "test-doc-update"
        assert updated_document.title == "Updated Title"
        assert updated_document.content["content"][0]["content"][0]["text"] == "Updated content with more text for word count testing."
        assert updated_document.tags == ["updated", "modified"]
        assert updated_document.word_count == 100
        assert updated_document.version == "1.1.0"
        assert updated_document.created_at == original_created_at  # Should not change
        assert updated_document.updated_at > original_created_at   # Should be updated
        # Path should remain unchanged since not in updates
        assert updated_document.path == "/original.md"
    
    async def test_update_nonexistent_document(self, document_repo: DocumentRepository):
        """Test updating a document that doesn't exist"""
        updates = {"title": "New Title"}
        result = await document_repo.update("nonexistent-doc-id", updates)
        assert result is None
    
    async def test_delete_document(self, document_repo: DocumentRepository, test_project):
        """Test deleting an existing document"""
        # Create document first
        document_data = {
            "id": "test-doc-delete",
            "project_id": test_project.id,
            "title": "To Be Deleted",
            "path": "/delete_me.md",
            "content": {"type": "doc", "content": []}
        }
        await document_repo.create(document_data)
        
        # Verify it exists
        document = await document_repo.get_by_id("test-doc-delete")
        assert document is not None
        
        # Delete the document
        delete_result = await document_repo.delete("test-doc-delete")
        assert delete_result is True
        
        # Verify it's gone
        deleted_document = await document_repo.get_by_id("test-doc-delete")
        assert deleted_document is None
    
    async def test_delete_nonexistent_document(self, document_repo: DocumentRepository):
        """Test deleting a document that doesn't exist"""
        result = await document_repo.delete("nonexistent-doc-id")
        assert result is False


class TestDocumentRepositoryContent:
    """Test document content handling and ProseMirror structures"""
    
    @pytest.fixture
    def memory_repos(self):
        """Memory repositories for content testing"""
        return create_repositories(backend="memory")
    
    @pytest.fixture
    async def test_project(self, memory_repos):
        """Create a test project for content tests"""
        project_data = {
            "id": "content-test-project",
            "title": "Content Test Project"
        }
        return await memory_repos.project.create(project_data)
    
    async def test_create_document_with_complex_prosemirror_content(self, memory_repos, test_project):
        """Test creating a document with complex ProseMirror content"""
        complex_content = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [
                        {
                            "type": "text",
                            "text": "Chapter 1: The Beginning"
                        }
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is the first paragraph with "
                        },
                        {
                            "type": "text",
                            "marks": [{"type": "strong"}],
                            "text": "bold text"
                        },
                        {
                            "type": "text",
                            "text": " and "
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
                                    "text": "This is a quote block with important information."
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
                                            "text": "First bullet point"
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
                                            "text": "Second bullet point"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        document_data = {
            "id": "complex-content-doc",
            "project_id": test_project.id,
            "title": "Complex Content Document",
            "path": "/complex.md",
            "content": complex_content,
            "word_count": 25  # Approximate word count
        }
        
        document = await memory_repos.document.create(document_data)
        
        assert document is not None
        assert document.content["type"] == "doc"
        assert len(document.content["content"]) == 4  # heading, paragraph, blockquote, bullet_list
        
        # Verify heading
        heading = document.content["content"][0]
        assert heading["type"] == "heading"
        assert heading["attrs"]["level"] == 1
        assert heading["content"][0]["text"] == "Chapter 1: The Beginning"
        
        # Verify paragraph with formatting
        paragraph = document.content["content"][1]
        assert paragraph["type"] == "paragraph"
        assert len(paragraph["content"]) == 5  # 5 text nodes with different formatting
        
        # Verify blockquote
        blockquote = document.content["content"][2]
        assert blockquote["type"] == "blockquote"
        
        # Verify bullet list
        bullet_list = document.content["content"][3]
        assert bullet_list["type"] == "bullet_list"
        assert len(bullet_list["content"]) == 2  # 2 list items
    
    async def test_create_document_with_minimal_content(self, memory_repos, test_project):
        """Test creating a document with minimal content"""
        minimal_content = {
            "type": "doc",
            "content": []
        }
        
        document_data = {
            "id": "minimal-content-doc",
            "project_id": test_project.id,
            "title": "Minimal Content Document",
            "path": "/minimal.md",
            "content": minimal_content
        }
        
        document = await memory_repos.document.create(document_data)
        
        assert document is not None
        assert document.content["type"] == "doc"
        assert document.content["content"] == []
        assert document.word_count == 0  # Default
    
    async def test_update_document_content(self, memory_repos, test_project):
        """Test updating document content"""
        # Create document with initial content
        initial_content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Initial content"
                        }
                    ]
                }
            ]
        }
        
        document_data = {
            "id": "update-content-doc",
            "project_id": test_project.id,
            "title": "Update Content Test",
            "path": "/update.md",
            "content": initial_content,
            "word_count": 2
        }
        
        created_doc = await memory_repos.document.create(document_data)
        
        # Update content
        updated_content = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [
                        {
                            "type": "text",
                            "text": "Updated Heading"
                        }
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is the updated content with much more text to test."
                        }
                    ]
                }
            ]
        }
        
        updates = {
            "content": updated_content,
            "word_count": 12
        }
        
        updated_doc = await memory_repos.document.update("update-content-doc", updates)
        
        assert updated_doc is not None
        assert updated_doc.content["content"][0]["type"] == "heading"
        assert updated_doc.content["content"][0]["content"][0]["text"] == "Updated Heading"
        assert updated_doc.content["content"][1]["content"][0]["text"] == "This is the updated content with much more text to test."
        assert updated_doc.word_count == 12


class TestDocumentRepositoryLocking:
    """Test document locking functionality"""
    
    @pytest.fixture
    def memory_repos(self):
        """Memory repositories for locking testing"""
        return create_repositories(backend="memory")
    
    @pytest.fixture
    async def test_project(self, memory_repos):
        """Create a test project for locking tests"""
        project_data = {
            "id": "locking-test-project",
            "title": "Locking Test Project"
        }
        return await memory_repos.project.create(project_data)
    
    async def test_create_locked_document(self, memory_repos, test_project):
        """Test creating a document that is locked"""
        document_data = {
            "id": "locked-doc",
            "project_id": test_project.id,
            "title": "Locked Document",
            "path": "/locked.md",
            "content": {"type": "doc", "content": []},
            "is_locked": True,
            "locked_by": "user_123"
        }
        
        document = await memory_repos.document.create(document_data)
        
        assert document is not None
        assert document.is_locked is True
        assert document.locked_by == "user_123"
    
    async def test_lock_unlocked_document(self, memory_repos, test_project):
        """Test locking an initially unlocked document"""
        # Create unlocked document
        document_data = {
            "id": "to-be-locked-doc",
            "project_id": test_project.id,
            "title": "To Be Locked",
            "path": "/to_lock.md",
            "content": {"type": "doc", "content": []},
            "is_locked": False
        }
        
        created_doc = await memory_repos.document.create(document_data)
        assert created_doc.is_locked is False
        assert created_doc.locked_by is None
        
        # Lock the document
        updates = {
            "is_locked": True,
            "locked_by": "user_456"
        }
        
        locked_doc = await memory_repos.document.update("to-be-locked-doc", updates)
        
        assert locked_doc is not None
        assert locked_doc.is_locked is True
        assert locked_doc.locked_by == "user_456"
    
    async def test_unlock_document(self, memory_repos, test_project):
        """Test unlocking a locked document"""
        # Create locked document
        document_data = {
            "id": "to-be-unlocked-doc",
            "project_id": test_project.id,
            "title": "To Be Unlocked",
            "path": "/to_unlock.md",
            "content": {"type": "doc", "content": []},
            "is_locked": True,
            "locked_by": "user_789"
        }
        
        created_doc = await memory_repos.document.create(document_data)
        assert created_doc.is_locked is True
        assert created_doc.locked_by == "user_789"
        
        # Unlock the document
        updates = {
            "is_locked": False,
            "locked_by": None
        }
        
        unlocked_doc = await memory_repos.document.update("to-be-unlocked-doc", updates)
        
        assert unlocked_doc is not None
        assert unlocked_doc.is_locked is False
        assert unlocked_doc.locked_by is None


class TestDocumentRepositoryVersioning:
    """Test document versioning functionality"""
    
    @pytest.fixture
    def memory_repos(self):
        """Memory repositories for versioning testing"""
        return create_repositories(backend="memory")
    
    @pytest.fixture
    async def test_project(self, memory_repos):
        """Create a test project for versioning tests"""
        project_data = {
            "id": "versioning-test-project",
            "title": "Versioning Test Project"
        }
        return await memory_repos.project.create(project_data)
    
    async def test_document_version_progression(self, memory_repos, test_project):
        """Test document version updates"""
        # Create document with initial version
        document_data = {
            "id": "version-doc",
            "project_id": test_project.id,
            "title": "Versioned Document",
            "path": "/versioned.md",
            "content": {"type": "doc", "content": []},
            "version": "1.0.0"
        }
        
        created_doc = await memory_repos.document.create(document_data)
        assert created_doc.version == "1.0.0"
        
        # Update to version 1.1.0
        updates = {
            "version": "1.1.0",
            "title": "Versioned Document v1.1"
        }
        
        updated_doc = await memory_repos.document.update("version-doc", updates)
        assert updated_doc.version == "1.1.0"
        assert updated_doc.title == "Versioned Document v1.1"
        
        # Update to version 2.0.0
        updates = {
            "version": "2.0.0",
            "title": "Versioned Document v2.0"
        }
        
        final_doc = await memory_repos.document.update("version-doc", updates)
        assert final_doc.version == "2.0.0"
        assert final_doc.title == "Versioned Document v2.0"