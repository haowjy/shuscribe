"""
Workspace Repository Interface

Abstract interface for workspace operations and arc management.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.database.models.workspace import Workspace, WorkspaceCreate, WorkspaceUpdate


class IWorkspaceRepository(ABC):
    """Abstract interface for workspace repository"""

    @abstractmethod
    async def get(self, id: UUID) -> Optional[Workspace]:
        """Retrieve a workspace by ID"""
        pass

    @abstractmethod
    async def get_by_owner(self, owner_id: UUID) -> List[Workspace]:
        """Get all workspaces owned by a user"""
        pass

    @abstractmethod
    async def get_multi(self, *, offset: int = 0, limit: int = 100) -> List[Workspace]:
        """Retrieve multiple workspaces with pagination"""
        pass

    @abstractmethod
    async def create(self, workspace_data: WorkspaceCreate) -> Workspace:
        """Create a new workspace"""
        pass
    
    @abstractmethod
    async def update(self, workspace_id: UUID, workspace_data: WorkspaceUpdate) -> Workspace:
        """Update an existing workspace"""
        pass

    @abstractmethod
    async def delete(self, workspace_id: UUID) -> bool:
        """Delete a workspace"""
        pass 