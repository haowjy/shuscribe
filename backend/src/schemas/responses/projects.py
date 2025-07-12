"""
Response schemas for project-related API endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema


class ProjectCollaborator(BaseModel):
    """Project collaborator info"""
    model_config = {"populate_by_name": True}
    
    user_id: str = Field(alias="userId")
    role: str  # 'owner' | 'editor' | 'viewer'
    name: str
    avatar: Optional[str] = None


class ProjectSettings(BaseModel):
    """Project settings"""
    model_config = {"populate_by_name": True}
    
    auto_save_interval: int = Field(default=30000, alias="autoSaveInterval")
    word_count_target: int = Field(default=0, alias="wordCountTarget")
    backup_enabled: bool = Field(default=True, alias="backupEnabled")


class ProjectDetails(BaseSchema):
    """Complete project details"""
    model_config = {"populate_by_name": True}
    
    id: str
    title: str
    description: str
    word_count: int = Field(alias="wordCount")
    document_count: int = Field(alias="documentCount")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    tags: List[str] = Field(default_factory=list)
    collaborators: List[ProjectCollaborator] = Field(default_factory=list)
    settings: ProjectSettings = Field(default_factory=ProjectSettings)


class ProjectSummary(BaseSchema):
    """Project summary for listing"""
    model_config = {"populate_by_name": True}
    
    id: str
    title: str
    description: str
    word_count: int = Field(alias="wordCount")
    document_count: int = Field(alias="documentCount")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    tags: List[str] = Field(default_factory=list)


class FileTreeItemResponse(BaseSchema):
    """File tree item response"""
    model_config = {"populate_by_name": True}
    
    id: str
    name: str
    type: str  # 'file' | 'folder'
    path: str
    parent_id: Optional[str] = Field(default=None, alias="parentId")
    children: Optional[List["FileTreeItemResponse"]] = None
    
    # File-specific properties
    document_id: Optional[str] = Field(default=None, alias="documentId")
    icon: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    word_count: Optional[int] = Field(default=None, alias="wordCount")
    
    # Timestamps
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")


class FileTreeMetadata(BaseSchema):
    """File tree metadata"""
    model_config = {"populate_by_name": True}
    
    total_files: int = Field(alias="totalFiles")
    total_folders: int = Field(alias="totalFolders")
    total_word_count: int = Field(alias="totalWordCount")
    last_modified: str = Field(alias="lastModified")


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
    has_more: bool = Field(alias="hasMore")
    next_offset: Optional[int] = Field(default=None, alias="nextOffset")


class ProjectSearchResponse(BaseSchema):
    """Response for project search"""
    model_config = {"populate_by_name": True}
    
    results: List[ProjectSummary]
    total: int
    query: Optional[str] = None
    limit: int
    offset: int
    has_more: bool = Field(alias="hasMore")


class ProjectStatsResponse(BaseSchema):
    """Project statistics response"""
    model_config = {"populate_by_name": True}
    
    total_projects: int = Field(alias="totalProjects")
    total_documents: int = Field(alias="totalDocuments")
    total_word_count: int = Field(alias="totalWordCount")
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list, alias="recentActivity")


# Enable forward references for self-referencing FileTreeItemResponse
FileTreeItemResponse.model_rebuild()