"""
Request schemas for document-related API endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema


class DocumentContent(BaseModel):
    """ProseMirror document content structure"""
    type: str = "doc"
    content: List[Dict[str, Any]] = Field(default_factory=list)
    
    model_config = {"populate_by_name": True}


class CreateDocumentRequest(BaseSchema):
    """Request to create a new document"""
    model_config = {"populate_by_name": True}
    
    project_id: str
    title: str
    path: str
    content: DocumentContent = Field(default_factory=DocumentContent)
    tags: List[str] = Field(default_factory=list)
    file_tree_parent_id: Optional[str] = None


class UpdateDocumentRequest(BaseSchema):
    """Request to update an existing document"""
    model_config = {"populate_by_name": True}
    
    title: Optional[str] = None
    content: Optional[DocumentContent] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None


class BulkDocumentRequest(BaseSchema):
    """Request for bulk document operations"""
    model_config = {"populate_by_name": True}
    
    document_ids: List[str]
    operation: str  # 'delete', 'tag', 'move'
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DocumentSearchRequest(BaseSchema):
    """Request for document search"""
    model_config = {"populate_by_name": True}
    
    query: str
    project_id: Optional[str] = None
    tags: Optional[List[str]] = Field(default=None)
    limit: int = Field(default=20)
    offset: int = Field(default=0)