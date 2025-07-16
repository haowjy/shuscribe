"""
Response schemas for tag-related API endpoints
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema


class TagInfo(BaseSchema):
    """Simplified tag info for use in other responses"""
    model_config = {"populate_by_name": True}
    
    id: str
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None


class TagResponse(BaseSchema):
    """Tag response schema"""
    model_config = {"populate_by_name": True}
    
    id: str
    project_id: str
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    usage_count: int = Field(ge=0)
    is_system: bool = Field(default=False)
    is_archived: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime


class TagListResponse(BaseSchema):
    """Response for tag list operations"""
    model_config = {"populate_by_name": True}
    
    tags: List[TagResponse]
    total: int
    project_id: str


class TagSearchResponse(BaseSchema):
    """Response for tag search operations"""
    model_config = {"populate_by_name": True}
    
    tags: List[TagResponse]
    query: str
    total: int
    limit: int


class TagStatsResponse(BaseSchema):
    """Response for tag statistics"""
    model_config = {"populate_by_name": True}
    
    project_id: str
    total_tags: int
    active_tags: int
    archived_tags: int
    system_tags: int
    categories: List[str]
    most_used_tags: List[TagResponse]


class BulkTagOperationResponse(BaseSchema):
    """Response for bulk tag operations"""
    model_config = {"populate_by_name": True}
    
    operation: str
    processed: int
    successful: int
    failed: int
    errors: List[str] = Field(default_factory=list)