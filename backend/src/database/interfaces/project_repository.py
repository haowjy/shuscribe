# backend/src/database/interfaces/project_repository.py
"""
Project repository interface
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from src.database.models import Project


class ProjectRepository(ABC):
    """Abstract project repository interface"""
    
    @abstractmethod
    async def get_by_id(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        pass
    
    @abstractmethod
    async def create(self, project_data: Dict[str, Any]) -> Project:
        """Create new project"""
        pass
    
    @abstractmethod
    async def update(self, project_id: str, updates: Dict[str, Any]) -> Optional[Project]:
        """Update project"""
        pass
    
    @abstractmethod
    async def delete(self, project_id: str) -> bool:
        """Delete project"""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[Project]:
        """List all projects"""
        pass
    
    @abstractmethod
    async def list_by_user(self, user_id: str) -> List[Project]:
        """List projects owned by a specific user"""
        pass
    
    @abstractmethod
    async def get_by_user_and_id(self, user_id: str, project_id: str) -> Optional[Project]:
        """Get project by ID with user ownership validation"""
        pass