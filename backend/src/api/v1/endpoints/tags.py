"""
Tag management API endpoints
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import get_repositories, get_auth_context
from src.database.factory import RepositoryContainer
from src.schemas.requests.tags import (
    CreateTagRequest,
    UpdateTagRequest,
    AssignTagRequest,
    UnassignTagRequest,
    SearchTagsRequest,
    BulkTagOperationRequest
)
from src.schemas.responses.tags import (
    TagResponse,
    TagListResponse,
    TagSearchResponse,
    TagStatsResponse,
    BulkTagOperationResponse
)
from src.schemas.base import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{project_id}/tags", response_model=ApiResponse[TagListResponse])
async def list_project_tags(
    project_id: str,
    include_archived: bool = Query(False, description="Include archived tags"),
    category: Optional[str] = Query(None, description="Filter by category"),
    repositories: RepositoryContainer = Depends(get_repositories),
    auth_context: dict = Depends(get_auth_context)
):
    """List all tags for a project"""
    try:
        # Check if project exists
        project = await repositories.project.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get tags
        if category:
            tags = await repositories.tag.get_by_category(project_id, category)
        else:
            tags = await repositories.tag.get_by_project_id(project_id, include_archived)
        
        tag_responses = [TagResponse.model_validate(tag.__dict__) for tag in tags]
        
        response = TagListResponse(
            tags=tag_responses,
            total=len(tag_responses),
            project_id=project_id
        )
        
        return ApiResponse(success=True, data=response)
        
    except Exception as e:
        logger.error(f"Error listing tags for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{project_id}/tags", response_model=ApiResponse[TagResponse])
async def create_tag(
    project_id: str,
    request: CreateTagRequest,
    repositories: RepositoryContainer = Depends(get_repositories),
    auth_context: dict = Depends(get_auth_context)
):
    """Create a new tag for a project"""
    try:
        # Check if project exists
        project = await repositories.project.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if tag name already exists in project
        existing_tag = await repositories.tag.get_by_name(project_id, request.name)
        if existing_tag:
            raise HTTPException(status_code=409, detail="Tag name already exists in this project")
        
        # Create tag
        tag_data = request.model_dump(exclude_unset=True)
        tag_data["project_id"] = project_id
        
        tag = await repositories.tag.create(tag_data)
        
        response = TagResponse.model_validate(tag.__dict__)
        return ApiResponse(success=True, data=response)
        
    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"Integrity error creating tag: {e}")
        raise HTTPException(status_code=409, detail="Tag name already exists in this project")
    except Exception as e:
        logger.error(f"Error creating tag: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{project_id}/tags/{tag_id}", response_model=ApiResponse[TagResponse])
async def get_tag(
    project_id: str,
    tag_id: str,
    repositories: RepositoryContainer = Depends(get_repositories),
    auth_context: dict = Depends(get_auth_context)
):
    """Get a specific tag by ID"""
    try:
        tag = await repositories.tag.get_by_id(tag_id)
        if not tag or tag.project_id != project_id:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        response = TagResponse.model_validate(tag.__dict__)
        return ApiResponse(success=True, data=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tag {tag_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{project_id}/tags/{tag_id}", response_model=ApiResponse[TagResponse])
async def update_tag(
    project_id: str,
    tag_id: str,
    request: UpdateTagRequest,
    repositories: RepositoryContainer = Depends(get_repositories),
    auth_context: dict = Depends(get_auth_context)
):
    """Update a tag"""
    try:
        # Check if tag exists and belongs to project
        existing_tag = await repositories.tag.get_by_id(tag_id)
        if not existing_tag or existing_tag.project_id != project_id:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        # Check if new name conflicts (if name is being updated)
        if request.name and request.name != existing_tag.name:
            name_conflict = await repositories.tag.get_by_name(project_id, request.name)
            if name_conflict:
                raise HTTPException(status_code=409, detail="Tag name already exists in this project")
        
        # Update tag
        updates = request.model_dump(exclude_unset=True)
        tag = await repositories.tag.update(tag_id, updates)
        
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        response = TagResponse.model_validate(tag.__dict__)
        return ApiResponse(success=True, data=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tag {tag_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{project_id}/tags/{tag_id}")
async def delete_tag(
    project_id: str,
    tag_id: str,
    repositories: RepositoryContainer = Depends(get_repositories),
    auth_context: dict = Depends(get_auth_context)
):
    """Delete a tag (hard delete)"""
    try:
        # Check if tag exists and belongs to project
        tag = await repositories.tag.get_by_id(tag_id)
        if not tag or tag.project_id != project_id:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        # Don't allow deletion of system tags
        if tag.is_system:
            raise HTTPException(status_code=403, detail="Cannot delete system tags")
        
        # TODO: Remove tag from all file tree items that reference it
        # This would require updating all FileTreeItem records that have this tag_id in their tag_ids array
        
        success = await repositories.tag.delete(tag_id)
        if not success:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        return ApiResponse(success=True, data={"message": "Tag deleted successfully"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tag {tag_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{project_id}/tags/{tag_id}/archive", response_model=ApiResponse[TagResponse])
async def archive_tag(
    project_id: str,
    tag_id: str,
    repositories: RepositoryContainer = Depends(get_repositories),
    auth_context: dict = Depends(get_auth_context)
):
    """Archive a tag (soft delete)"""
    try:
        # Check if tag exists and belongs to project
        existing_tag = await repositories.tag.get_by_id(tag_id)
        if not existing_tag or existing_tag.project_id != project_id:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        tag = await repositories.tag.archive(tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        response = TagResponse.model_validate(tag.__dict__)
        return ApiResponse(success=True, data=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error archiving tag {tag_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{project_id}/tags/{tag_id}/unarchive", response_model=ApiResponse[TagResponse])
async def unarchive_tag(
    project_id: str,
    tag_id: str,
    repositories: RepositoryContainer = Depends(get_repositories),
    auth_context: dict = Depends(get_auth_context)
):
    """Unarchive a tag"""
    try:
        # Check if tag exists and belongs to project
        existing_tag = await repositories.tag.get_by_id(tag_id)
        if not existing_tag or existing_tag.project_id != project_id:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        tag = await repositories.tag.unarchive(tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        response = TagResponse.model_validate(tag.__dict__)
        return ApiResponse(success=True, data=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unarchiving tag {tag_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{project_id}/tags/search", response_model=ApiResponse[TagSearchResponse])
async def search_tags(
    project_id: str,
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    include_archived: bool = Query(False, description="Include archived tags"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    repositories: RepositoryContainer = Depends(get_repositories),
    auth_context: dict = Depends(get_auth_context)
):
    """Search tags within a project"""
    try:
        # Check if project exists
        project = await repositories.project.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Search tags
        tags = await repositories.tag.search_tags(project_id, q, limit)
        
        # Filter by category if specified
        if category:
            tags = [tag for tag in tags if tag.category == category]
        
        # Filter archived if not included
        if not include_archived:
            tags = [tag for tag in tags if not tag.is_archived]
        
        tag_responses = [TagResponse.model_validate(tag.__dict__) for tag in tags]
        
        response = TagSearchResponse(
            tags=tag_responses,
            query=q,
            total=len(tag_responses),
            limit=limit
        )
        
        return ApiResponse(success=True, data=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching tags in project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{project_id}/tags/stats", response_model=ApiResponse[TagStatsResponse])
async def get_tag_stats(
    project_id: str,
    repositories: RepositoryContainer = Depends(get_repositories),
    auth_context: dict = Depends(get_auth_context)
):
    """Get tag statistics for a project"""
    try:
        # Check if project exists
        project = await repositories.project.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get all tags (including archived)
        all_tags = await repositories.tag.get_by_project_id(project_id, include_archived=True)
        active_tags = [tag for tag in all_tags if not tag.is_archived]
        archived_tags = [tag for tag in all_tags if tag.is_archived]
        system_tags = [tag for tag in active_tags if tag.is_system]
        
        # Get categories
        categories = list(set(tag.category for tag in active_tags if tag.category))
        
        # Get most used tags (top 10)
        most_used = sorted(active_tags, key=lambda t: t.usage_count, reverse=True)[:10]
        most_used_responses = [TagResponse.model_validate(tag.__dict__) for tag in most_used]
        
        response = TagStatsResponse(
            project_id=project_id,
            total_tags=len(all_tags),
            active_tags=len(active_tags),
            archived_tags=len(archived_tags),
            system_tags=len(system_tags),
            categories=sorted(categories),
            most_used_tags=most_used_responses
        )
        
        return ApiResponse(success=True, data=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tag stats for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{project_id}/tags/{tag_id}/assign", response_model=ApiResponse[TagResponse])
async def assign_tag_to_file(
    project_id: str,
    tag_id: str,
    request: AssignTagRequest,
    repositories: RepositoryContainer = Depends(get_repositories),
    auth_context: dict = Depends(get_auth_context)
):
    """Assign a tag to a file/document"""
    try:
        # Check if tag exists and belongs to project
        tag = await repositories.tag.get_by_id(tag_id)
        if not tag or tag.project_id != project_id:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        # Check if file tree item exists
        file_item = await repositories.file_tree.get_by_id(request.file_tree_item_id)
        if not file_item or file_item.project_id != project_id:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Add tag to file tree item if not already present
        if tag_id not in file_item.tag_ids:
            updated_tag_ids = file_item.tag_ids + [tag_id]
            await repositories.file_tree.update(request.file_tree_item_id, {"tag_ids": updated_tag_ids})
            
            # Increment tag usage count
            await repositories.tag.increment_usage(tag_id)
        
        # Return updated tag
        updated_tag = await repositories.tag.get_by_id(tag_id)
        response = TagResponse.model_validate(updated_tag.__dict__)
        return ApiResponse(success=True, data=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning tag {tag_id} to file {request.file_tree_item_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{project_id}/tags/{tag_id}/assign", response_model=ApiResponse[TagResponse])
async def unassign_tag_from_file(
    project_id: str,
    tag_id: str,
    request: UnassignTagRequest,
    repositories: RepositoryContainer = Depends(get_repositories),
    auth_context: dict = Depends(get_auth_context)
):
    """Remove a tag from a file/document"""
    try:
        # Check if tag exists and belongs to project
        tag = await repositories.tag.get_by_id(tag_id)
        if not tag or tag.project_id != project_id:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        # Check if file tree item exists
        file_item = await repositories.file_tree.get_by_id(request.file_tree_item_id)
        if not file_item or file_item.project_id != project_id:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Remove tag from file tree item if present
        if tag_id in file_item.tag_ids:
            updated_tag_ids = [tid for tid in file_item.tag_ids if tid != tag_id]
            await repositories.file_tree.update(request.file_tree_item_id, {"tag_ids": updated_tag_ids})
            
            # Decrement tag usage count
            await repositories.tag.decrement_usage(tag_id)
        
        # Return updated tag
        updated_tag = await repositories.tag.get_by_id(tag_id)
        response = TagResponse.model_validate(updated_tag.__dict__)
        return ApiResponse(success=True, data=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unassigning tag {tag_id} from file {request.file_tree_item_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")