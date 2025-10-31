"""
Request schemas for document-related API endpoints
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator

from src.schemas.base import BaseSchema


class DocumentContent(BaseModel):
    """Document content wrapper with optional metadata.

    content must be canonical plaintext Markdown. Any other formats
    (docx/pdf/html/ProseMirror/MDX) must be converted to Markdown before
    persistence. The database stores only Markdown in `content`.
    """
    model_config = {"populate_by_name": True}
    content: str = ""
    format: Literal["md"] = "md"
    language: Optional[str] = None
    source: Optional[str] = None  # e.g., 'user' | 'import' | 'generated'


class CreateDocumentRequest(BaseSchema):
    """Request to create a new document"""
    model_config = {"populate_by_name": True}
    
    project_id: str
    title: str
    path: str
    content: Optional[DocumentContent] = None
    tag_ids: List[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("path")
    @classmethod
    def normalize_path(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Path cannot be empty")
        path_clean = v.strip()
        if not path_clean.startswith("/"):
            path_clean = "/" + path_clean
        while "//" in path_clean:
            path_clean = path_clean.replace("//", "/")
        return path_clean


class UpdateDocumentRequest(BaseSchema):
    """Request to update an existing document"""
    model_config = {"populate_by_name": True}
    
    title: Optional[str] = None
    content: Optional[DocumentContent] = None
    tag_ids: Optional[List[str]] = None
    version: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title_optional(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


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