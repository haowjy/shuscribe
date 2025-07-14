"""
Response schemas for document-related API endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema
from src.schemas.responses.tags import TagInfo


class DocumentContent(BaseModel):
    """ProseMirror document content structure"""
    type: str = "doc"
    content: List[Dict[str, Any]] = Field(default_factory=list)
    
    model_config = {"populate_by_name": True}


class DocumentMeta(BaseSchema):
    """Document metadata response"""
    model_config = {"populate_by_name": True}
    
    id: str
    project_id: str
    title: str
    path: str
    tags: List[TagInfo] = Field(default_factory=list)
    word_count: int
    created_at: str
    updated_at: str
    version: str
    is_locked: bool
    locked_by: Optional[str] = None
    file_tree_id: Optional[str] = None


class DocumentResponse(DocumentMeta):
    """Complete document response including content"""
    content: DocumentContent


class DocumentReference(BaseSchema):
    """Document reference for @-mentions"""
    model_config = {"populate_by_name": True}
    
    id: str
    title: str
    path: str
    type: str  # 'character' | 'location' | 'item' | 'chapter' | 'note'
    project_id: str
    tags: List[TagInfo] = Field(default_factory=list)


class DocumentListResponse(BaseSchema):
    """Response for document listing"""
    model_config = {"populate_by_name": True}
    
    documents: List[DocumentMeta]
    total: int
    limit: int
    offset: int
    has_more: bool
    next_offset: Optional[int] = None


class DocumentSearchResponse(BaseSchema):
    """Response for document search"""
    model_config = {"populate_by_name": True}
    
    results: List[DocumentMeta]
    total: int
    query: str
    limit: int
    offset: int
    has_more: bool


class DeleteResponse(BaseSchema):
    """Response for delete operations"""
    model_config = {"populate_by_name": True}
    
    success: bool
    message: str
    deleted_count: int


class BulkOperationResponse(BaseSchema):
    """Response for bulk operations"""
    model_config = {"populate_by_name": True}
    
    success: bool
    message: str
    processed_count: int
    failed_count: int
    errors: List[str] = Field(default_factory=list)