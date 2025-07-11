# backend/src/api/v1/endpoints/projects.py
"""
Project API endpoints matching frontend expectations
"""
import logging
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.database.factory import get_repositories
from src.database.models import Project, FileTreeItem

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Response Models (matching frontend API types)
# ============================================================================

class ProjectCollaborator(BaseModel):
    """Project collaborator info"""
    user_id: str
    role: str  # 'owner' | 'editor' | 'viewer'
    name: str
    avatar: str | None = None


class ProjectSettings(BaseModel):
    """Project settings"""
    auto_save_interval: int = 30000  # 30 seconds
    word_count_target: int = 0
    backup_enabled: bool = True


class ProjectDetails(BaseModel):
    """Complete project details matching frontend ProjectDetails interface"""
    id: str
    title: str
    description: str
    word_count: int
    document_count: int
    created_at: str
    updated_at: str
    tags: List[str]
    collaborators: List[ProjectCollaborator]
    settings: ProjectSettings


class FileTreeItemResponse(BaseModel):
    """File tree item response matching frontend FileTreeItem interface"""
    id: str
    name: str
    type: str  # 'file' | 'folder'
    path: str
    parent_id: str | None = None
    children: List["FileTreeItemResponse"] | None = None
    
    # File-specific properties
    document_id: str | None = None
    icon: str | None = None
    tags: List[str] = []
    word_count: int | None = None
    
    # Timestamps
    created_at: str
    updated_at: str


class FileTreeMetadata(BaseModel):
    """File tree metadata"""
    total_files: int
    total_folders: int
    last_updated: str


class FileTreeResponse(BaseModel):
    """File tree response matching frontend FileTreeResponse interface"""
    file_tree: List[FileTreeItemResponse]
    metadata: FileTreeMetadata


# ============================================================================
# Helper Functions
# ============================================================================

def project_to_response(project: Project) -> ProjectDetails:
    """Convert Project model to ProjectDetails response"""
    # Parse collaborators from JSON
    collaborators = []
    for collab in project.collaborators:
        collaborators.append(ProjectCollaborator(
            user_id=collab.get("user_id", ""),
            role=collab.get("role", "viewer"),
            name=collab.get("name", ""),
            avatar=collab.get("avatar"),
        ))
    
    # Parse settings from JSON with defaults
    settings_data = project.settings or {}
    settings = ProjectSettings(
        auto_save_interval=settings_data.get("auto_save_interval", 30000),
        word_count_target=settings_data.get("word_count_target", 0),
        backup_enabled=settings_data.get("backup_enabled", True),
    )
    
    return ProjectDetails(
        id=project.id,
        title=project.title,
        description=project.description,
        word_count=project.word_count,
        document_count=project.document_count,
        created_at=project.created_at.isoformat() if hasattr(project.created_at, 'isoformat') else str(project.created_at),
        updated_at=project.updated_at.isoformat() if hasattr(project.updated_at, 'isoformat') else str(project.updated_at),
        tags=project.tags,
        collaborators=collaborators,
        settings=settings,
    )


def file_tree_item_to_response(item: FileTreeItem, children: List["FileTreeItemResponse"] = None) -> FileTreeItemResponse:
    """Convert FileTreeItem model to FileTreeItemResponse"""
    return FileTreeItemResponse(
        id=item.id,
        name=item.name,
        type=item.type,
        path=item.path,
        parent_id=item.parent_id,
        children=children if children else None,
        document_id=item.document_id,
        icon=item.icon,
        tags=item.tags,
        word_count=item.word_count,
        created_at=item.created_at.isoformat() if hasattr(item.created_at, 'isoformat') else str(item.created_at),
        updated_at=item.updated_at.isoformat() if hasattr(item.updated_at, 'isoformat') else str(item.updated_at),
    )


def build_file_tree_hierarchy(items: List[FileTreeItem]) -> List[FileTreeItemResponse]:
    """Build hierarchical file tree from flat list of items"""
    # Group items by parent_id
    items_by_parent: Dict[str | None, List[FileTreeItem]] = {}
    for item in items:
        parent_id = item.parent_id
        if parent_id not in items_by_parent:
            items_by_parent[parent_id] = []
        items_by_parent[parent_id].append(item)
    
    def build_children(parent_id: str | None) -> List[FileTreeItemResponse]:
        """Recursively build children for a parent"""
        if parent_id not in items_by_parent:
            return []
        
        children_responses = []
        for item in items_by_parent[parent_id]:
            children = build_children(item.id)
            # Pass children as None if empty list, or the actual list if not empty
            children_to_pass = children if children else None
            children_responses.append(file_tree_item_to_response(item, children_to_pass))
        
        return children_responses
    
    # Build tree starting from root items (parent_id = None)
    return build_children(None)


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/{project_id}", response_model=ProjectDetails)
async def get_project(project_id: str) -> ProjectDetails:
    """
    Get project details by ID
    
    Matches frontend expectation: GET /projects/{projectId}
    """
    try:
        repos = get_repositories()
        project = await repos.project.get_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        logger.info(f"Retrieved project: {project.title} (ID: {project_id})")
        return project_to_response(project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{project_id}/file-tree", response_model=FileTreeResponse)
async def get_project_file_tree(project_id: str) -> FileTreeResponse:
    """
    Get file tree for a project
    
    Matches frontend expectation: GET /projects/{projectId}/file-tree
    """
    try:
        repos = get_repositories()
        
        # Verify project exists
        project = await repos.project.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Get file tree items
        items = await repos.file_tree.get_by_project_id(project_id)
        
        # Build hierarchical structure
        file_tree = build_file_tree_hierarchy(items)
        
        # Calculate metadata
        total_files = sum(1 for item in items if item.type == "file")
        total_folders = sum(1 for item in items if item.type == "folder")
        last_updated_obj = max(
            (item.updated_at for item in items),
            default=project.updated_at
        )
        last_updated = last_updated_obj.isoformat() if hasattr(last_updated_obj, 'isoformat') else str(last_updated_obj)
        
        metadata = FileTreeMetadata(
            total_files=total_files,
            total_folders=total_folders,
            last_updated=last_updated,
        )
        
        logger.info(f"Retrieved file tree for project {project_id}: {total_files} files, {total_folders} folders")
        
        return FileTreeResponse(
            file_tree=file_tree,
            metadata=metadata,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving file tree for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )