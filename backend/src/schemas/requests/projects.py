"""
Request schemas for project-related API endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema


class ProjectCollaborator(BaseModel):
    """Project collaborator info"""
    model_config = {"populate_by_name": True}
    
    user_id: str
    role: str  # 'owner' | 'editor' | 'viewer'
    name: str
    avatar: Optional[str] = None


class ProjectSettings(BaseModel):
    """Project settings"""
    model_config = {"populate_by_name": True}
    
    auto_save_interval: int = Field(default=30000)
    word_count_target: int = Field(default=0)
    backup_enabled: bool = Field(default=True)


class CreateProjectRequest(BaseSchema):
    """Request to create a new project"""
    model_config = {"populate_by_name": True}
    
    title: str
    description: str = Field(default="")
    tags: List[str] = Field(default_factory=list)
    settings: ProjectSettings = Field(default_factory=ProjectSettings)


class UpdateProjectRequest(BaseSchema):
    """Request to update an existing project"""
    model_config = {"populate_by_name": True}
    
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    settings: Optional[ProjectSettings] = None


class CreateFileTreeItemRequest(BaseSchema):
    """Request to create a new file tree item"""
    model_config = {"populate_by_name": True}
    
    name: str
    type: str  # 'file' | 'folder'
    parent_id: Optional[str] = None
    icon: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class UpdateFileTreeItemRequest(BaseSchema):
    """Request to update a file tree item"""
    model_config = {"populate_by_name": True}
    
    name: Optional[str] = None
    parent_id: Optional[str] = None
    icon: Optional[str] = None
    tags: Optional[List[str]] = None


class MoveFileTreeItemRequest(BaseSchema):
    """Request to move a file tree item"""
    model_config = {"populate_by_name": True}
    
    new_parent_id: Optional[str] = None
    new_position: Optional[int] = None


class ProjectSearchRequest(BaseSchema):
    """Request for project search"""
    model_config = {"populate_by_name": True}
    
    query: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = Field(default=20)
    offset: int = Field(default=0)
    sort_by: str = Field(default="updated_at")  # 'created_at' | 'updated_at' | 'title'
    sort_order: str = Field(default="desc")  # 'asc' | 'desc'