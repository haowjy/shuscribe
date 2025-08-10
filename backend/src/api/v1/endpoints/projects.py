# backend/src/api/v1/endpoints/projects.py
"""
Project API endpoints matching frontend expectations
"""
import logging
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field

from src.database.factory import get_repositories
from src.database.interfaces.models import Project, FileTreeItem, Tag
from src.schemas.base import ApiResponse
from src.schemas.responses.tags import TagInfo
from src.api.dependencies import require_auth, get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Response Models (matching frontend API types)
# ============================================================================

class ProjectCollaborator(BaseModel):
    """Project collaborator info"""
    model_config = {"populate_by_name": True}
    
    user_id: str
    role: str  # 'owner' | 'editor' | 'viewer'
    name: str
    avatar: str | None = None


class ProjectSettings(BaseModel):
    """Project settings"""
    model_config = {"populate_by_name": True}
    
    auto_save_interval: int = Field(default=30000)  # 30 seconds
    word_count_target: int = Field(default=0)
    backup_enabled: bool = Field(default=True)


class ProjectSummary(BaseModel):
    """Project summary for listing (subset of ProjectDetails)"""
    model_config = {"populate_by_name": True}
    
    id: str
    title: str
    description: str
    word_count: int
    document_count: int
    created_at: str
    updated_at: str
    tags: List[TagInfo]
    collaborators: List[ProjectCollaborator]


class ProjectDetails(BaseModel):
    """Complete project details matching frontend ProjectDetails interface"""
    model_config = {"populate_by_name": True}
    
    id: str
    title: str
    description: str
    word_count: int
    document_count: int
    created_at: str
    updated_at: str
    tags: List[TagInfo]
    collaborators: List[ProjectCollaborator]
    settings: ProjectSettings


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    model_config = {"populate_by_name": True}
    
    total: int
    limit: int
    offset: int
    has_more: bool
    next_offset: int | None = None


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
    tags: List[TagInfo] = []
    settings: ProjectSettings | None = None


class UpdateProjectRequest(BaseModel):
    """Request model for updating a project"""
    model_config = {"populate_by_name": True}
    
    title: str | None = None
    description: str | None = None
    tags: List[TagInfo] | None = None
    settings: ProjectSettings | None = None


class FileTreeItemResponse(BaseModel):
    """File tree item response matching frontend FileTreeItem interface"""
    model_config = {"populate_by_name": True}
    
    id: str
    name: str
    type: str  # 'file' | 'folder'
    path: str
    parent_id: str | None = None
    children: List["FileTreeItemResponse"] | None = None
    
    # File-specific properties
    document_id: str | None = None
    icon: str | None = None
    tags: List[TagInfo] = []
    word_count: int | None = None
    
    # Timestamps
    created_at: str
    updated_at: str


class FileTreeMetadata(BaseModel):
    """File tree metadata"""
    model_config = {"populate_by_name": True}
    
    total_files: int
    total_folders: int
    last_updated: str


class FileTreeResponse(BaseModel):
    """File tree response matching frontend FileTreeResponse interface"""
    model_config = {"populate_by_name": True}
    
    file_tree: List[FileTreeItemResponse]
    metadata: FileTreeMetadata




# ============================================================================
# Helper Functions
# ============================================================================

def tag_to_info(tag: Tag | str) -> TagInfo:
    """Convert Tag model or tag string to TagInfo response"""
    if isinstance(tag, str):
        # For domain models where tags are stored as strings
        return TagInfo(
            id=tag,  # Use the tag string as ID for now
            name=tag,
            icon=None,
            color=None
        )
    else:
        # Full Tag object
        return TagInfo(
            id=tag.id,
            name=tag.name,
            icon=tag.icon,
            color=tag.color
        )


async def recalculate_project_word_count(project: Project, repos) -> Project:
    """
    Recalculate project word count from all its documents.
    Returns the updated project with correct counts.
    """
    try:
        # Get all documents for this project
        documents = await repos.document.get_by_project_id(project.id)
        
        # Calculate total word count from all documents
        actual_word_count = sum(doc.word_count for doc in documents)
        actual_document_count = len(documents)
        
        # Check if we need to update the project
        needs_update = (
            project.word_count != actual_word_count or 
            project.document_count != actual_document_count
        )
        
        if needs_update:
            logger.info(
                f"Word count sync for project {project.id}: "
                f"stored={project.word_count} actual={actual_word_count}, "
                f"stored_docs={project.document_count} actual_docs={actual_document_count}"
            )
            
            # Update project with correct counts
            updated_project = await repos.project.update(project.id, {
                "word_count": actual_word_count,
                "document_count": actual_document_count,
            })
            
            # Return the updated project or original if update failed
            return updated_project if updated_project else project
        
        return project
        
    except Exception as e:
        logger.error(f"Error recalculating word count for project {project.id}: {e}")
        # Return original project if calculation fails
        return project


def project_to_summary(project: Project) -> ProjectSummary:
    """Convert Project model to ProjectSummary response"""
    # Parse collaborators from JSON
    collaborators = []
    for collab in project.collaborators:
        collaborators.append(ProjectCollaborator(
            user_id=collab.get("user_id", ""),
            role=collab.get("role", "viewer"),
            name=collab.get("name", ""),
            avatar=collab.get("avatar"),
        ))
    
    # Handle tags - in domain models they are List[str], convert to TagInfo
    tags = [tag_to_info(tag) for tag in project.tags] if project.tags else []
    
    return ProjectSummary(
        id=project.id,
        title=project.title,
        description=project.description,
        word_count=project.word_count,
        document_count=project.document_count,
        created_at=project.created_at.isoformat() if project.created_at and hasattr(project.created_at, 'isoformat') else str(project.created_at) if project.created_at else "",
        updated_at=project.updated_at.isoformat() if project.updated_at and hasattr(project.updated_at, 'isoformat') else str(project.updated_at) if project.updated_at else "",
        tags=tags,
        collaborators=collaborators,
    )


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
    
    # Handle tags - in domain models they are List[str], convert to TagInfo
    tags = [tag_to_info(tag) for tag in project.tags] if project.tags else []
    
    return ProjectDetails(
        id=project.id,
        title=project.title,
        description=project.description,
        word_count=project.word_count,
        document_count=project.document_count,
        created_at=project.created_at.isoformat() if project.created_at and hasattr(project.created_at, 'isoformat') else str(project.created_at) if project.created_at else "",
        updated_at=project.updated_at.isoformat() if project.updated_at and hasattr(project.updated_at, 'isoformat') else str(project.updated_at) if project.updated_at else "",
        tags=tags,
        collaborators=collaborators,
        settings=settings,
    )


def file_tree_item_to_response(item: FileTreeItem, children: List["FileTreeItemResponse"] | None = None) -> FileTreeItemResponse:
    """Convert FileTreeItem model to FileTreeItemResponse"""
    # Handle tags - in domain models they are List[str], convert to TagInfo  
    tags = [tag_to_info(tag) for tag in item.tags] if item.tags else []
    
    return FileTreeItemResponse(
        id=item.id,
        name=item.name,
        type=item.type,
        path=item.path,
        parent_id=item.parent_id,
        children=children if children else None,
        document_id=item.document_id,
        icon=item.icon,
        tags=tags,
        word_count=item.word_count,
        created_at=item.created_at.isoformat() if item.created_at and hasattr(item.created_at, 'isoformat') else str(item.created_at) if item.created_at else "",
        updated_at=item.updated_at.isoformat() if item.updated_at and hasattr(item.updated_at, 'isoformat') else str(item.updated_at) if item.updated_at else "",
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


async def resolve_project_tags(project_id: str, tag_requests: List[TagInfo], repos) -> List[Tag]:
    """
    Resolve tags for project creation with always-fork logic
    
    For each requested tag:
    1. Check if project-specific tag exists → use it
    2. Check if global tag exists → always fork it to project
    3. Create new project-specific tag if neither exists
    """
    resolved_tags = []
    
    for tag_request in tag_requests:
        try:
            # Check if project-specific tag already exists
            project_tag = await repos.tag.get_project_tag_by_name(project_id, tag_request.name)
            
            if project_tag:
                # Use existing project-specific tag
                logger.info(f"Using existing project tag '{tag_request.name}' for project {project_id}")
                resolved_tags.append(project_tag)
            else:
                # Check if global tag exists
                global_tag = await repos.tag.get_global_tag_by_name(tag_request.name)
                
                if global_tag:
                    # Always fork global tag to project with any customizations
                    logger.info(f"Forking global tag '{tag_request.name}' for project {project_id}")
                    customizations = extract_tag_customizations(tag_request, global_tag)
                    forked_tag = await repos.tag.fork_global_tag(
                        project_id, global_tag.id, customizations
                    )
                    resolved_tags.append(forked_tag)
                else:
                    # Create new project-specific tag
                    logger.info(f"Creating new project tag '{tag_request.name}' for project {project_id}")
                    new_tag = await repos.tag.create({
                        "name": tag_request.name,
                        "icon": tag_request.icon,
                        "color": tag_request.color,
                        "description": None,  # TagInfo doesn't have description
                        "category": None,     # TagInfo doesn't have category
                        "project_id": project_id,
                        "is_global": False,
                        "is_system": False,
                        "usage_count": 0
                    })
                    resolved_tags.append(new_tag)
                
        except Exception as e:
            logger.error(f"Error resolving tag '{tag_request.name}' for project {project_id}: {e}")
            # Continue with other tags rather than failing entire project creation
            continue
    
    return resolved_tags




def extract_tag_customizations(tag_request: TagInfo, global_tag: Tag) -> Dict[str, Any]:
    """Extract customization fields from tag request, using global tag defaults"""
    customizations = {
        "icon": tag_request.icon if tag_request.icon is not None else global_tag.icon,
        "color": tag_request.color if tag_request.color is not None else global_tag.color
    }
    return customizations




# ============================================================================
# API Endpoints
# ============================================================================


@router.get("", response_model=ProjectListResponse)
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
        
        # Use conditional user filtering based on environment
        from src.config import settings
        if settings.should_filter_by_user:
            all_projects = await repos.project.list_by_user(user_id)
        else:
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
            has_more=has_more,
            next_offset=next_offset
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
        
        # Use conditional user filtering based on environment
        from src.config import settings
        if settings.should_filter_by_user:
            project = await repos.project.get_by_user_and_id(user_id, project_id)
        else:
            project = await repos.project.get_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Lazy sync: recalculate word count from documents
        project = await recalculate_project_word_count(project, repos)
        
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
        
        # Verify project exists with user filtering
        from src.config import settings
        if settings.should_filter_by_user:
            project = await repos.project.get_by_user_and_id(user_id, project_id)
        else:
            project = await repos.project.get_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Lazy sync: recalculate word count from documents
        project = await recalculate_project_word_count(project, repos)
        
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
        
        response_data = FileTreeResponse(
            file_tree=file_tree,
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




@router.post("", response_model=ProjectDetails, status_code=status.HTTP_201_CREATED)
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
        
        # Prepare project data (without tags initially)
        project_data = {
            "title": request.title,
            "description": request.description,
            "collaborators": [],  # Start with empty collaborators
            "settings": request.settings.model_dump() if request.settings else {},
            "word_count": 0,
            "document_count": 0,
            "owner_id": user_id,
            "created_by": user_id,
            "tags": []  # Start with empty tags, will resolve after creation
        }
        
        # Create project first
        project = await repos.project.create(project_data)
        
        # Resolve and assign tags with smart forking logic
        if request.tags:
            resolved_tags = await resolve_project_tags(project.id, request.tags, repos)
            
            # Convert resolved tags to string list for domain model
            tag_names = [tag.name for tag in resolved_tags]
            
            # Update project with resolved tags
            updated_project = await repos.project.update(project.id, {"tags": tag_names})
            if updated_project:
                project = updated_project
        
        logger.info(f"Created project: {project.title} (ID: {project.id}) with {len(project.tags) if project.tags else 0} tags for user: {user_id}")
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
        
        # Check if project exists with user filtering
        from src.config import settings
        if settings.should_filter_by_user:
            existing_project = await repos.project.get_by_user_and_id(user_id, project_id)
        else:
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
        if request.settings is not None:
            updates["settings"] = request.settings.model_dump()
        
        # Update project with basic fields first
        updated_project = await repos.project.update(project_id, updates)
        
        if updated_project is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update project: Updated project not returned"
            )
        
        # Handle tag updates separately with always-fork logic
        if request.tags is not None:
            logger.info(f"Updating tags for project {project_id}")
            resolved_tags = await resolve_project_tags(project_id, request.tags, repos)
            
            # Convert resolved tags to string list for domain model
            tag_names = [tag.name for tag in resolved_tags]
            
            # Update project with resolved tags
            updated_project = await repos.project.update(project_id, {"tags": tag_names})
            
            if updated_project is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update project tags"
                )

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
        
        # Check if project exists with user filtering
        from src.config import settings
        if settings.should_filter_by_user:
            existing_project = await repos.project.get_by_user_and_id(user_id, project_id)
        else:
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