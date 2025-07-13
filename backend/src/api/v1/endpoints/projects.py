# backend/src/api/v1/endpoints/projects.py
"""
Project API endpoints matching frontend expectations
"""
import logging
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field

from src.database.factory import get_repositories
from src.database.models import Project, FileTreeItem
from src.schemas.base import ApiResponse
from src.api.dependencies import require_auth, get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Response Models (matching frontend API types)
# ============================================================================

class ProjectCollaborator(BaseModel):
    """Project collaborator info"""
    model_config = {"populate_by_name": True}
    
    user_id: str = Field(alias="userId")
    role: str  # 'owner' | 'editor' | 'viewer'
    name: str
    avatar: str | None = None


class ProjectSettings(BaseModel):
    """Project settings"""
    model_config = {"populate_by_name": True}
    
    auto_save_interval: int = Field(default=30000, alias="autoSaveInterval")  # 30 seconds
    word_count_target: int = Field(default=0, alias="wordCountTarget")
    backup_enabled: bool = Field(default=True, alias="backupEnabled")


class ProjectSummary(BaseModel):
    """Project summary for listing (subset of ProjectDetails)"""
    model_config = {"populate_by_name": True}
    
    id: str
    title: str
    description: str
    word_count: int = Field(alias="wordCount")
    document_count: int = Field(alias="documentCount")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    tags: List[str]
    collaborators: List[ProjectCollaborator]


class ProjectDetails(BaseModel):
    """Complete project details matching frontend ProjectDetails interface"""
    model_config = {"populate_by_name": True}
    
    id: str
    title: str
    description: str
    word_count: int = Field(alias="wordCount")
    document_count: int = Field(alias="documentCount")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    tags: List[str]
    collaborators: List[ProjectCollaborator]
    settings: ProjectSettings


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    model_config = {"populate_by_name": True}
    
    total: int
    limit: int
    offset: int
    has_more: bool = Field(alias="hasMore")
    next_offset: int | None = Field(default=None, alias="nextOffset")


class ProjectListResponse(BaseModel):
    """Paginated list of projects"""
    model_config = {"populate_by_name": True}
    
    data: List[ProjectSummary]
    pagination: PaginationMeta


class CreateProjectRequest(BaseModel):
    """Request model for creating a new project"""
    model_config = {"populate_by_name": True}
    
    title: str
    description: str
    tags: List[str] = []
    settings: ProjectSettings | None = None


class UpdateProjectRequest(BaseModel):
    """Request model for updating a project"""
    model_config = {"populate_by_name": True}
    
    title: str | None = None
    description: str | None = None
    tags: List[str] | None = None
    settings: ProjectSettings | None = None


class FileTreeItemResponse(BaseModel):
    """File tree item response matching frontend FileTreeItem interface"""
    model_config = {"populate_by_name": True}
    
    id: str
    name: str
    type: str  # 'file' | 'folder'
    path: str
    parent_id: str | None = Field(default=None, alias="parentId")
    children: List["FileTreeItemResponse"] | None = None
    
    # File-specific properties
    document_id: str | None = Field(default=None, alias="documentId")
    icon: str | None = None
    tags: List[str] = []
    word_count: int | None = Field(default=None, alias="wordCount")
    
    # Timestamps
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")


class FileTreeMetadata(BaseModel):
    """File tree metadata"""
    model_config = {"populate_by_name": True}
    
    total_files: int = Field(alias="totalFiles")
    total_folders: int = Field(alias="totalFolders")
    last_updated: str = Field(alias="lastUpdated")


class FileTreeResponse(BaseModel):
    """File tree response matching frontend FileTreeResponse interface"""
    model_config = {"populate_by_name": True}
    
    file_tree: List[FileTreeItemResponse] = Field(alias="fileTree")
    metadata: FileTreeMetadata




# ============================================================================
# Helper Functions
# ============================================================================

def project_to_summary(project: Project) -> ProjectSummary:
    """Convert Project model to ProjectSummary response"""
    # Parse collaborators from JSON
    collaborators = []
    for collab in project.collaborators:
        collaborators.append(ProjectCollaborator(
            userId=collab.get("user_id", ""),
            role=collab.get("role", "viewer"),
            name=collab.get("name", ""),
            avatar=collab.get("avatar"),
        ))
    
    return ProjectSummary(
        id=project.id,
        title=project.title,
        description=project.description,
        wordCount=project.word_count,
        documentCount=project.document_count,
        createdAt=project.created_at.isoformat() if hasattr(project.created_at, 'isoformat') else str(project.created_at),
        updatedAt=project.updated_at.isoformat() if hasattr(project.updated_at, 'isoformat') else str(project.updated_at),
        tags=project.tags,
        collaborators=collaborators,
    )


def project_to_response(project: Project) -> ProjectDetails:
    """Convert Project model to ProjectDetails response"""
    # Parse collaborators from JSON
    collaborators = []
    for collab in project.collaborators:
        collaborators.append(ProjectCollaborator(
            userId=collab.get("user_id", ""),
            role=collab.get("role", "viewer"),
            name=collab.get("name", ""),
            avatar=collab.get("avatar"),
        ))
    
    # Parse settings from JSON with defaults
    settings_data = project.settings or {}
    settings = ProjectSettings(
        autoSaveInterval=settings_data.get("auto_save_interval", 30000),
        wordCountTarget=settings_data.get("word_count_target", 0),
        backupEnabled=settings_data.get("backup_enabled", True),
    )
    
    return ProjectDetails(
        id=project.id,
        title=project.title,
        description=project.description,
        wordCount=project.word_count,
        documentCount=project.document_count,
        createdAt=project.created_at.isoformat() if hasattr(project.created_at, 'isoformat') else str(project.created_at),
        updatedAt=project.updated_at.isoformat() if hasattr(project.updated_at, 'isoformat') else str(project.updated_at),
        tags=project.tags,
        collaborators=collaborators,
        settings=settings,
    )


def file_tree_item_to_response(item: FileTreeItem, children: List["FileTreeItemResponse"] | None = None) -> FileTreeItemResponse:
    """Convert FileTreeItem model to FileTreeItemResponse"""
    return FileTreeItemResponse(
        id=item.id,
        name=item.name,
        type=item.type,
        path=item.path,
        parentId=item.parent_id,
        children=children if children else None,
        documentId=item.document_id,
        icon=item.icon,
        tags=item.tags,
        wordCount=item.word_count,
        createdAt=item.created_at.isoformat() if hasattr(item.created_at, 'isoformat') else str(item.created_at),
        updatedAt=item.updated_at.isoformat() if hasattr(item.updated_at, 'isoformat') else str(item.updated_at),
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
            children_responses.append(file_tree_item_to_response(item, children_to_pass or []))
        
        return children_responses
    
    # Build tree starting from root items (parent_id = None)
    return build_children(None)




# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    limit: int = Query(default=20, ge=1, le=100, description="Number of projects to return"),
    offset: int = Query(default=0, ge=0, description="Number of projects to skip"),
    sort: str = Query(default="updated_at", regex="^(title|created_at|updated_at)$", description="Field to sort by"),
    order: str = Query(default="desc", regex="^(asc|desc)$", description="Sort order"),
    user_id: str = Depends(get_current_user_id)
) -> ProjectListResponse:
    """
    List all projects with pagination
    
    Matches frontend expectation: GET /projects
    Returns ProjectListResponse with pagination metadata
    """
    try:
        repos = get_repositories()
        all_projects = await repos.project.list_all()
        
        # Apply sorting
        if sort == "title":
            all_projects.sort(key=lambda p: p.title, reverse=(order == "desc"))
        elif sort == "created_at":
            all_projects.sort(key=lambda p: p.created_at, reverse=(order == "desc"))
        else:  # updated_at (default)
            all_projects.sort(key=lambda p: p.updated_at, reverse=(order == "desc"))
        
        # Apply pagination
        total = len(all_projects)
        paginated_projects = all_projects[offset:offset + limit]
        
        # Convert to response format
        project_summaries = [project_to_summary(project) for project in paginated_projects]
        
        # Calculate pagination metadata
        has_more = offset + limit < total
        next_offset = offset + limit if has_more else None
        
        pagination = PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            hasMore=has_more,
            nextOffset=next_offset
        )
        
        response_data = ProjectListResponse(
            data=project_summaries,
            pagination=pagination
        )
        
        logger.info(f"Listed {len(project_summaries)} projects (total: {total}) for user: {user_id}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{project_id}", response_model=ProjectDetails)
async def get_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id)
) -> ProjectDetails:
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
        
        logger.info(f"Retrieved project: {project.title} (ID: {project_id}) for user: {user_id}")
        response_data = project_to_response(project)
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{project_id}/file-tree", response_model=FileTreeResponse)
async def get_project_file_tree(
    project_id: str,
    user_id: str = Depends(get_current_user_id)
) -> FileTreeResponse:
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
            totalFiles=total_files,
            totalFolders=total_folders,
            lastUpdated=last_updated,
        )
        
        logger.info(f"Retrieved file tree for project {project_id}: {total_files} files, {total_folders} folders")
        
        response_data = FileTreeResponse(
            fileTree=file_tree,
            metadata=metadata,
        )
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving file tree for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )




@router.post("/", response_model=ProjectDetails, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    user_id: str = Depends(get_current_user_id)
) -> ProjectDetails:
    """
    Create a new project
    
    Matches frontend expectation: POST /projects
    """
    try:
        repos = get_repositories()
        
        # Prepare project data
        project_data = {
            "title": request.title,
            "description": request.description,
            "tags": request.tags,
            "collaborators": [],  # Start with empty collaborators
            "settings": request.settings.model_dump() if request.settings else {},
            "word_count": 0,
            "document_count": 0,
        }
        
        project = await repos.project.create(project_data)
        
        logger.info(f"Created project: {project.title} (ID: {project.id}) for user: {user_id}")
        response_data = project_to_response(project)
        return response_data
        
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{project_id}", response_model=ProjectDetails)
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    user_id: str = Depends(get_current_user_id)
) -> ProjectDetails:
    """
    Update an existing project
    
    Matches frontend expectation: PUT /projects/{projectId}
    """
    try:
        repos = get_repositories()
        
        # Check if project exists
        existing_project = await repos.project.get_by_id(project_id)
        if not existing_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Prepare updates (only include non-None values)
        updates = {}
        if request.title is not None:
            updates["title"] = request.title
        if request.description is not None:
            updates["description"] = request.description
        if request.tags is not None:
            updates["tags"] = request.tags
        if request.settings is not None:
            updates["settings"] = request.settings.model_dump()
        
        # Update project
        updated_project = await repos.project.update(project_id, updates)
        
        logger.info(f"Updated project: {project_id} for user: {user_id}")
        response_data = project_to_response(updated_project)
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{project_id}", response_model=Dict[str, str])
async def delete_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id)
) -> Dict[str, str]:
    """
    Delete a project
    
    Matches frontend expectation: DELETE /projects/{projectId}
    """
    try:
        repos = get_repositories()
        
        # Check if project exists
        existing_project = await repos.project.get_by_id(project_id)
        if not existing_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Delete project
        success = await repos.project.delete(project_id)
        
        if success:
            logger.info(f"Deleted project: {project_id} for user: {user_id}")
            response_data = {"message": f"Project {project_id} deleted successfully"}
            return response_data
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete project"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )