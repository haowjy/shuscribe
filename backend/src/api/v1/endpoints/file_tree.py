# backend/src/api/v1/endpoints/file_tree.py
"""
File Tree Management API endpoints

Handles moving, renaming, creating, and deleting files and folders in the project file tree.
Documents remain unchanged - only the organizational structure is modified.
"""
import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from src.database.factory import get_repositories
from src.database.interfaces.models import FileTreeItem
from src.schemas.responses.file_tree import FileTreeItemResponse
from src.schemas.requests.file_tree import MoveFileTreeItemRequest, RenameFileTreeItemRequest, CreateFolderRequest
from src.api.dependencies import get_current_user_id
from src.utils.path_utils import (
    validate_document_path, 
    normalize_path, 
    extract_folder_path,
    ensure_folder_hierarchy_exists,
    get_folder_name_from_path
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================


class DeleteResponse(BaseModel):
    """Response for delete operations"""
    
    success: bool
    message: Optional[str] = None


# ============================================================================
# Helper Functions
# ============================================================================


def file_tree_item_to_response(item: FileTreeItem) -> FileTreeItemResponse:
    """Convert FileTreeItem domain model to API response"""
    return FileTreeItemResponse(
        id=item.id,
        project_id=item.project_id,
        name=item.name,
        type=item.type,
        path=item.path,
        parent_id=item.parent_id,
        document_id=item.document_id,
        word_count=item.word_count,
        icon=item.icon,
        tags=[],  # TODO: Convert tags properly when tag system is ready
        created_at=(
            item.created_at.isoformat()
            if item.created_at and hasattr(item.created_at, "isoformat")
            else str(item.created_at) if item.created_at else ""
        ),
        updated_at=(
            item.updated_at.isoformat()
            if item.updated_at and hasattr(item.updated_at, "isoformat")
            else str(item.updated_at) if item.updated_at else ""
        ),
        children=None  # Single item response, no children
    )


async def update_children_paths_recursively(
    project_id: str,
    old_parent_path: str,
    new_parent_path: str,
    file_tree_repo
) -> int:
    """
    Recursively update paths of all children when a folder is moved
    
    Args:
        project_id: Project ID
        old_parent_path: Original parent path
        new_parent_path: New parent path
        file_tree_repo: File tree repository
        
    Returns:
        Number of items updated
    """
    # Get all items in this project
    all_items = await file_tree_repo.get_by_project_id(project_id)
    
    updated_count = 0
    
    # Find all children of the old parent path
    for item in all_items:
        if item.path.startswith(old_parent_path + "/"):
            # This is a child of the moved folder
            # Update its path
            relative_path = item.path[len(old_parent_path):]  # e.g., "/subfolder/file"
            new_item_path = new_parent_path + relative_path
            
            logger.info(f"Updating child path: {item.path} -> {new_item_path}")
            
            await file_tree_repo.update(item.id, {"path": new_item_path})
            updated_count += 1
    
    return updated_count


async def validate_move_operation(
    item: FileTreeItem,
    new_parent_id: Optional[str],
    new_path: str,
    file_tree_repo
) -> Optional[str]:
    """
    Validate that a move operation is allowed
    
    Args:
        item: Item being moved
        new_parent_id: New parent ID (None for root)
        new_path: New path for the item
        file_tree_repo: File tree repository
        
    Returns:
        Error message if invalid, None if valid
    """
    # Check if trying to move item to itself
    if new_parent_id == item.id:
        return "Cannot move item to itself"
    
    # Check if new path already exists (for a different item)
    all_items = await file_tree_repo.get_by_project_id(item.project_id)
    for existing_item in all_items:
        if existing_item.id != item.id and existing_item.path == new_path:
            return f"Path '{new_path}' already exists"
    
    # If moving a folder, check for circular references
    if item.type == "folder" and new_parent_id:
        # Check if new parent is a descendant of this item
        new_parent = await file_tree_repo.get_by_id(new_parent_id)
        if new_parent and new_parent.path.startswith(item.path + "/"):
            return "Cannot move folder into its own descendant"
    
    # Validate new parent exists if specified
    if new_parent_id:
        new_parent = await file_tree_repo.get_by_id(new_parent_id)
        if not new_parent:
            return f"New parent with ID {new_parent_id} not found"
        if new_parent.type != "folder":
            return "New parent must be a folder"
        if new_parent.project_id != item.project_id:
            return "Cannot move item to different project"
    
    return None


# ============================================================================
# API Endpoints
# ============================================================================


@router.put("/{project_id}/file-tree/{item_id}/move", response_model=FileTreeItemResponse)
async def move_file_tree_item(
    project_id: str,
    item_id: str,
    request: MoveFileTreeItemRequest,
    user_id: str = Depends(get_current_user_id)
) -> FileTreeItemResponse:
    """
    Move a file tree item to a new location
    
    This changes the organizational structure without modifying document content.
    For files, the associated document remains unchanged.
    For folders, all children are recursively updated.
    """
    try:
        repos = get_repositories()
        
        # Get the item to move
        item = await repos.file_tree.get_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File tree item with ID {item_id} not found"
            )
        
        # Verify item belongs to the project
        if item.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item does not belong to the specified project"
            )
        
        # Validate the move operation
        validation_error = await validate_move_operation(
            item, request.new_parent_id, request.new_path, repos.file_tree
        )
        if validation_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_error
            )
        
        # Ensure parent folders exist for the new path if it's a file
        if item.type == "file":
            await ensure_folder_hierarchy_exists(
                project_id, request.new_path, repos.file_tree
            )
        
        # For folders, update all children first
        if item.type == "folder":
            updated_children = await update_children_paths_recursively(
                project_id, item.path, request.new_path, repos.file_tree
            )
            logger.info(f"Updated {updated_children} child items for folder move")
        
        # Update the item itself
        updates = {
            "path": request.new_path,
            "parent_id": request.new_parent_id,
        }
        
        # Extract new name from path if it changed
        old_name = item.name
        new_name = get_folder_name_from_path(request.new_path) if item.type == "folder" else request.new_path.split("/")[-1]
        if new_name and new_name != old_name:
            updates["name"] = new_name
        
        updated_item = await repos.file_tree.update(item_id, updates)
        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update file tree item"
            )
        
        logger.info(f"Moved file tree item {item_id} from {item.path} to {request.new_path}")
        return file_tree_item_to_response(updated_item)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moving file tree item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{project_id}/file-tree/{item_id}", response_model=FileTreeItemResponse)
async def rename_file_tree_item(
    project_id: str,
    item_id: str,
    request: RenameFileTreeItemRequest,
    user_id: str = Depends(get_current_user_id)
) -> FileTreeItemResponse:
    """
    Rename a file tree item
    
    This updates the name and path while keeping the same parent location.
    For folders, all children paths are updated recursively.
    """
    try:
        repos = get_repositories()
        
        # Get the item to rename
        item = await repos.file_tree.get_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File tree item with ID {item_id} not found"
            )
        
        # Verify item belongs to the project
        if item.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item does not belong to the specified project"
            )
        
        # Calculate new path with new name
        if item.parent_id:
            parent = await repos.file_tree.get_by_id(item.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Parent folder not found"
                )
            new_path = f"{parent.path}/{request.new_name}"
        else:
            # Root level item
            new_path = f"/{request.new_name}"
        
        # Check if new path already exists
        all_items = await repos.file_tree.get_by_project_id(project_id)
        for existing_item in all_items:
            if existing_item.id != item_id and existing_item.path == new_path:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"An item with name '{request.new_name}' already exists in this location"
                )
        
        # For folders, update all children paths
        if item.type == "folder":
            updated_children = await update_children_paths_recursively(
                project_id, item.path, new_path, repos.file_tree
            )
            logger.info(f"Updated {updated_children} child items for folder rename")
        
        # Update the item
        updates = {
            "name": request.new_name,
            "path": new_path,
        }
        
        updated_item = await repos.file_tree.update(item_id, updates)
        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update file tree item"
            )
        
        logger.info(f"Renamed file tree item {item_id} from '{item.name}' to '{request.new_name}'")
        return file_tree_item_to_response(updated_item)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error renaming file tree item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{project_id}/file-tree/folders", response_model=FileTreeItemResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    project_id: str,
    request: CreateFolderRequest,
    user_id: str = Depends(get_current_user_id)
) -> FileTreeItemResponse:
    """
    Create a new folder in the file tree
    
    This creates a new folder at the specified path. Parent folders are created automatically if needed.
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
        
        # Check if folder already exists at this path
        all_items = await repos.file_tree.get_by_project_id(project_id)
        for existing_item in all_items:
            if existing_item.path == request.path:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Folder already exists at path '{request.path}'"
                )
        
        # Ensure parent folders exist
        parent_folder_id = await ensure_folder_hierarchy_exists(
            project_id, request.path, repos.file_tree
        )
        
        # Verify parent_id matches what we expect
        if request.parent_id and request.parent_id != parent_folder_id:
            # Check if specified parent exists and matches path
            specified_parent = await repos.file_tree.get_by_id(request.parent_id)
            if not specified_parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Specified parent folder {request.parent_id} not found"
                )
            
            parent_path = extract_folder_path(request.path)
            if specified_parent.path != parent_path:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Specified parent_id does not match path structure"
                )
        
        # Create folder data
        folder_data = {
            "project_id": project_id,
            "name": request.name,
            "path": request.path,
            "type": "folder",
            "parent_id": request.parent_id or parent_folder_id,
            "tags": []
        }
        
        # Create the folder
        folder = await repos.file_tree.create(folder_data)
        
        logger.info(f"Created folder '{request.name}' at path '{request.path}' in project {project_id}")
        return file_tree_item_to_response(folder)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating folder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{project_id}/file-tree/{item_id}", response_model=DeleteResponse)
async def delete_file_tree_item(
    project_id: str,
    item_id: str,
    user_id: str = Depends(get_current_user_id)
) -> DeleteResponse:
    """
    Delete a file tree item
    
    For files: Removes the file tree reference. The associated document is NOT deleted.
    For folders: Removes the folder and all its children. Associated documents are NOT deleted.
    
    Warning: This only removes organizational structure, not the actual document content.
    """
    try:
        repos = get_repositories()
        
        # Get the item to delete
        item = await repos.file_tree.get_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File tree item with ID {item_id} not found"
            )
        
        # Verify item belongs to the project
        if item.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item does not belong to the specified project"
            )
        
        deleted_count = 0
        
        # If it's a folder, delete all children first
        if item.type == "folder":
            all_items = await repos.file_tree.get_by_project_id(project_id)
            
            # Find all children (items whose path starts with this folder's path)
            children_to_delete = []
            for child_item in all_items:
                if child_item.path.startswith(item.path + "/"):
                    children_to_delete.append(child_item)
            
            # Delete children
            for child in children_to_delete:
                child_deleted = await repos.file_tree.delete(child.id)
                if child_deleted:
                    deleted_count += 1
                    logger.info(f"Deleted child file tree item: {child.path}")
        
        # Delete the item itself
        success = await repos.file_tree.delete(item_id)
        if success:
            deleted_count += 1
            logger.info(f"Deleted file tree item: {item.path} (type: {item.type})")
            
            message = f"Deleted {item.type} '{item.name}'"
            if item.type == "folder" and deleted_count > 1:
                message += f" and {deleted_count - 1} child items"
            
            return DeleteResponse(success=True, message=message)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file tree item"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file tree item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )