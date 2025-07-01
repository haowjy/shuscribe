"""
File-Based Workspace Repository Implementation

Stores workspace metadata in the .shuscribe directory.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from src.database.interfaces.workspace import IWorkspaceRepository
from src.schemas.db.workspace import Workspace, Arc, WorkspaceCreate, WorkspaceUpdate
from src.database.file.utils import FileManager, ensure_workspace_structure


class FileWorkspaceRepository(IWorkspaceRepository):
    """File-based workspace repository"""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.file_manager = FileManager(workspace_path)
        
        # Ensure workspace structure exists
        ensure_workspace_structure(workspace_path)
        
        # File paths
        structure = self.file_manager.get_workspace_structure()
        self.workspace_file = structure['system'] / "workspace.json"
        
        # Workspace ID for this directory
        self._workspace_id = self._get_or_create_workspace_id()
    
    def _get_or_create_workspace_id(self) -> UUID:
        """Get or create workspace ID"""
        workspace_data = self.file_manager.read_json_file(self.workspace_file, {})
        
        if "id" in workspace_data:
            try:
                return UUID(workspace_data["id"])
            except ValueError:
                pass
        
        # Create new workspace ID
        workspace_id = uuid4() 
        workspace_data["id"] = str(workspace_id)
        workspace_data["created_at"] = datetime.now().isoformat()
        self.file_manager.write_json_file(self.workspace_file, workspace_data)
        return workspace_id
    
    def _load_workspace_data(self) -> dict:
        """Load workspace data from file"""
        return self.file_manager.read_json_file(self.workspace_file, {
            "id": str(self._workspace_id),
            "name": self.workspace_path.name,
            "description": "",
            "arcs": [],
            "settings": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        })
    
    def _save_workspace_data(self, data: dict) -> None:
        """Save workspace data to file"""
        data["updated_at"] = datetime.now().isoformat()
        self.file_manager.write_json_file(self.workspace_file, data)

    async def get(self, id: UUID) -> Optional[Workspace]:
        """Get workspace by ID"""
        if id != self._workspace_id:
            return None
        
        data = self._load_workspace_data()
        
        # Convert arc data to Arc objects
        arcs = []
        for arc_data in data.get("arcs", []):
            arcs.append(Arc(
                name=arc_data["name"],
                description=arc_data.get("description"),
                start_chapter=arc_data["start_chapter"],
                end_chapter=arc_data["end_chapter"],
                metadata=arc_data.get("metadata", {})
            ))
        
        return Workspace(
            id=self._workspace_id,
            name=data.get("name", self.workspace_path.name),
            description=data.get("description", ""),
            owner_id=UUID(data["owner_id"]) if "owner_id" in data else uuid4(),  # Default owner
            arcs=arcs,
            settings=data.get("settings", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )

    async def get_by_owner(self, owner_id: UUID) -> List[Workspace]:
        """Get workspaces by owner"""
        workspace = await self.get(self._workspace_id)
        if workspace and workspace.owner_id == owner_id:
            return [workspace]
        return []

    async def get_multi(self, *, offset: int = 0, limit: int = 100) -> List[Workspace]:
        """Get multiple workspaces (local mode returns single workspace)"""
        if offset == 0:
            workspace = await self.get(self._workspace_id)
            return [workspace] if workspace else []
        return []

    async def create(self, workspace_data: WorkspaceCreate) -> Workspace:
        """Create workspace (updates current workspace)"""
        data = self._load_workspace_data()
        
        # Convert arcs to dict format for storage
        arcs_data = []
        for arc in workspace_data.arcs:
            arcs_data.append({
                "name": arc.name,
                "description": arc.description,
                "start_chapter": arc.start_chapter,
                "end_chapter": arc.end_chapter,
                "metadata": arc.metadata
            })
        
        # Update with new data
        data.update({
            "name": workspace_data.name,
            "description": workspace_data.description or "",
            "owner_id": str(workspace_data.owner_id),
            "arcs": arcs_data,
            "settings": workspace_data.settings,
            "updated_at": datetime.now().isoformat()
        })
        
        self._save_workspace_data(data)
        result = await self.get(self._workspace_id)
        assert result is not None
        return result

    async def update(self, workspace_id: UUID, workspace_data: WorkspaceUpdate) -> Workspace:
        """Update workspace"""
        if workspace_id != self._workspace_id:
            raise ValueError("Workspace not found")
        
        data = self._load_workspace_data()
        
        # Update fields
        update_dict = workspace_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if field not in ['id', 'created_at']:
                if field == 'arcs' and value is not None:
                    # Convert arcs to dict format
                    arcs_data = []
                    for arc in value:
                        arcs_data.append({
                            "name": arc.name,
                            "description": arc.description,
                            "start_chapter": arc.start_chapter,
                            "end_chapter": arc.end_chapter,
                            "metadata": arc.metadata
                        })
                    data[field] = arcs_data
                else:
                    data[field] = value
        
        self._save_workspace_data(data)
        result = await self.get(self._workspace_id)
        assert result is not None
        return result

    async def delete(self, workspace_id: UUID) -> bool:
        """Delete workspace (resets to default)"""
        if workspace_id != self._workspace_id:
            return False
        
        # Reset workspace to default state
        self.file_manager.delete_file(self.workspace_file)
        
        # Recreate workspace ID
        self._workspace_id = self._get_or_create_workspace_id()
        return True 