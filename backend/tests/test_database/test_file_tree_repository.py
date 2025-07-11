"""
Tests for FileTreeRepository implementations
"""

import pytest
from datetime import datetime
from typing import Dict, Any, List

from src.database.factory import create_repositories
from src.database.interfaces import FileTreeRepository, ProjectRepository


class TestFileTreeRepositoryInterface:
    """Test the FileTreeRepository interface contract"""
    
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
    async def file_tree_repo(self, repos) -> FileTreeRepository:
        """File tree repository from the repos fixture"""
        resolved_repos = await repos if hasattr(repos, '__aiter__') else repos
        return resolved_repos.file_tree
    
    @pytest.fixture
    async def project_repo(self, repos) -> ProjectRepository:
        """Project repository from the same repos fixture (for relationships)"""
        resolved_repos = await repos if hasattr(repos, '__aiter__') else repos
        return resolved_repos.project
    
    @pytest.fixture
    async def test_project(self, project_repo: ProjectRepository):
        """Create a test project for file tree tests"""
        project_data = {
            "id": "test-project-for-files",
            "title": "Test Project for File Tree",
            "description": "A project to test file tree operations"
        }
        return await project_repo.create(project_data)
    
    async def test_create_file_tree_item(self, file_tree_repo: FileTreeRepository, test_project):
        """Test creating a new file tree item"""
        item_data = {
            "id": "test-file-create",
            "project_id": test_project.id,
            "name": "test_file.md",
            "type": "file",
            "path": "/test_file.md",
            "parent_id": None,
            "document_id": "some-doc-id",
            "icon": "file-text",
            "tags": ["test", "file"],
            "word_count": 150
        }
        
        item = await file_tree_repo.create(item_data)
        
        assert item is not None
        assert item.id == "test-file-create"
        assert item.project_id == test_project.id
        assert item.name == "test_file.md"
        assert item.type == "file"
        assert item.path == "/test_file.md"
        assert item.parent_id is None
        assert item.document_id == "some-doc-id"
        assert item.icon == "file-text"
        assert item.tags == ["test", "file"]
        assert item.word_count == 150
        assert isinstance(item.created_at, datetime)
        assert isinstance(item.updated_at, datetime)
    
    async def test_create_folder_item(self, file_tree_repo: FileTreeRepository, test_project):
        """Test creating a folder in the file tree"""
        folder_data = {
            "id": "test-folder-create",
            "project_id": test_project.id,
            "name": "Characters",
            "type": "folder",
            "path": "/Characters",
            "parent_id": None,
            "icon": "folder",
            "tags": ["characters", "organization"]
        }
        
        folder = await file_tree_repo.create(folder_data)
        
        assert folder is not None
        assert folder.id == "test-folder-create"
        assert folder.type == "folder"
        assert folder.name == "Characters"
        assert folder.path == "/Characters"
        assert folder.document_id is None  # Folders don't have documents
        assert folder.word_count is None   # Folders don't have word counts
        assert folder.icon == "folder"
        assert folder.tags == ["characters", "organization"]
    
    async def test_get_items_by_project_id(self, file_tree_repo: FileTreeRepository, test_project):
        """Test retrieving all file tree items for a specific project"""
        # Create multiple items for the project
        items_data = [
            {
                "id": "project-folder-1",
                "project_id": test_project.id,
                "name": "Chapters",
                "type": "folder",
                "path": "/Chapters",
                "parent_id": None
            },
            {
                "id": "project-file-1",
                "project_id": test_project.id,
                "name": "chapter1.md",
                "type": "file",
                "path": "/Chapters/chapter1.md",
                "parent_id": "project-folder-1",
                "document_id": "doc-1",
                "word_count": 500
            },
            {
                "id": "project-file-2",
                "project_id": test_project.id,
                "name": "notes.md",
                "type": "file",
                "path": "/notes.md",
                "parent_id": None,
                "document_id": "doc-2",
                "word_count": 200
            }
        ]
        
        created_items = []
        for item_data in items_data:
            item = await file_tree_repo.create(item_data)
            created_items.append(item)
        
        # Retrieve all items for the project
        project_items = await file_tree_repo.get_by_project_id(test_project.id)
        
        assert len(project_items) == 3
        
        # Verify all items belong to the project
        item_ids = [item.id for item in project_items]
        assert "project-folder-1" in item_ids
        assert "project-file-1" in item_ids
        assert "project-file-2" in item_ids
        
        for item in project_items:
            assert item.project_id == test_project.id
    
    async def test_update_file_tree_item(self, file_tree_repo: FileTreeRepository, test_project):
        """Test updating an existing file tree item"""
        # Create item first
        item_data = {
            "id": "test-item-update",
            "project_id": test_project.id,
            "name": "original.md",
            "type": "file",
            "path": "/original.md",
            "tags": ["original"],
            "word_count": 100
        }
        created_item = await file_tree_repo.create(item_data)
        original_created_at = created_item.created_at
        
        # Update the item
        updates = {
            "name": "renamed.md",
            "path": "/renamed.md",
            "tags": ["updated", "renamed"],
            "word_count": 200,
            "icon": "file-edit"
        }
        updated_item = await file_tree_repo.update("test-item-update", updates)
        
        assert updated_item is not None
        assert updated_item.id == "test-item-update"
        assert updated_item.name == "renamed.md"
        assert updated_item.path == "/renamed.md"
        assert updated_item.tags == ["updated", "renamed"]
        assert updated_item.word_count == 200
        assert updated_item.icon == "file-edit"
        assert updated_item.created_at == original_created_at  # Should not change
        assert updated_item.updated_at > original_created_at   # Should be updated
        # Type and project_id should remain unchanged
        assert updated_item.type == "file"
        assert updated_item.project_id == test_project.id
    
    async def test_update_nonexistent_item(self, file_tree_repo: FileTreeRepository):
        """Test updating a file tree item that doesn't exist"""
        updates = {"name": "new_name.md"}
        result = await file_tree_repo.update("nonexistent-item-id", updates)
        assert result is None
    
    async def test_delete_file_tree_item(self, file_tree_repo: FileTreeRepository, test_project):
        """Test deleting an existing file tree item"""
        # Create item first
        item_data = {
            "id": "test-item-delete",
            "project_id": test_project.id,
            "name": "to_delete.md",
            "type": "file",
            "path": "/to_delete.md"
        }
        await file_tree_repo.create(item_data)
        
        # Verify it exists
        items = await file_tree_repo.get_by_project_id(test_project.id)
        item_ids = [item.id for item in items]
        assert "test-item-delete" in item_ids
        
        # Delete the item
        delete_result = await file_tree_repo.delete("test-item-delete")
        assert delete_result is True
        
        # Verify it's gone
        items_after = await file_tree_repo.get_by_project_id(test_project.id)
        item_ids_after = [item.id for item in items_after]
        assert "test-item-delete" not in item_ids_after
    
    async def test_delete_nonexistent_item(self, file_tree_repo: FileTreeRepository):
        """Test deleting a file tree item that doesn't exist"""
        result = await file_tree_repo.delete("nonexistent-item-id")
        assert result is False


class TestFileTreeHierarchy:
    """Test hierarchical file tree structure and relationships"""
    
    @pytest.fixture
    def memory_repos(self):
        """Memory repositories for hierarchy testing"""
        return create_repositories(backend="memory")
    
    @pytest.fixture
    async def test_project(self, memory_repos):
        """Create a test project for hierarchy tests"""
        project_data = {
            "id": "hierarchy-test-project",
            "title": "Hierarchy Test Project"
        }
        return await memory_repos.project.create(project_data)
    
    async def test_create_nested_folder_structure(self, memory_repos, test_project):
        """Test creating a nested folder structure"""
        # Create root folder
        root_folder = await memory_repos.file_tree.create({
            "id": "root-folder",
            "project_id": test_project.id,
            "name": "Story",
            "type": "folder",
            "path": "/Story",
            "parent_id": None
        })
        
        # Create subfolder
        sub_folder = await memory_repos.file_tree.create({
            "id": "sub-folder",
            "project_id": test_project.id,
            "name": "Chapters",
            "type": "folder",
            "path": "/Story/Chapters",
            "parent_id": root_folder.id
        })
        
        # Create sub-subfolder
        sub_sub_folder = await memory_repos.file_tree.create({
            "id": "sub-sub-folder",
            "project_id": test_project.id,
            "name": "Arc1",
            "type": "folder",
            "path": "/Story/Chapters/Arc1",
            "parent_id": sub_folder.id
        })
        
        # Create file in deepest folder
        file_item = await memory_repos.file_tree.create({
            "id": "nested-file",
            "project_id": test_project.id,
            "name": "chapter1.md",
            "type": "file",
            "path": "/Story/Chapters/Arc1/chapter1.md",
            "parent_id": sub_sub_folder.id,
            "document_id": "doc-chapter-1"
        })
        
        # Verify the hierarchy
        all_items = await memory_repos.file_tree.get_by_project_id(test_project.id)
        assert len(all_items) == 4
        
        items_by_id = {item.id: item for item in all_items}
        
        # Verify parent-child relationships
        assert items_by_id["root-folder"].parent_id is None
        assert items_by_id["sub-folder"].parent_id == "root-folder"
        assert items_by_id["sub-sub-folder"].parent_id == "sub-folder"
        assert items_by_id["nested-file"].parent_id == "sub-sub-folder"
        
        # Verify paths reflect hierarchy
        assert items_by_id["root-folder"].path == "/Story"
        assert items_by_id["sub-folder"].path == "/Story/Chapters"
        assert items_by_id["sub-sub-folder"].path == "/Story/Chapters/Arc1"
        assert items_by_id["nested-file"].path == "/Story/Chapters/Arc1/chapter1.md"
    
    async def test_multiple_root_folders(self, memory_repos, test_project):
        """Test creating multiple root-level folders"""
        root_folders = [
            {
                "id": "characters-root",
                "name": "Characters",
                "path": "/Characters"
            },
            {
                "id": "locations-root",
                "name": "Locations",
                "path": "/Locations"
            },
            {
                "id": "chapters-root",
                "name": "Chapters",
                "path": "/Chapters"
            }
        ]
        
        created_folders = []
        for folder_data in root_folders:
            folder = await memory_repos.file_tree.create({
                "id": folder_data["id"],
                "project_id": test_project.id,
                "name": folder_data["name"],
                "type": "folder",
                "path": folder_data["path"],
                "parent_id": None
            })
            created_folders.append(folder)
        
        # Verify all are root folders
        for folder in created_folders:
            assert folder.parent_id is None
            assert folder.type == "folder"
            assert folder.path.count("/") == 1  # Only one slash for root folders
    
    async def test_folder_with_multiple_children(self, memory_repos, test_project):
        """Test a folder containing multiple files and subfolders"""
        # Create parent folder
        parent_folder = await memory_repos.file_tree.create({
            "id": "parent-folder",
            "project_id": test_project.id,
            "name": "Characters",
            "type": "folder",
            "path": "/Characters",
            "parent_id": None
        })
        
        # Create multiple children
        children_data = [
            {
                "id": "child-folder-1",
                "name": "Protagonists",
                "type": "folder",
                "path": "/Characters/Protagonists"
            },
            {
                "id": "child-folder-2",
                "name": "Antagonists",
                "type": "folder",
                "path": "/Characters/Antagonists"
            },
            {
                "id": "child-file-1",
                "name": "overview.md",
                "type": "file",
                "path": "/Characters/overview.md",
                "document_id": "doc-overview"
            },
            {
                "id": "child-file-2",
                "name": "relationships.md",
                "type": "file",
                "path": "/Characters/relationships.md",
                "document_id": "doc-relationships"
            }
        ]
        
        created_children = []
        for child_data in children_data:
            child = await memory_repos.file_tree.create({
                "id": child_data["id"],
                "project_id": test_project.id,
                "name": child_data["name"],
                "type": child_data["type"],
                "path": child_data["path"],
                "parent_id": parent_folder.id,
                "document_id": child_data.get("document_id")
            })
            created_children.append(child)
        
        # Verify all children have correct parent
        for child in created_children:
            assert child.parent_id == parent_folder.id
            assert child.path.startswith("/Characters/")
        
        # Verify we have both folders and files
        folders = [c for c in created_children if c.type == "folder"]
        files = [c for c in created_children if c.type == "file"]
        assert len(folders) == 2
        assert len(files) == 2
    
    async def test_move_item_to_different_parent(self, memory_repos, test_project):
        """Test moving a file tree item to a different parent folder"""
        # Create two folders
        folder1 = await memory_repos.file_tree.create({
            "id": "folder-1",
            "project_id": test_project.id,
            "name": "Folder1",
            "type": "folder",
            "path": "/Folder1",
            "parent_id": None
        })
        
        folder2 = await memory_repos.file_tree.create({
            "id": "folder-2",
            "project_id": test_project.id,
            "name": "Folder2",
            "type": "folder",
            "path": "/Folder2",
            "parent_id": None
        })
        
        # Create file in folder1
        file_item = await memory_repos.file_tree.create({
            "id": "movable-file",
            "project_id": test_project.id,
            "name": "movable.md",
            "type": "file",
            "path": "/Folder1/movable.md",
            "parent_id": folder1.id,
            "document_id": "doc-movable"
        })
        
        assert file_item.parent_id == folder1.id
        assert file_item.path == "/Folder1/movable.md"
        
        # Move file to folder2
        updates = {
            "parent_id": folder2.id,
            "path": "/Folder2/movable.md"
        }
        moved_file = await memory_repos.file_tree.update("movable-file", updates)
        
        assert moved_file is not None
        assert moved_file.parent_id == folder2.id
        assert moved_file.path == "/Folder2/movable.md"
        # Name and other properties should remain the same
        assert moved_file.name == "movable.md"
        assert moved_file.document_id == "doc-movable"


class TestFileTreeDocumentRelationships:
    """Test relationships between file tree items and documents"""
    
    @pytest.fixture
    def memory_repos(self):
        """Memory repositories for document relationship testing"""
        return create_repositories(backend="memory")
    
    @pytest.fixture
    async def test_project(self, memory_repos):
        """Create a test project for document relationship tests"""
        project_data = {
            "id": "doc-rel-test-project",
            "title": "Document Relationship Test Project"
        }
        return await memory_repos.project.create(project_data)
    
    async def test_file_with_document_reference(self, memory_repos, test_project):
        """Test file tree item with document reference"""
        # Create a document first
        document = await memory_repos.document.create({
            "id": "test-document",
            "project_id": test_project.id,
            "title": "Test Document",
            "path": "/test.md",
            "content": {"type": "doc", "content": []},
            "word_count": 250
        })
        
        # Create file tree item that references the document
        file_item = await memory_repos.file_tree.create({
            "id": "file-with-doc",
            "project_id": test_project.id,
            "name": "test.md",
            "type": "file",
            "path": "/test.md",
            "document_id": document.id,
            "word_count": 250  # Should match document
        })
        
        assert file_item.document_id == document.id
        assert file_item.word_count == document.word_count
        assert file_item.path == document.path
    
    async def test_folder_without_document_reference(self, memory_repos, test_project):
        """Test that folders don't have document references"""
        folder = await memory_repos.file_tree.create({
            "id": "folder-no-doc",
            "project_id": test_project.id,
            "name": "NoDocFolder",
            "type": "folder",
            "path": "/NoDocFolder",
            "parent_id": None
        })
        
        assert folder.document_id is None
        assert folder.word_count is None  # Folders don't have word counts
    
    async def test_update_file_document_reference(self, memory_repos, test_project):
        """Test updating a file's document reference"""
        # Create two documents
        doc1 = await memory_repos.document.create({
            "id": "doc-1",
            "project_id": test_project.id,
            "title": "Document 1",
            "path": "/doc1.md",
            "content": {"type": "doc", "content": []},
            "word_count": 100
        })
        
        doc2 = await memory_repos.document.create({
            "id": "doc-2",
            "project_id": test_project.id,
            "title": "Document 2",
            "path": "/doc2.md",
            "content": {"type": "doc", "content": []},
            "word_count": 200
        })
        
        # Create file item pointing to doc1
        file_item = await memory_repos.file_tree.create({
            "id": "switchable-file",
            "project_id": test_project.id,
            "name": "switchable.md",
            "type": "file",
            "path": "/doc1.md",
            "document_id": doc1.id,
            "word_count": 100
        })
        
        assert file_item.document_id == doc1.id
        assert file_item.word_count == 100
        
        # Update to point to doc2
        updates = {
            "document_id": doc2.id,
            "word_count": 200,
            "path": "/doc2.md"
        }
        updated_file = await memory_repos.file_tree.update("switchable-file", updates)
        
        assert updated_file.document_id == doc2.id
        assert updated_file.word_count == 200
        assert updated_file.path == "/doc2.md"


class TestFileTreeTagging:
    """Test file tree item tagging functionality"""
    
    @pytest.fixture
    def memory_repos(self):
        """Memory repositories for tagging testing"""
        return create_repositories(backend="memory")
    
    @pytest.fixture
    async def test_project(self, memory_repos):
        """Create a test project for tagging tests"""
        project_data = {
            "id": "tagging-test-project",
            "title": "Tagging Test Project"
        }
        return await memory_repos.project.create(project_data)
    
    async def test_create_item_with_tags(self, memory_repos, test_project):
        """Test creating file tree items with tags"""
        items_with_tags = [
            {
                "id": "tagged-file-1",
                "name": "hero.md",
                "type": "file",
                "path": "/Characters/hero.md",
                "tags": ["character", "protagonist", "main"]
            },
            {
                "id": "tagged-folder-1",
                "name": "Locations",
                "type": "folder",
                "path": "/Locations",
                "tags": ["worldbuilding", "setting"]
            },
            {
                "id": "untagged-file",
                "name": "notes.md",
                "type": "file",
                "path": "/notes.md",
                "tags": []  # Explicitly empty
            }
        ]
        
        created_items = []
        for item_data in items_with_tags:
            item = await memory_repos.file_tree.create({
                "id": item_data["id"],
                "project_id": test_project.id,
                "name": item_data["name"],
                "type": item_data["type"],
                "path": item_data["path"],
                "tags": item_data["tags"]
            })
            created_items.append(item)
        
        # Verify tags
        assert created_items[0].tags == ["character", "protagonist", "main"]
        assert created_items[1].tags == ["worldbuilding", "setting"]
        assert created_items[2].tags == []
    
    async def test_update_item_tags(self, memory_repos, test_project):
        """Test updating file tree item tags"""
        # Create item with initial tags
        item = await memory_repos.file_tree.create({
            "id": "taggable-item",
            "project_id": test_project.id,
            "name": "character.md",
            "type": "file",
            "path": "/character.md",
            "tags": ["character", "draft"]
        })
        
        assert item.tags == ["character", "draft"]
        
        # Update tags
        updates = {
            "tags": ["character", "published", "important", "main"]
        }
        updated_item = await memory_repos.file_tree.update("taggable-item", updates)
        
        assert updated_item.tags == ["character", "published", "important", "main"]
        
        # Clear tags
        clear_updates = {
            "tags": []
        }
        cleared_item = await memory_repos.file_tree.update("taggable-item", clear_updates)
        
        assert cleared_item.tags == []