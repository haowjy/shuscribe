# backend/src/database/interfaces/file_tree_repository.py
"""
File tree repository interface
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from src.database.models import FileTreeItem


class FileTreeRepository(ABC):
    """Abstract file tree repository interface"""
    
    @abstractmethod
    async def get_by_project_id(self, project_id: str) -> List[FileTreeItem]:
        """Get file tree for a project"""
        pass
    
    @abstractmethod
    async def create(self, item_data: Dict[str, Any]) -> FileTreeItem:
        """Create new file tree item"""
        pass
    
    @abstractmethod
    async def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[FileTreeItem]:
        """Update file tree item"""
        pass
    
    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """Delete file tree item"""
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[FileTreeItem]:
        """Get file tree item by ID"""
        pass
    
    @abstractmethod
    async def assign_tag(self, item_id: str, tag_id: str) -> bool:
        """Assign tag to file tree item"""
        pass
    
    @abstractmethod
    async def unassign_tag(self, item_id: str, tag_id: str) -> bool:
        """Unassign tag from file tree item"""
        pass