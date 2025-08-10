"""
Path utilities for file tree management and auto-folder creation
"""
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import logging

from ..database.interfaces.models import FileTreeItem
from ..database.interfaces.file_tree_repository import FileTreeRepository

logger = logging.getLogger(__name__)


def normalize_path(path: str) -> str:
    """
    Normalize a path string for consistent handling
    
    Args:
        path: Input path (e.g., "/characters/elara", "characters/elara", "/characters//elara/")
        
    Returns:
        Normalized path starting with "/" and no trailing slash
        
    Examples:
        "/characters/elara" -> "/characters/elara"
        "characters/elara" -> "/characters/elara"  
        "/characters//elara/" -> "/characters/elara"
        "/characters" -> "/characters"
        "/" -> "/"
        "" -> "/"
    """
    if not path or path.strip() == "":
        return "/"
        
    # Use pathlib to normalize the path
    normalized = str(Path("/" + path.strip()).resolve())
    
    # Ensure it starts with /
    if not normalized.startswith("/"):
        normalized = "/" + normalized
        
    # Remove trailing slash unless it's root
    if normalized != "/" and normalized.endswith("/"):
        normalized = normalized[:-1]
        
    return normalized


def parse_path_segments(path: str) -> List[str]:
    """
    Parse a normalized path into its segments
    
    Args:
        path: Normalized path (e.g., "/characters/locations/taverns")
        
    Returns:
        List of path segments from root to leaf
        
    Examples:
        "/characters/locations/taverns" -> ["/characters", "/characters/locations", "/characters/locations/taverns"]
        "/characters" -> ["/characters"]
        "/" -> []
    """
    normalized = normalize_path(path)
    
    if normalized == "/":
        return []
    
    segments = []
    parts = normalized.strip("/").split("/")
    
    for i in range(len(parts)):
        segment_path = "/" + "/".join(parts[:i+1])
        segments.append(segment_path)
    
    return segments


def extract_folder_path(document_path: str) -> Optional[str]:
    """
    Extract the parent folder path from a document path
    
    Args:
        document_path: Full document path (e.g., "/characters/locations/taverns/prancing-pony")
        
    Returns:
        Parent folder path or None if document is at root
        
    Examples:
        "/characters/locations/taverns/prancing-pony" -> "/characters/locations/taverns"
        "/characters/elara" -> "/characters"
        "/standalone-doc" -> None (root level)
        "/" -> None
    """
    normalized = normalize_path(document_path)
    
    if normalized == "/" or "/" not in normalized[1:]:
        # Root level document
        return None
        
    parent_path = str(Path(normalized).parent)
    return parent_path if parent_path != "/" else None


async def ensure_folder_hierarchy_exists(
    project_id: str,
    document_path: str,
    file_tree_repo: FileTreeRepository
) -> Optional[str]:
    """
    Ensure all folders in a document path exist, creating them if necessary
    
    Args:
        project_id: Project ID
        document_path: Full path where document will be created
        file_tree_repo: File tree repository for database operations
        
    Returns:
        ID of the immediate parent folder, or None if document is at root level
        
    Examples:
        ensure_folder_hierarchy_exists("proj_123", "/characters/locations/taverns/doc", repo)
        -> Creates: "/characters", "/characters/locations", "/characters/locations/taverns"
        -> Returns: ID of "/characters/locations/taverns" folder
    """
    parent_folder_path = extract_folder_path(document_path)
    
    if not parent_folder_path:
        # Document is at root level
        return None
    
    # Get existing file tree items for this project
    existing_items = await file_tree_repo.get_by_project_id(project_id)
    existing_paths = {item.path: item for item in existing_items if item.type == "folder"}
    
    # Get all folder segments that need to exist
    folder_segments = parse_path_segments(parent_folder_path)
    
    parent_id = None
    
    # Create missing folders in order from root to leaf
    for folder_path in folder_segments:
        if folder_path in existing_paths:
            # Folder already exists
            parent_id = existing_paths[folder_path].id
            continue
            
        # Need to create this folder
        folder_name = Path(folder_path).name
        
        logger.info(f"Auto-creating folder '{folder_name}' at path '{folder_path}' for project {project_id}")
        
        folder_data = {
            "project_id": project_id,
            "name": folder_name,
            "path": folder_path,
            "type": "folder",
            "parent_id": parent_id,  # Parent of this folder
            "tags": []
        }
        
        created_folder = await file_tree_repo.create(folder_data)
        existing_paths[folder_path] = created_folder
        parent_id = created_folder.id
    
    return parent_id


def validate_document_path(path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a document path for correctness
    
    Args:
        path: Document path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Examples:
        validate_document_path("/characters/elara") -> (True, None)
        validate_document_path("") -> (False, "Path cannot be empty")
        validate_document_path("/../invalid") -> (False, "Path cannot contain '..' segments")
    """
    if not path or not path.strip():
        return False, "Path cannot be empty"
    
    try:
        normalized = normalize_path(path)
    except Exception as e:
        return False, f"Invalid path format: {str(e)}"
    
    # Check for invalid characters or patterns
    if ".." in path:
        return False, "Path cannot contain '..' segments"
        
    if "//" in path.replace("//", "/"):  # Allow normalization to fix double slashes
        return False, "Path cannot contain empty segments"
    
    # Check path length
    if len(normalized) > 500:
        return False, "Path too long (max 500 characters)"
        
    # Check individual segment length  
    segments = normalized.strip("/").split("/") if normalized != "/" else []
    for segment in segments:
        if len(segment) > 100:
            return False, f"Path segment '{segment}' too long (max 100 characters)"
        if not segment.strip():
            return False, "Path cannot contain empty segments"
    
    return True, None


def get_folder_name_from_path(folder_path: str) -> str:
    """
    Extract folder name from folder path
    
    Args:
        folder_path: Full folder path
        
    Returns:
        Just the folder name
        
    Examples:
        get_folder_name_from_path("/characters/locations") -> "locations"
        get_folder_name_from_path("/characters") -> "characters"
        get_folder_name_from_path("/") -> ""
    """
    normalized = normalize_path(folder_path)
    if normalized == "/":
        return ""
    return Path(normalized).name


def update_child_paths(old_parent_path: str, new_parent_path: str, child_path: str) -> str:
    """
    Update a child path when its parent folder is moved
    
    Args:
        old_parent_path: Original parent folder path
        new_parent_path: New parent folder path
        child_path: Current child path
        
    Returns:
        Updated child path
        
    Examples:
        update_child_paths("/old", "/new", "/old/child") -> "/new/child"
        update_child_paths("/old/sub", "/moved/sub", "/old/sub/deep/child") -> "/moved/sub/deep/child"
    """
    if not child_path.startswith(old_parent_path + "/"):
        # Child is not actually under the old parent path
        return child_path
    
    # Replace the old parent path with the new parent path
    relative_path = child_path[len(old_parent_path):]  # e.g., "/subfolder/file"
    return new_parent_path + relative_path


def calculate_new_path_after_rename(old_path: str, new_name: str) -> str:
    """
    Calculate new path after renaming an item
    
    Args:
        old_path: Current path of the item
        new_name: New name for the item
        
    Returns:
        New path with updated name
        
    Examples:
        calculate_new_path_after_rename("/characters/old-name", "new-name") -> "/characters/new-name"
        calculate_new_path_after_rename("/old-name", "new-name") -> "/new-name"
    """
    parent_path = extract_folder_path(old_path)
    if parent_path:
        return f"{parent_path}/{new_name}"
    else:
        return f"/{new_name}"