from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.schemas.db.workspace import Workspace, WorkspaceCreate, WorkspaceUpdate, Arc


class IWorkspaceRepository(ABC):
    """Abstract interface for workspace repository - pure CRUD + simple queries"""

    # Workspace CRUD
    @abstractmethod
    async def create_workspace(self, workspace_data: WorkspaceCreate) -> Workspace:
        """Create a new workspace"""
        pass

    @abstractmethod
    async def get_workspace(self, workspace_id: UUID) -> Optional[Workspace]:
        """Retrieve a single workspace by ID"""
        pass

    @abstractmethod
    async def update_workspace(self, workspace_id: UUID, workspace_data: WorkspaceUpdate) -> Workspace:
        """Update an existing workspace"""
        pass

    @abstractmethod
    async def delete_workspace(self, workspace_id: UUID) -> bool:
        """Delete a workspace"""
        pass

    # Simple Workspace Queries
    @abstractmethod
    async def get_workspaces_by_user(self, user_id: UUID) -> List[Workspace]:
        """Get all workspaces owned by a user"""
        pass

    @abstractmethod
    async def get_workspace_by_name(self, name: str, user_id: UUID) -> Optional[Workspace]:
        """Get workspace by name for a specific user"""
        pass

    @abstractmethod
    async def get_workspaces_by_status(
        self, status: str, user_id: Optional[UUID] = None
    ) -> List[Workspace]:
        """Get workspaces filtered by status"""
        pass

    @abstractmethod
    async def get_workspaces(
        self, 
        user_id: Optional[UUID] = None, 
        offset: int = 0, 
        limit: int = 100
    ) -> List[Workspace]:
        """Retrieve multiple workspaces with optional user filtering"""
        pass

    # Arc CRUD
    @abstractmethod
    async def create_arc(self, arc_data: Dict[str, Any]) -> Arc:
        """Create a new arc for the workspace"""
        pass

    @abstractmethod
    async def get_arc(self, arc_id: UUID) -> Optional[Arc]:
        """Get a specific arc by ID"""
        pass

    @abstractmethod
    async def update_arc(self, arc_id: UUID, arc_data: Dict[str, Any]) -> Arc:
        """Update an existing arc"""
        pass

    @abstractmethod
    async def delete_arc(self, arc_id: UUID) -> bool:
        """Delete an arc"""
        pass

    # Simple Arc Queries
    @abstractmethod
    async def get_arcs_by_workspace(self, workspace_id: UUID) -> List[Arc]:
        """Get all arcs for a workspace"""
        pass

    @abstractmethod
    async def get_arcs_by_chapter_range(
        self, workspace_id: UUID, start_chapter: int, end_chapter: int
    ) -> List[Arc]:
        """Get arcs that overlap with a chapter range"""
        pass

    # Processing State Operations (Simple Updates)
    @abstractmethod
    async def update_processing_state(
        self, workspace_id: UUID, state_data: Dict[str, Any]
    ) -> Workspace:
        """Update the processing state of a workspace"""
        pass

    @abstractmethod
    async def update_last_processed_chapter(
        self, workspace_id: UUID, chapter_number: int
    ) -> Workspace:
        """Update the last processed chapter number"""
        pass

    @abstractmethod
    async def update_status(self, workspace_id: UUID, status: str) -> Workspace:
        """Set workspace status (active, processing, archived, error)"""
        pass