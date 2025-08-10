# backend/src/database/memory/repositories/file_tree_repository.py
"""
Memory FileTree repository implementation
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC

from src.database.interfaces.file_tree_repository import FileTreeRepository
from src.database.interfaces.models import FileTreeItem as DomainFileTreeItem


class MemoryFileTreeRepository(FileTreeRepository):
    """In-memory file tree repository for testing"""
    
    def __init__(self):
        self._items: Dict[str, DomainFileTreeItem] = {}
    
    def _validate_file_tree_constraints(self, item_data: Dict[str, Any], item_id: str = None) -> None:
        """Validate file tree business rules for memory repository"""
        item_type = item_data.get("type")
        document_id = item_data.get("document_id")
        parent_id = item_data.get("parent_id")
        
        # Validate type-document_id consistency
        if item_type == "file" and not document_id:
            raise ValueError("Files must have a document_id")
        if item_type == "folder" and document_id:
            raise ValueError("Folders cannot have a document_id")
        
        # Validate that parent is not a file (files cannot have children)
        if parent_id and parent_id in self._items:
            parent = self._items[parent_id]
            if parent.type == "file":
                raise ValueError("Files cannot have children")
        
        # For updates, validate that if changing to file type, item has no children
        if item_id and item_type == "file":
            has_children = any(item.parent_id == item_id for item in self._items.values())
            if has_children:
                raise ValueError("Cannot change item to file type when it has children")
    
    async def get_by_project_id(self, project_id: str) -> List[DomainFileTreeItem]:
        return [item for item in self._items.values() if item.project_id == project_id]
    
    async def create(self, item_data: Dict[str, Any]) -> DomainFileTreeItem:
        # Validate constraints before creating
        self._validate_file_tree_constraints(item_data)
        
        item_id = item_data.get("id", str(uuid.uuid4()))
        now = datetime.now(UTC).replace(tzinfo=None)
        
        item = DomainFileTreeItem(
            id=item_id,
            project_id=item_data["project_id"],
            name=item_data["name"],
            type=item_data["type"],
            path=item_data["path"],
            parent_id=item_data.get("parent_id"),
            document_id=item_data.get("document_id"),
            icon=item_data.get("icon"),
            word_count=item_data.get("word_count"),
            tags=item_data.get("tags", []),
            created_at=now,
            updated_at=now,
        )
        self._items[item_id] = item
        return item
    
    async def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[DomainFileTreeItem]:
        item = self._items.get(item_id)
        if not item:
            return None
        
        # Validate constraints before updating
        self._validate_file_tree_constraints(updates, item_id)
        
        # Create updated item (dataclass is immutable)
        update_data = {
            "id": item.id,
            "project_id": item.project_id,
            "name": updates.get("name", item.name),
            "type": updates.get("type", item.type),
            "path": updates.get("path", item.path),
            "parent_id": updates.get("parent_id", item.parent_id),
            "document_id": updates.get("document_id", item.document_id),
            "icon": updates.get("icon", item.icon),
            "word_count": updates.get("word_count", item.word_count),
            "tags": updates.get("tags", item.tags),
            "created_at": item.created_at,
            "updated_at": datetime.now(UTC).replace(tzinfo=None),
        }
        
        updated_item = DomainFileTreeItem(**update_data)
        self._items[item_id] = updated_item
        return updated_item
    
    async def delete(self, item_id: str) -> bool:
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False
    
    async def get_by_id(self, item_id: str) -> Optional[DomainFileTreeItem]:
        return self._items.get(item_id)
    
    async def assign_tag(self, item_id: str, tag_id: str) -> bool:
        """Assign tag to file tree item (simplified for memory repository)"""
        # For memory implementation, we simulate the relationship
        # In a real system with relationships, this would be handled by SQLAlchemy
        item = self._items.get(item_id)
        if item:
            # Simulate assignment - in real implementation this would use relationships
            # For now, we'll just return True to indicate successful assignment
            return True
        return False
    
    async def unassign_tag(self, item_id: str, tag_id: str) -> bool:
        """Unassign tag from file tree item (simplified for memory repository)"""
        item = self._items.get(item_id)
        if item:
            # Simulate unassignment - in real implementation this would use relationships
            # For now, we'll just return True to indicate successful unassignment
            return True
        return False
    
    async def get_by_path(self, project_id: str, path: str) -> Optional[DomainFileTreeItem]:
        """Get file tree item by project ID and path"""
        for item in self._items.values():
            if item.project_id == project_id and item.path == path:
                return item
        return None
    
    async def get_children(self, parent_id: str) -> List[DomainFileTreeItem]:
        """Get direct children of a file tree item"""
        return [item for item in self._items.values() if item.parent_id == parent_id]
    
    async def move_item(self, item_id: str, new_parent_id: Optional[str], new_path: str) -> Optional[DomainFileTreeItem]:
        """Move file tree item to new location"""
        return await self.update(item_id, {
            "parent_id": new_parent_id,
            "path": new_path
        })