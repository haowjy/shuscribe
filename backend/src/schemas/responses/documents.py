"""
Response schemas for document-related API endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema


class DocumentContent(BaseModel):
    """ProseMirror document content structure"""
    type: str = "doc"
    content: List[Dict[str, Any]] = Field(default_factory=list)
    
    model_config = {"populate_by_name": True}


class DocumentMeta(BaseSchema):
    """Document metadata response"""
    model_config = {"populate_by_name": True}
    
    id: str
    project_id: str = Field(alias="projectId")
    title: str
    path: str
    tags: List[str] = Field(default_factory=list)
    word_count: int = Field(alias="wordCount")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    version: str
    is_locked: bool = Field(alias="isLocked")
    locked_by: Optional[str] = Field(default=None, alias="lockedBy")
    file_tree_id: Optional[str] = Field(default=None, alias="fileTreeId")


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
    project_id: str = Field(alias="projectId")
    tags: List[str] = Field(default_factory=list)


class DocumentListResponse(BaseSchema):
    """Response for document listing"""
    model_config = {"populate_by_name": True}
    
    documents: List[DocumentMeta]
    total: int
    limit: int
    offset: int
    has_more: bool = Field(alias="hasMore")
    next_offset: Optional[int] = Field(default=None, alias="nextOffset")


class DocumentSearchResponse(BaseSchema):
    """Response for document search"""
    model_config = {"populate_by_name": True}
    
    results: List[DocumentMeta]
    total: int
    query: str
    limit: int
    offset: int
    has_more: bool = Field(alias="hasMore")


class DeleteResponse(BaseSchema):
    """Response for delete operations"""
    model_config = {"populate_by_name": True}
    
    success: bool
    message: str
    deleted_count: int = Field(alias="deletedCount")


class BulkOperationResponse(BaseSchema):
    """Response for bulk operations"""
    model_config = {"populate_by_name": True}
    
    success: bool
    message: str
    processed_count: int = Field(alias="processedCount")
    failed_count: int = Field(alias="failedCount")
    errors: List[str] = Field(default_factory=list)