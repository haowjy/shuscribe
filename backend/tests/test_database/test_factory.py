"""
Tests for Repository Factory and Container
"""

import pytest
from typing import Dict, Any

from src.database.factory import RepositoryContainer, create_repositories, get_repositories, init_repositories, is_initialized, reset_repositories
from src.database.interfaces import ProjectRepository, DocumentRepository, FileTreeRepository


class TestRepositoryContainer:
    """Test the RepositoryContainer class"""
    
    def test_repository_container_attribute_access(self, repository_container: RepositoryContainer):
        """Test that all repositories are accessible via attributes"""
        assert hasattr(repository_container, 'project')
        assert hasattr(repository_container, 'document')
        assert hasattr(repository_container, 'file_tree')
        
        # Verify they're not None
        assert repository_container.project is not None
        assert repository_container.document is not None
        assert repository_container.file_tree is not None
    
    def test_repository_container_all_repositories_present(self, repository_container: RepositoryContainer):
        """Verify all 3 repository types are present and implement their interfaces"""
        assert isinstance(repository_container.project, ProjectRepository)
        assert isinstance(repository_container.document, DocumentRepository)
        assert isinstance(repository_container.file_tree, FileTreeRepository)


class TestMemoryBackend:
    """Test memory backend repository creation"""
    
    def test_memory_backend_creates_all_repositories(self):
        """Verify memory backend creates all 3 repository types"""
        repos = create_repositories(backend="memory")
        
        # Check all repositories exist
        assert repos.project is not None
        assert repos.document is not None
        assert repos.file_tree is not None
    
    def test_memory_backend_repositories_are_independent(self):
        """Each factory call should create new repository instances"""
        repos1 = create_repositories(backend="memory")
        repos2 = create_repositories(backend="memory")
        
        # They should be different instances
        assert repos1.project is not repos2.project
        assert repos1.document is not repos2.document
        assert repos1.file_tree is not repos2.file_tree
    
    async def test_memory_backend_data_isolation(self):
        """Data in one container should not affect another"""
        repos1 = create_repositories(backend="memory")
        repos2 = create_repositories(backend="memory")
        
        # Create project in first repository
        project_data = {
            "id": "test-project-1",
            "title": "Test Project 1",
            "description": "First test project"
        }
        project1 = await repos1.project.create(project_data)
        
        # Verify project doesn't exist in second repository
        project2_check = await repos2.project.get_by_id(project1.id)
        assert project2_check is None
        
        # Verify project exists in first repository
        project1_check = await repos1.project.get_by_id(project1.id)
        assert project1_check is not None
        assert project1_check.title == "Test Project 1"
    
    def test_memory_repositories_implement_interfaces(self):
        """Verify each memory repository implements its interface correctly"""
        repos = create_repositories(backend="memory")
        
        # Check that each repository has the expected interface methods
        # Project repository
        assert hasattr(repos.project, 'create')
        assert hasattr(repos.project, 'get_by_id')
        assert hasattr(repos.project, 'update')
        assert hasattr(repos.project, 'delete')
        
        # Document repository
        assert hasattr(repos.document, 'create')
        assert hasattr(repos.document, 'get_by_id')
        assert hasattr(repos.document, 'get_by_project_id')
        assert hasattr(repos.document, 'update')
        assert hasattr(repos.document, 'delete')
        
        # File tree repository
        assert hasattr(repos.file_tree, 'create')
        assert hasattr(repos.file_tree, 'get_by_project_id')
        assert hasattr(repos.file_tree, 'update')
        assert hasattr(repos.file_tree, 'delete')


class TestDatabaseBackend:
    """Test database backend repository creation"""
    
    def test_database_backend_creates_all_repositories(self):
        """Verify database backend creates all 3 repository types"""
        repos = create_repositories(backend="database")
        
        # Check all repositories exist
        assert repos.project is not None
        assert repos.document is not None
        assert repos.file_tree is not None
        
        # Verify they implement the interfaces
        assert isinstance(repos.project, ProjectRepository)
        assert isinstance(repos.document, DocumentRepository)
        assert isinstance(repos.file_tree, FileTreeRepository)


class TestFactoryErrors:
    """Test error handling in the factory"""
    
    def test_unknown_backend_raises_error(self):
        """Test that invalid backend type raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            create_repositories(backend="invalid_backend")
        
        assert "Unknown backend: invalid_backend" in str(exc_info.value)


class TestGlobalRepositoryManagement:
    """Test global repository initialization and management"""
    
    def test_init_and_get_repositories(self):
        """Test global repository initialization and retrieval"""
        # Reset first
        reset_repositories()
        assert not is_initialized()
        
        # Initialize with memory backend
        init_repositories(backend="memory")
        assert is_initialized()
        
        # Get repositories
        repos = get_repositories()
        assert isinstance(repos, RepositoryContainer)
        assert repos.project is not None
        assert repos.document is not None
        assert repos.file_tree is not None
    
    def test_get_repositories_without_init_raises_error(self):
        """Test that getting repositories without initialization raises error"""
        reset_repositories()
        
        with pytest.raises(RuntimeError) as exc_info:
            get_repositories()
        
        assert "Repositories not initialized" in str(exc_info.value)
    
    def test_reset_repositories(self):
        """Test repository reset functionality"""
        # Initialize
        init_repositories(backend="memory")
        assert is_initialized()
        
        # Reset
        reset_repositories()
        assert not is_initialized()
        
        # Should raise error after reset
        with pytest.raises(RuntimeError):
            get_repositories()


class TestIntegration:
    """Integration tests using multiple repositories together"""
    
    async def test_cross_repository_workflow(self, repository_container: RepositoryContainer):
        """Test a workflow that uses multiple repositories"""
        
        # Create a project
        project_data = {
            "id": "workflow-project",
            "title": "Integration Test Project",
            "description": "Testing cross-repository workflow",
            "tags": ["test", "integration"],
            "collaborators": [
                {
                    "user_id": "user_1",
                    "role": "owner",
                    "name": "Test Owner"
                }
            ]
        }
        project = await repository_container.project.create(project_data)
        
        # Create a document in the project
        document_data = {
            "id": "workflow-document",
            "project_id": project.id,
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
                                "text": "This is a test document for integration testing."
                            }
                        ]
                    }
                ]
            },
            "tags": ["test"],
            "word_count": 10
        }
        document = await repository_container.document.create(document_data)
        
        # Create a file tree item for the document
        file_tree_data = {
            "id": "workflow-file",
            "project_id": project.id,
            "name": "test_document.md",
            "type": "file",
            "path": "/test_document.md",
            "document_id": document.id,
            "icon": "file-text",
            "tags": ["test"],
            "word_count": 10
        }
        file_item = await repository_container.file_tree.create(file_tree_data)
        
        # Verify relationships
        assert document.project_id == project.id
        assert file_item.project_id == project.id
        assert file_item.document_id == document.id
        
        # Verify data persistence within the container
        retrieved_project = await repository_container.project.get_by_id(project.id)
        retrieved_document = await repository_container.document.get_by_id(document.id)
        file_tree_items = await repository_container.file_tree.get_by_project_id(project.id)
        
        assert retrieved_project is not None
        assert retrieved_document is not None
        assert len(file_tree_items) == 1
        
        assert retrieved_project.title == "Integration Test Project"
        assert retrieved_document.title == "Test Document"
        assert file_tree_items[0].name == "test_document.md"
    
    async def test_document_project_relationship(self, repository_container: RepositoryContainer):
        """Test document-project relationship queries"""
        
        # Create project
        project_data = {
            "id": "rel-project",
            "title": "Relationship Test",
            "description": "Testing relationships"
        }
        project = await repository_container.project.create(project_data)
        
        # Create multiple documents
        doc_ids = []
        for i in range(3):
            doc_data = {
                "id": f"rel-doc-{i}",
                "project_id": project.id,
                "title": f"Document {i}",
                "path": f"/doc_{i}.md",
                "content": {"type": "doc", "content": []},
                "word_count": 10 * i
            }
            doc = await repository_container.document.create(doc_data)
            doc_ids.append(doc.id)
        
        # Query documents by project
        project_docs = await repository_container.document.get_by_project_id(project.id)
        assert len(project_docs) == 3
        
        # Verify all documents belong to the project
        for doc in project_docs:
            assert doc.project_id == project.id
            assert doc.id in doc_ids
    
    async def test_hierarchical_file_tree(self, repository_container: RepositoryContainer):
        """Test hierarchical file tree structure"""
        
        # Create project
        project_data = {
            "id": "tree-project",
            "title": "File Tree Test",
            "description": "Testing file tree hierarchy"
        }
        project = await repository_container.project.create(project_data)
        
        # Create root folder
        root_folder = await repository_container.file_tree.create({
            "id": "root-folder",
            "project_id": project.id,
            "name": "Characters",
            "type": "folder",
            "path": "/Characters",
            "parent_id": None
        })
        
        # Create sub-folder
        sub_folder = await repository_container.file_tree.create({
            "id": "sub-folder",
            "project_id": project.id,
            "name": "Protagonists",
            "type": "folder",
            "path": "/Characters/Protagonists",
            "parent_id": root_folder.id
        })
        
        # Create file in sub-folder
        file_item = await repository_container.file_tree.create({
            "id": "char-file",
            "project_id": project.id,
            "name": "hero.md",
            "type": "file",
            "path": "/Characters/Protagonists/hero.md",
            "parent_id": sub_folder.id
        })
        
        # Query all items for project
        all_items = await repository_container.file_tree.get_by_project_id(project.id)
        assert len(all_items) == 3
        
        # Verify hierarchy
        items_by_id = {item.id: item for item in all_items}
        
        assert items_by_id["root-folder"].parent_id is None
        assert items_by_id["sub-folder"].parent_id == "root-folder"
        assert items_by_id["char-file"].parent_id == "sub-folder"
        
        # Verify paths
        assert items_by_id["root-folder"].path == "/Characters"
        assert items_by_id["sub-folder"].path == "/Characters/Protagonists"
        assert items_by_id["char-file"].path == "/Characters/Protagonists/hero.md"