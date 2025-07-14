"""
Response schemas for project-related API endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema
from src.schemas.responses.tags import TagInfo


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


class ProjectDetails(BaseSchema):
    """Complete project details"""
    model_config = {"populate_by_name": True}
    
    id: str
    title: str
    description: str
    word_count: int
    document_count: int
    created_at: str
    updated_at: str
    tags: List[TagInfo] = Field(default_factory=list)
    collaborators: List[ProjectCollaborator] = Field(default_factory=list)
    settings: ProjectSettings = Field(default_factory=ProjectSettings)


class ProjectSummary(BaseSchema):
    """Project summary for listing"""
    model_config = {"populate_by_name": True}
    
    id: str
    title: str
    description: str
    word_count: int
    document_count: int
    created_at: str
    updated_at: str
    tags: List[TagInfo] = Field(default_factory=list)


class FileTreeItemResponse(BaseSchema):
    """File tree item response"""
    model_config = {"populate_by_name": True}
    
    id: str
    name: str
    type: str  # 'file' | 'folder'
    path: str
    parent_id: Optional[str] = None
    children: Optional[List["FileTreeItemResponse"]] = None
    
    # File-specific properties
    document_id: Optional[str] = None
    icon: Optional[str] = None
    tags: List[TagInfo] = Field(default_factory=list)
    word_count: Optional[int] = None
    
    # Timestamps
    created_at: str
    updated_at: str


class FileTreeMetadata(BaseSchema):
    """File tree metadata"""
    model_config = {"populate_by_name": True}
    
    total_files: int
    total_folders: int
    total_word_count: int
    last_modified: str


class FileTreeResponse(BaseSchema):
    """Complete file tree response"""
    model_config = {"populate_by_name": True}
    
    items: List[FileTreeItemResponse]
    metadata: FileTreeMetadata


class ProjectListResponse(BaseSchema):
    """Response for project listing"""
    model_config = {"populate_by_name": True}
    
    projects: List[ProjectSummary]
    total: int
    limit: int
    offset: int
    has_more: bool
    next_offset: Optional[int] = None


class ProjectSearchResponse(BaseSchema):
    """Response for project search"""
    model_config = {"populate_by_name": True}
    
    results: List[ProjectSummary]
    total: int
    query: Optional[str] = None
    limit: int
    offset: int
    has_more: bool


class ProjectStatsResponse(BaseSchema):
    """Project statistics response"""
    model_config = {"populate_by_name": True}
    
    total_projects: int
    total_documents: int
    total_word_count: int
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list)


# Enable forward references for self-referencing FileTreeItemResponse
FileTreeItemResponse.model_rebuild()