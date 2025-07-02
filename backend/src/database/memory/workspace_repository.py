"""Memory-based workspace repository implementation for testing and development."""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import UTC, datetime

from src.database.interfaces.workspace_repository import IWorkspaceRepository
from src.schemas.db.workspace import Workspace, WorkspaceCreate, WorkspaceUpdate, Arc


class MemoryWorkspaceRepository(IWorkspaceRepository):
    """In-memory implementation of workspace repository for testing."""
    
    def __init__(self):
        self._workspaces: Dict[UUID, Workspace] = {}
        self._arcs: Dict[UUID, Arc] = {}  # arc_id -> Arc
        self._workspace_arcs: Dict[UUID, List[UUID]] = {}  # workspace_id -> [arc_ids]
    
    # Workspace CRUD
    async def create_workspace(self, workspace_data: WorkspaceCreate) -> Workspace:
        """Create a new workspace"""
        workspace_id = uuid4()
        now = datetime.now(UTC)
        
        workspace = Workspace(
            id=workspace_id,
            owner_id=workspace_data.owner_id,
            name=workspace_data.name,
            description=workspace_data.description,
            arcs=workspace_data.arcs,
            settings=workspace_data.settings,
            created_at=now,
            updated_at=now
        )
        
        self._workspaces[workspace_id] = workspace
        
        # Store arcs separately for efficient querying
        arc_ids = []
        for arc_data in workspace_data.arcs:
            arc_id = uuid4()
            # Convert Arc to dict and add ID for storage
            arc = Arc(**arc_data.model_dump())
            self._arcs[arc_id] = arc
            arc_ids.append(arc_id)
        
        self._workspace_arcs[workspace_id] = arc_ids
        
        return workspace
    
    async def get_workspace(self, workspace_id: UUID) -> Optional[Workspace]:
        """Retrieve a single workspace by ID"""
        workspace = self._workspaces.get(workspace_id)
        if workspace:
            # Rebuild arcs from separate storage
            arc_ids = self._workspace_arcs.get(workspace_id, [])
            arcs = [self._arcs[arc_id] for arc_id in arc_ids if arc_id in self._arcs]
            workspace = workspace.model_copy(update={'arcs': arcs})
        return workspace
    
    async def update_workspace(self, workspace_id: UUID, workspace_data: WorkspaceUpdate) -> Workspace:
        """Update an existing workspace"""
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        update_dict = workspace_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        # Handle arcs update separately
        if 'arcs' in update_dict:
            # Clear old arcs
            old_arc_ids = self._workspace_arcs.get(workspace_id, [])
            for arc_id in old_arc_ids:
                self._arcs.pop(arc_id, None)
            
            # Add new arcs
            new_arc_ids = []
            for arc_data in update_dict['arcs']:
                arc_id = uuid4()
                if isinstance(arc_data, Arc):
                    arc = arc_data
                else:
                    arc = Arc(**arc_data)
                self._arcs[arc_id] = arc
                new_arc_ids.append(arc_id)
            
            self._workspace_arcs[workspace_id] = new_arc_ids
        
        updated_workspace = workspace.model_copy(update=update_dict)
        self._workspaces[workspace_id] = updated_workspace
        
        rebuilt_workspace = await self.get_workspace(workspace_id)  # Return with rebuilt arcs
        if not rebuilt_workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        return rebuilt_workspace
    
    async def delete_workspace(self, workspace_id: UUID) -> bool:
        """Delete a workspace"""
        if workspace_id in self._workspaces:
            # Clean up associated arcs
            arc_ids = self._workspace_arcs.get(workspace_id, [])
            for arc_id in arc_ids:
                self._arcs.pop(arc_id, None)
            self._workspace_arcs.pop(workspace_id, None)
            
            del self._workspaces[workspace_id]
            return True
        return False
    
    # Simple Workspace Queries
    async def get_workspaces_by_user(self, user_id: UUID) -> List[Workspace]:
        """Get all workspaces owned by a user"""
        user_workspaces = []
        for workspace in self._workspaces.values():
            if workspace.owner_id == user_id:
                # Rebuild with arcs
                rebuilt_workspace = await self.get_workspace(workspace.id)
                if rebuilt_workspace:
                    user_workspaces.append(rebuilt_workspace)
        return user_workspaces
    
    async def get_workspace_by_name(self, name: str, user_id: UUID) -> Optional[Workspace]:
        """Get workspace by name for a specific user"""
        for workspace in self._workspaces.values():
            if workspace.name == name and workspace.owner_id == user_id:
                return await self.get_workspace(workspace.id)
        return None
    
    async def get_workspaces_by_status(
        self, status: str, user_id: Optional[UUID] = None
    ) -> List[Workspace]:
        """Get workspaces filtered by status"""
        # Note: This implementation assumes status is stored in settings
        filtered_workspaces = []
        for workspace in self._workspaces.values():
            workspace_status = workspace.settings.get('status', 'active')
            if workspace_status == status:
                if user_id is None or workspace.owner_id == user_id:
                    rebuilt_workspace = await self.get_workspace(workspace.id)
                    if rebuilt_workspace:
                        filtered_workspaces.append(rebuilt_workspace)
        return filtered_workspaces
    
    async def get_workspaces(
        self, 
        user_id: Optional[UUID] = None, 
        offset: int = 0, 
        limit: int = 100
    ) -> List[Workspace]:
        """Retrieve multiple workspaces with optional user filtering"""
        workspaces = []
        for workspace in self._workspaces.values():
            if user_id is None or workspace.owner_id == user_id:
                rebuilt_workspace = await self.get_workspace(workspace.id)
                if rebuilt_workspace:
                    workspaces.append(rebuilt_workspace)
        
        # Sort by created_at for consistent pagination
        workspaces.sort(key=lambda w: w.created_at)
        return workspaces[offset:offset + limit]
    
    # Arc CRUD
    async def create_arc(self, arc_data: Dict[str, Any]) -> Arc:
        """Create a new arc for the workspace"""
        arc_id = uuid4()
        
        # Extract workspace_id if present
        workspace_id = arc_data.get('workspace_id')
        if workspace_id:
            arc_data = {k: v for k, v in arc_data.items() if k != 'workspace_id'}
        
        arc = Arc(**arc_data)
        self._arcs[arc_id] = arc
        
        # Associate with workspace if provided
        if workspace_id:
            if workspace_id not in self._workspace_arcs:
                self._workspace_arcs[workspace_id] = []
            self._workspace_arcs[workspace_id].append(arc_id)
        
        return arc
    
    async def get_arc(self, arc_id: UUID) -> Optional[Arc]:
        """Get a specific arc by ID"""
        return self._arcs.get(arc_id)
    
    async def update_arc(self, arc_id: UUID, arc_data: Dict[str, Any]) -> Arc:
        """Update an existing arc"""
        arc = self._arcs.get(arc_id)
        if not arc:
            raise ValueError(f"Arc {arc_id} not found")
        
        # Remove fields that shouldn't be updated directly
        arc_data = {k: v for k, v in arc_data.items() if k != 'workspace_id'}
        
        updated_arc = arc.model_copy(update=arc_data)
        self._arcs[arc_id] = updated_arc
        return updated_arc
    
    async def delete_arc(self, arc_id: UUID) -> bool:
        """Delete an arc"""
        if arc_id in self._arcs:
            # Remove from workspace associations
            for workspace_id, arc_ids in self._workspace_arcs.items():
                if arc_id in arc_ids:
                    arc_ids.remove(arc_id)
            
            del self._arcs[arc_id]
            return True
        return False
    
    # Simple Arc Queries
    async def get_arcs_by_workspace(self, workspace_id: UUID) -> List[Arc]:
        """Get all arcs for a workspace"""
        arc_ids = self._workspace_arcs.get(workspace_id, [])
        return [self._arcs[arc_id] for arc_id in arc_ids if arc_id in self._arcs]
    
    async def get_arcs_by_chapter_range(
        self, workspace_id: UUID, start_chapter: int, end_chapter: int
    ) -> List[Arc]:
        """Get arcs that overlap with a chapter range"""
        workspace_arcs = await self.get_arcs_by_workspace(workspace_id)
        overlapping_arcs = []
        
        for arc in workspace_arcs:
            # Check if arc overlaps with the specified range
            if (arc.start_chapter <= end_chapter and arc.end_chapter >= start_chapter):
                overlapping_arcs.append(arc)
        
        return overlapping_arcs
    
    # Processing State Operations (Simple Updates)
    async def update_processing_state(
        self, workspace_id: UUID, state_data: Dict[str, Any]
    ) -> Workspace:
        """Update the processing state of a workspace"""
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        # Merge state_data into settings
        new_settings = workspace.settings.copy()
        new_settings.update(state_data)
        
        updated_workspace = workspace.model_copy(update={
            'settings': new_settings,
            'updated_at': datetime.now(UTC)
        })
        
        self._workspaces[workspace_id] = updated_workspace
        rebuilt_workspace = await self.get_workspace(workspace_id)
        if not rebuilt_workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        return rebuilt_workspace
    
    async def update_last_processed_chapter(
        self, workspace_id: UUID, chapter_number: int
    ) -> Workspace:
        """Update the last processed chapter number"""
        return await self.update_processing_state(
            workspace_id, 
            {'last_processed_chapter': chapter_number}
        )
    
    async def update_status(self, workspace_id: UUID, status: str) -> Workspace:
        """Set workspace status (active, processing, archived, error)"""
        return await self.update_processing_state(
            workspace_id, 
            {'status': status}
        )