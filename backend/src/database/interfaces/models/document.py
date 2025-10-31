# backend/src/database/interfaces/models/document.py
"""
Domain model for Document - database-agnostic
"""
from datetime import datetime
from typing import Optional, Any, List

from pydantic import BaseModel, Field, ConfigDict, field_validator


class Document(BaseModel):
    """
    Domain model for Document - pure business logic representation
    """
    # Identity
    id: str
    project_id: str
    title: str
    path: str

    # Content stored as plaintext Markdown (no JSX). This is the source of truth for the document body.
    content: str = ""
    word_count: int = 0
    version: str = "1.0.0"

    # Index cache (optional)
    index_markdown: Optional[str] = None
    last_indexed_at: Optional[datetime] = None

    # Edit Control
    is_locked: bool = False
    locked_by: Optional[str] = None

    # File Tree Integration
    file_tree_id: Optional[str] = None

    # User Tracking
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    # Tags represented as tag IDs for stability
    tag_ids: List[str] = Field(default_factory=list)

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
    )

    @field_validator("content", mode="before")
    @classmethod
    def _ensure_content(cls, v: Any) -> str:
        if v is None:
            return ""
        return v if isinstance(v, str) else str(v)

    @field_validator("tag_ids", mode="before")
    @classmethod
    def _normalize_tag_ids(cls, v: Any) -> List[str]:
        if v is None:
            return []
        if isinstance(v, list):
            normalized: List[str] = []
            for item in v:
                # Support ORM Tag objects by projecting to id when present
                tag_id = getattr(item, "id", None)
                if isinstance(item, str):
                    normalized.append(item)
                elif isinstance(tag_id, str):
                    normalized.append(tag_id)
                else:
                    # Fallback: string cast
                    normalized.append(str(item))
            return normalized
        # Fallback: return single tag as string
        return [str(v)]