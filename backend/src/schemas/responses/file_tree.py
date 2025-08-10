"""
Response schemas for file tree management API endpoints
"""
from typing import List, Optional
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema
from src.schemas.responses.tags import TagInfo


class FileTreeItemResponse(BaseSchema):
    """File tree item response"""
    model_config = {"populate_by_name": True}
    
    id: str
    project_id: str
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
    last_updated: str


class FileTreeResponse(BaseSchema):
    """Complete file tree response"""
    model_config = {"populate_by_name": True}
    
    file_tree: List[FileTreeItemResponse]
    metadata: FileTreeMetadata


# Enable forward references for self-referencing FileTreeItemResponse
FileTreeItemResponse.model_rebuild()