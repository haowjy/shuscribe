"""
Common request schemas used across multiple API endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema


class PaginationRequest(BaseSchema):
    """Standard pagination request parameters"""
    model_config = {"populate_by_name": True}
    
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SearchRequest(BaseSchema):
    """Standard search request parameters"""
    model_config = {"populate_by_name": True}
    
    query: str
    tags: Optional[List[str]] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="created_at", alias="sortBy")
    sort_order: str = Field(default="desc", alias="sortOrder")  # 'asc' | 'desc'


class TagRequest(BaseSchema):
    """Request to manage tags"""
    model_config = {"populate_by_name": True}
    
    tags: List[str]
    operation: str  # 'add' | 'remove' | 'replace'


class BulkOperationRequest(BaseSchema):
    """Request for bulk operations"""
    model_config = {"populate_by_name": True}
    
    item_ids: List[str] = Field(alias="itemIds")
    operation: str
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ReferenceSearchRequest(BaseSchema):
    """Request for @-reference search"""
    model_config = {"populate_by_name": True}
    
    query: str
    project_id: str = Field(alias="projectId")
    type: Optional[str] = None  # 'character' | 'location' | 'item' | 'all'
    limit: int = Field(default=10, ge=1, le=50)