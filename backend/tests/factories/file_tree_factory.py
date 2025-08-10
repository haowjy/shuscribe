"""
FileTreeItemFactory for creating FileTreeItem domain models in tests.
"""
import uuid
from datetime import datetime, UTC
from typing import Optional, List, Literal

from src.database.interfaces.models import FileTreeItem


class FileTreeItemFactory:
    """Factory for creating FileTreeItem domain models with realistic test data."""
    
    @staticmethod
    def create(
        id: Optional[str] = None,
        project_id: Optional[str] = None,
        name: Optional[str] = None,
        type: Literal["file", "folder"] = "file",
        path: Optional[str] = None,
        parent_id: Optional[str] = None,
        document_id: Optional[str] = None,
        word_count: Optional[int] = None,
        icon: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs
    ) -> FileTreeItem:
        """
        Create a FileTreeItem domain model with sensible defaults.
        
        Args:
            id: Item ID (auto-generated UUID if not provided)
            project_id: Project ID (auto-generated UUID if not provided)
            name: Item name (auto-generated based on type if not provided)
            type: Item type - "file" or "folder" (default "file")
            path: Item path (auto-generated based on name if not provided)
            parent_id: Parent item ID (default None for root level)
            document_id: Associated document ID (required for files, None for folders)
            word_count: Word count (for files only, None for folders)
            icon: Display icon (auto-selected based on type if not provided)
            tags: List of tag names/IDs (default empty)
            created_at: Creation timestamp (current time if not provided)
            updated_at: Update timestamp (current time if not provided)
            **kwargs: Additional keyword arguments
            
        Returns:
            Properly constructed FileTreeItem domain model
        """
        # Generate defaults
        item_id = id or str(uuid.uuid4())
        item_project_id = project_id or str(uuid.uuid4())
        now = datetime.now(UTC).replace(tzinfo=None)
        
        # Generate name based on type
        if name is None:
            if type == "folder":
                name = f"Test Folder {item_id[:8]}"
            else:
                name = f"test_file_{item_id[:8]}.md"
        
        # Generate path based on name and parent
        if path is None:
            if parent_id:
                # In a real scenario, we'd need to look up parent path
                # For testing, we'll assume a simple structure
                path = f"/parent/{name}"
            else:
                path = f"/{name}"
        
        # Handle file/folder-specific logic
        if type == "folder":
            # Folders cannot have documents or word counts
            document_id = None
            word_count = None
            if icon is None:
                icon = "folder"
        else:  # type == "file"
            # Files need document_id and can have word counts
            if document_id is None:
                document_id = str(uuid.uuid4())
            if word_count is None:
                word_count = 100  # Default word count for test files
            if icon is None:
                icon = "file-text"
        
        # Default tags
        if tags is None:
            tags = []
        
        return FileTreeItem(
            id=item_id,
            project_id=item_project_id,
            name=name,
            type=type,
            path=path,
            parent_id=parent_id,
            document_id=document_id,
            word_count=word_count,
            icon=icon,
            tags=tags,
            created_at=created_at or now,
            updated_at=updated_at or now,
        )
    
    @staticmethod
    def create_folder(
        id: Optional[str] = None,
        name: Optional[str] = None,
        project_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        path: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> FileTreeItem:
        """Create a folder item with proper constraints."""
        folder_name = name or "Test Folder"
        folder_path = path or f"/{folder_name}"
        
        return FileTreeItemFactory.create(
            id=id,
            name=folder_name,
            type="folder",
            path=folder_path,
            project_id=project_id,
            parent_id=parent_id,
            tags=tags or [],
            icon="folder"
        )
    
    @staticmethod
    def create_file(
        id: Optional[str] = None,
        name: Optional[str] = None,
        project_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        path: Optional[str] = None,
        document_id: Optional[str] = None,
        word_count: int = 100,
        tags: Optional[List[str]] = None
    ) -> FileTreeItem:
        """Create a file item with proper constraints."""
        file_name = name or "test_file.md"
        file_path = path or f"/{file_name}"
        
        return FileTreeItemFactory.create(
            id=id,
            name=file_name,
            type="file",
            path=file_path,
            project_id=project_id,
            parent_id=parent_id,
            document_id=document_id,
            word_count=word_count,
            tags=tags or [],
            icon="file-text"
        )
    
    @staticmethod
    def create_character_file(
        character_name: str = "Aria Moonwhisper",
        project_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        document_id: Optional[str] = None
    ) -> FileTreeItem:
        """Create a character file with appropriate naming and tags."""
        safe_name = character_name.lower().replace(" ", "_")
        
        return FileTreeItemFactory.create_file(
            name=f"{safe_name}.md",
            path=f"/characters/{safe_name}.md",
            project_id=project_id,
            parent_id=parent_id,
            document_id=document_id,
            word_count=250,
            tags=["character", "protagonist"],
            icon="user"
        )
    
    @staticmethod
    def create_chapter_file(
        chapter_num: int = 1,
        project_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        document_id: Optional[str] = None,
        word_count: int = 500
    ) -> FileTreeItem:
        """Create a chapter file with appropriate naming and tags."""
        chapter_name = f"chapter_{chapter_num:02d}.md"
        
        return FileTreeItemFactory.create_file(
            name=chapter_name,
            path=f"/chapters/{chapter_name}",
            project_id=project_id,
            parent_id=parent_id,
            document_id=document_id,
            word_count=word_count,
            tags=["chapter", "story"],
            icon="book-open"
        )
    
    @staticmethod
    def create_root_folders(
        project_id: str,
        folder_names: Optional[List[str]] = None
    ) -> List[FileTreeItem]:
        """Create a set of root-level folders for organizing a project."""
        if folder_names is None:
            folder_names = ["Characters", "Locations", "Chapters", "World Building", "Notes"]
        
        folders = []
        for folder_name in folder_names:
            folder = FileTreeItemFactory.create_folder(
                name=folder_name,
                path=f"/{folder_name}",
                project_id=project_id,
                parent_id=None,
                tags=[folder_name.lower().replace(" ", "_")]
            )
            folders.append(folder)
        
        return folders
    
    @staticmethod
    def create_nested_structure(
        project_id: str,
        root_name: str = "Story",
        depth: int = 3
    ) -> List[FileTreeItem]:
        """Create a nested folder structure for testing hierarchy."""
        items = []
        
        # Create root folder
        root_folder = FileTreeItemFactory.create_folder(
            name=root_name,
            path=f"/{root_name}",
            project_id=project_id
        )
        items.append(root_folder)
        
        current_parent = root_folder
        current_path = f"/{root_name}"
        
        # Create nested folders
        for level in range(1, depth):
            level_name = f"Level{level}"
            current_path = f"{current_path}/{level_name}"
            
            level_folder = FileTreeItemFactory.create_folder(
                name=level_name,
                path=current_path,
                project_id=project_id,
                parent_id=current_parent.id
            )
            items.append(level_folder)
            current_parent = level_folder
        
        # Add a file at the deepest level
        file_path = f"{current_path}/deep_file.md"
        deep_file = FileTreeItemFactory.create_file(
            name="deep_file.md",
            path=file_path,
            project_id=project_id,
            parent_id=current_parent.id,
            word_count=150
        )
        items.append(deep_file)
        
        return items