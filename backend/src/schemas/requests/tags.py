"""
Request schemas for tag-related API endpoints
"""
from typing import Optional, List
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema


class CreateTagRequest(BaseSchema):
    """Request to create a new tag"""
    model_config = {"populate_by_name": True}
    
    name: str = Field(max_length=100)
    icon: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7, pattern=r"^#[0-9A-Fa-f]{6}$")  # hex color
    description: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None, max_length=100)
    is_system: bool = Field(default=False)


class UpdateTagRequest(BaseSchema):
    """Request to update an existing tag"""
    model_config = {"populate_by_name": True}
    
    name: Optional[str] = Field(default=None, max_length=100)
    icon: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7, pattern=r"^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None, max_length=100)


class AssignTagRequest(BaseSchema):
    """Request to assign tag to file/document"""
    model_config = {"populate_by_name": True}
    
    file_tree_item_id: str


class UnassignTagRequest(BaseSchema):
    """Request to remove tag from file/document"""
    model_config = {"populate_by_name": True}
    
    file_tree_item_id: str


class SearchTagsRequest(BaseSchema):
    """Request for tag search"""
    model_config = {"populate_by_name": True}
    
    query: str = Field(min_length=1)
    category: Optional[str] = Field(default=None)
    include_archived: bool = Field(default=False)
    limit: int = Field(default=20, ge=1, le=100)


class BulkTagOperationRequest(BaseSchema):
    """Request for bulk tag operations"""
    model_config = {"populate_by_name": True}
    
    tag_ids: List[str] = Field(min_length=1)
    operation: str = Field(pattern=r"^(archive|unarchive|delete)$")  # archive, unarchive, delete