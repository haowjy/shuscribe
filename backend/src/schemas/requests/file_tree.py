"""
Request schemas for file tree management API endpoints
"""
from typing import Optional
from pydantic import BaseModel, field_validator

from src.utils.path_utils import validate_document_path, normalize_path


class MoveFileTreeItemRequest(BaseModel):
    """Request to move a file tree item to a new location"""
    
    new_parent_id: Optional[str] = None  # None for root level
    new_path: str  # Full new path for the item
    new_position: Optional[int] = None  # Future: for ordering within parent
    
    @field_validator("new_path")
    @classmethod
    def validate_new_path(cls, v: str) -> str:
        """Validate the new path format"""
        if not v or not v.strip():
            raise ValueError("New path cannot be empty")
        
        # Normalize the path
        normalized = normalize_path(v)
        
        # Validate path
        is_valid, error = validate_document_path(normalized)
        if not is_valid:
            raise ValueError(f"Invalid path: {error}")
            
        return normalized


class RenameFileTreeItemRequest(BaseModel):
    """Request to rename a file tree item"""
    
    new_name: str
    
    @field_validator("new_name")
    @classmethod
    def validate_new_name(cls, v: str) -> str:
        """Validate the new name"""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
            
        name = v.strip()
        
        # Check length
        if len(name) > 100:
            raise ValueError("Name too long (max 100 characters)")
            
        # Check for invalid characters (basic validation)
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in name:
                raise ValueError(f"Name cannot contain character: {char}")
                
        return name


class CreateFolderRequest(BaseModel):
    """Request to create a new folder"""
    
    name: str
    parent_id: Optional[str] = None  # None for root level
    path: str  # Full path where folder should be created
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate the folder name"""
        if not v or not v.strip():
            raise ValueError("Folder name cannot be empty")
            
        name = v.strip()
        
        # Check length
        if len(name) > 100:
            raise ValueError("Folder name too long (max 100 characters)")
            
        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in name:
                raise ValueError(f"Folder name cannot contain character: {char}")
                
        return name
    
    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate the folder path"""
        if not v or not v.strip():
            raise ValueError("Path cannot be empty")
        
        # Normalize the path
        normalized = normalize_path(v)
        
        # Validate path
        is_valid, error = validate_document_path(normalized)
        if not is_valid:
            raise ValueError(f"Invalid path: {error}")
            
        return normalized