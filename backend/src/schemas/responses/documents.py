"""
Response schemas for document-related API endpoints
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema
from src.schemas.responses.tags import TagInfo


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


class DocumentContent(BaseModel):
    """Document content wrapper returned by API with computed fields.

    TODO(content policy)
    - content is canonical plain Markdown (no JSX). Other formats must be
      converted to Markdown before persistence.
    - index_markdown_present indicates whether an indexable Markdown variant is
      available/persisted. For now it's derived; later should reflect persisted
      index state. last_indexed_at conveys freshness when persisted.

    TODO(file uploads and large content)
    - For uploaded originals, do not overload `content`.
      Provide one of:
        - original_download_url: Short-lived signed URL to object storage
        - or a proxy endpoint: GET /documents/{id}/original (preferred)
    - For very large Markdown bodies, consider:
        - content_download_url: Fetch full Markdown via URL/proxy
        - content may be truncated; preview communicates a short excerpt
    """
    model_config = {"populate_by_name": True}
    content: str
    format: Literal["md"] = "md"
    word_count: int
    preview: Optional[str] = None
    summary: Optional[str] = None
    index_markdown_present: bool = False
    last_indexed_at: Optional[str] = None


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