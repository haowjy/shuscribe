"""
Workspace Service - Business logic for workspace and story arc management.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from src.database.interfaces.workspace_repository import IWorkspaceRepository
from src.schemas.db.workspace import (
    Workspace, WorkspaceCreate, WorkspaceUpdate, Arc
)


class WorkspaceService:
    """Service layer for workspace management with business logic."""
    
    def __init__(self, workspace_repository: IWorkspaceRepository):
        self.workspace_repository = workspace_repository
    
    # Workspace Management
    async def create_workspace(self, workspace_data: WorkspaceCreate) -> Workspace:
        """Create a new workspace with validation."""
        # Check for name conflicts within user's workspaces
        existing_workspaces = await self.workspace_repository.get_workspaces_by_user(
            workspace_data.owner_id
        )
        if any(w.name.lower() == workspace_data.name.lower() for w in existing_workspaces):
            raise ValueError(f"Workspace '{workspace_data.name}' already exists for this user")
        
        # Validate arcs if provided
        if workspace_data.arcs:
            self._validate_arcs(workspace_data.arcs)
        
        return await self.workspace_repository.create_workspace(workspace_data)
    
    async def get_workspace(self, workspace_id: UUID) -> Optional[Workspace]:
        """Get workspace by ID."""
        return await self.workspace_repository.get_workspace(workspace_id)
    
    async def update_workspace(self, workspace_id: UUID, workspace_data: WorkspaceUpdate) -> Workspace:
        """Update workspace with validation."""
        # Verify workspace exists
        existing_workspace = await self.workspace_repository.get_workspace(workspace_id)
        if not existing_workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        # Check for name conflicts if name is being changed
        if workspace_data.name and workspace_data.name != existing_workspace.name:
            user_workspaces = await self.workspace_repository.get_workspaces_by_user(
                existing_workspace.owner_id
            )
            if any(w.name.lower() == workspace_data.name.lower() and w.id != workspace_id 
                   for w in user_workspaces):
                raise ValueError(f"Workspace '{workspace_data.name}' already exists for this user")
        
        # Validate arcs if being updated
        if workspace_data.arcs is not None:
            self._validate_arcs(workspace_data.arcs)
        
        return await self.workspace_repository.update_workspace(workspace_id, workspace_data)
    
    async def delete_workspace(self, workspace_id: UUID) -> bool:
        """Delete workspace and cleanup related data."""
        # Verify workspace exists
        existing_workspace = await self.workspace_repository.get_workspace(workspace_id)
        if not existing_workspace:
            return False
        
        # TODO: Add cleanup logic for stories, wiki articles, etc.
        # This should coordinate with other services to cleanup workspace data
        
        return await self.workspace_repository.delete_workspace(workspace_id)
    
    async def get_workspaces_by_user(self, user_id: UUID) -> List[Workspace]:
        """Get all workspaces for a user."""
        return await self.workspace_repository.get_workspaces_by_user(user_id)
    
    async def get_workspace_by_name(self, user_id: UUID, name: str) -> Optional[Workspace]:
        """Get workspace by name within user's workspaces."""
        return await self.workspace_repository.get_workspace_by_name(name, user_id)
    
    async def get_workspaces_by_status(
        self, status: str, user_id: Optional[UUID] = None
    ) -> List[Workspace]:
        """Get workspaces filtered by status, optionally for a specific user."""
        return await self.workspace_repository.get_workspaces_by_status(status, user_id)
    
    # Arc Management (through workspace updates)
    async def add_arc_to_workspace(self, workspace_id: UUID, arc: Arc) -> Workspace:
        """Add a new arc to a workspace."""
        # Get current workspace
        workspace = await self.workspace_repository.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        # Validate new arc doesn't overlap with existing ones
        current_arcs = workspace.arcs
        all_arcs = current_arcs + [arc]
        self._validate_arcs(all_arcs)
        
        # Update workspace with new arc
        workspace_update = WorkspaceUpdate(arcs=all_arcs)
        return await self.workspace_repository.update_workspace(workspace_id, workspace_update)
    
    async def update_arc_in_workspace(self, workspace_id: UUID, arc_name: str, updated_arc: Arc) -> Workspace:
        """Update an arc within a workspace."""
        # Get current workspace
        workspace = await self.workspace_repository.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        # Find and update the arc
        updated_arcs = []
        arc_found = False
        
        for arc in workspace.arcs:
            if arc.name == arc_name:
                updated_arcs.append(updated_arc)
                arc_found = True
            else:
                updated_arcs.append(arc)
        
        if not arc_found:
            raise ValueError(f"Arc '{arc_name}' not found in workspace")
        
        # Validate updated arcs
        self._validate_arcs(updated_arcs)
        
        # Update workspace
        workspace_update = WorkspaceUpdate(arcs=updated_arcs)
        return await self.workspace_repository.update_workspace(workspace_id, workspace_update)
    
    async def remove_arc_from_workspace(self, workspace_id: UUID, arc_name: str) -> Workspace:
        """Remove an arc from a workspace."""
        # Get current workspace
        workspace = await self.workspace_repository.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        # Remove the arc
        updated_arcs = [arc for arc in workspace.arcs if arc.name != arc_name]
        
        if len(updated_arcs) == len(workspace.arcs):
            raise ValueError(f"Arc '{arc_name}' not found in workspace")
        
        # Update workspace
        workspace_update = WorkspaceUpdate(arcs=updated_arcs)
        return await self.workspace_repository.update_workspace(workspace_id, workspace_update)
    
    # Arc Queries
    async def get_arcs_by_workspace(self, workspace_id: UUID) -> List[Arc]:
        """Get all arcs for a workspace."""
        workspace = await self.workspace_repository.get_workspace(workspace_id)
        if not workspace:
            return []
        
        return workspace.arcs
    
    async def get_arcs_by_chapter_range(
        self, workspace_id: UUID, start_chapter: int, end_chapter: int
    ) -> List[Arc]:
        """Get arcs that overlap with the given chapter range."""
        workspace = await self.workspace_repository.get_workspace(workspace_id)
        if not workspace:
            return []
        
        overlapping_arcs = []
        for arc in workspace.arcs:
            # Check if arc overlaps with the range
            if (arc.start_chapter <= end_chapter and arc.end_chapter >= start_chapter):
                overlapping_arcs.append(arc)
        
        return overlapping_arcs
    
    async def get_arc_by_chapter(self, workspace_id: UUID, chapter_number: int) -> Optional[Arc]:
        """Get the arc containing a specific chapter."""
        workspace = await self.workspace_repository.get_workspace(workspace_id)
        if not workspace:
            return None
        
        return workspace.get_arc_by_chapter(chapter_number)
    
    async def get_arcs_through_chapter(self, workspace_id: UUID, chapter_number: int) -> List[Arc]:
        """Get all arcs that are complete through the given chapter."""
        workspace = await self.workspace_repository.get_workspace(workspace_id)
        if not workspace:
            return []
        
        complete_arcs = []
        for arc in workspace.arcs:
            if arc.end_chapter <= chapter_number:
                complete_arcs.append(arc)
        
        return complete_arcs
    
    # Processing State Management
    async def update_processing_state(self, workspace_id: UUID, state_data: Dict[str, Any]) -> Workspace:
        """Update workspace processing state."""
        return await self.workspace_repository.update_processing_state(workspace_id, state_data)
    
    async def update_last_processed_chapter(self, workspace_id: UUID, chapter_number: int) -> Workspace:
        """Update the last processed chapter number."""
        return await self.workspace_repository.update_last_processed_chapter(workspace_id, chapter_number)
    
    async def set_workspace_status(self, workspace_id: UUID, status: str) -> Workspace:
        """Set workspace status."""
        valid_statuses = ["active", "processing", "archived", "error"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")
        
        return await self.workspace_repository.update_status(workspace_id, status)
    
    async def update_status(self, workspace_id: UUID, status: str) -> Workspace:
        """Alias for set_workspace_status for consistency."""
        return await self.set_workspace_status(workspace_id, status)
    
    # Helper Methods
    def _validate_arcs(self, arcs: List[Arc]) -> None:
        """Validate that arcs don't overlap and are properly ordered."""
        if not arcs:
            return
        
        # Sort arcs by start chapter
        sorted_arcs = sorted(arcs, key=lambda a: a.start_chapter)
        
        # Check for overlaps and gaps
        for i in range(len(sorted_arcs)):
            arc = sorted_arcs[i]
            
            # Validate individual arc
            if arc.start_chapter > arc.end_chapter:
                raise ValueError(f"Arc '{arc.name}' has invalid chapter range: {arc.start_chapter}-{arc.end_chapter}")
            
            if arc.start_chapter < 1:
                raise ValueError(f"Arc '{arc.name}' cannot start before chapter 1")
            
            # Check for overlaps with next arc
            if i < len(sorted_arcs) - 1:
                next_arc = sorted_arcs[i + 1]
                if arc.end_chapter >= next_arc.start_chapter:
                    raise ValueError(
                        f"Arc '{arc.name}' (chapters {arc.start_chapter}-{arc.end_chapter}) "
                        f"overlaps with arc '{next_arc.name}' (chapters {next_arc.start_chapter}-{next_arc.end_chapter})"
                    )
    
    async def get_workspace_statistics(self, workspace_id: UUID) -> Dict[str, Any]:
        """Get statistics for a workspace."""
        workspace = await self.workspace_repository.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        total_chapters = workspace.total_chapters
        total_arcs = len(workspace.arcs)
        
        return {
            "workspace_id": workspace_id,
            "name": workspace.name,
            "total_arcs": total_arcs,
            "total_chapters": total_chapters,
            "arcs": [
                {
                    "name": arc.name,
                    "start_chapter": arc.start_chapter,
                    "end_chapter": arc.end_chapter,
                    "chapter_count": arc.end_chapter - arc.start_chapter + 1,
                    "description": arc.description
                }
                for arc in workspace.arcs
            ],
            "created_at": workspace.created_at,
            "updated_at": workspace.updated_at
        }