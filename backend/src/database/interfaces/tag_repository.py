# backend/src/database/interfaces/tag_repository.py
"""
Tag repository interface
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from .models import Tag


class TagRepository(ABC):
    """Abstract tag repository interface"""
    
    @abstractmethod
    async def get_by_id(self, tag_id: str) -> Optional[Tag]:
        """Get tag by ID"""
        pass
    
    @abstractmethod
    async def get_global_tags(self, include_archived: bool = False) -> List[Tag]:
        """Get all global tags"""
        pass
    
    @abstractmethod
    async def get_user_tags(self, user_id: str, include_archived: bool = False) -> List[Tag]:
        """Get all private tags for a user"""
        pass
    
    @abstractmethod
    async def get_by_project_id(self, project_id: str, include_archived: bool = False) -> List[Tag]:
        """Get all tags for a project"""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str, user_id: Optional[str] = None) -> Optional[Tag]:
        """Get tag by name (global if user_id is None, private if user_id provided)"""
        pass
    
    @abstractmethod
    async def create(self, tag_data: Dict[str, Any]) -> Tag:
        """Create new tag"""
        pass
    
    @abstractmethod
    async def update(self, tag_id: str, updates: Dict[str, Any]) -> Optional[Tag]:
        """Update tag"""
        pass
    
    @abstractmethod
    async def delete(self, tag_id: str) -> bool:
        """Delete tag"""
        pass
    
    @abstractmethod
    async def archive(self, tag_id: str) -> Optional[Tag]:
        """Archive tag (soft delete)"""
        pass
    
    @abstractmethod
    async def unarchive(self, tag_id: str) -> Optional[Tag]:
        """Unarchive tag"""
        pass
    
    @abstractmethod
    async def increment_usage(self, tag_id: str) -> Optional[Tag]:
        """Increment usage count for tag"""
        pass
    
    @abstractmethod
    async def decrement_usage(self, tag_id: str) -> Optional[Tag]:
        """Decrement usage count for tag"""
        pass
    
    @abstractmethod
    async def get_by_category(self, category: str, user_id: Optional[str] = None) -> List[Tag]:
        """Get tags by category (global if user_id is None, user's if provided)"""
        pass
    
    @abstractmethod
    async def get_system_tags(self) -> List[Tag]:
        """Get global system tags"""
        pass
    
    @abstractmethod
    async def search_tags(self, query: str, user_id: Optional[str] = None, limit: int = 20) -> List[Tag]:
        """Search tags by name (global and user's if user_id provided)"""
        pass
    
    # Tag forking and precedence methods
    
    @abstractmethod
    async def get_global_tag_by_name(self, name: str) -> Optional[Tag]:
        """Get global tag by name"""
        pass
    
    @abstractmethod
    async def get_project_tag_by_name(self, project_id: str, name: str) -> Optional[Tag]:
        """Get project-specific tag by name"""
        pass
    
    @abstractmethod
    async def get_tag_by_name_with_precedence(self, project_id: str, name: str) -> Optional[Tag]:
        """Get tag by name with project → global precedence"""
        pass
    
    @abstractmethod
    async def get_all_usable_tags(self, project_id: str, include_archived: bool = False) -> List[Tag]:
        """Get all tags available to project (project-specific + global) with precedence deduplication"""
        pass
    
    @abstractmethod
    async def fork_global_tag(self, project_id: str, global_tag_id: str, customizations: Dict[str, Any]) -> Tag:
        """Create project-specific copy of global tag with customizations"""
        pass