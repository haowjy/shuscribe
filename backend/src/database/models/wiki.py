"""
Wiki Domain Models

Handles AI-generated articles with chapter-based versioning for spoiler prevention,
article connections, and content evolution.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator, validator


class WikiArticleType(str, Enum):
    """Types of wiki articles"""
    CHARACTER = "character"
    LOCATION = "location"
    CONCEPT = "concept"
    EVENT = "event"
    ORGANIZATION = "organization"
    OBJECT = "object"  # Changed from ITEM to OBJECT to match tests


class ArticleConnectionCreate(BaseModel):
    """Schema for creating article connections"""
    from_article_id: UUID
    to_article_id: UUID
    connection_type: str = Field(..., min_length=1, description="Type of connection (related, mentions, etc.)")
    description: Optional[str] = None
    strength: float = Field(default=1.0, ge=0.0, le=1.0, description="Connection strength (0.0-1.0)")
    
    @field_validator("to_article_id", mode="after")
    def validate_no_self_connection(cls, to_id, info):
        """
        Ensure `to_article_id` is not the same as `from_article_id`.
        `info.data` holds the other fields' values.
        """
        from_id = info.data.get("from_article_id")
        if from_id == to_id:
            raise ValueError("cannot connect article to itself")
        return to_id
    
    model_config = ConfigDict(from_attributes=True)


class ArticleConnection(BaseModel):
    """Connection between wiki articles"""
    id: UUID
    from_article_id: UUID
    to_article_id: UUID
    connection_type: str = Field(..., description="Type of connection (related, mentions, etc.)")
    description: Optional[str] = None
    strength: float = Field(default=1.0, description="Connection strength (0.0-1.0)")
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    def __str__(self) -> str:
        return f"{self.connection_type}: {self.from_article_id} -> {self.to_article_id}"
    
    model_config = ConfigDict(from_attributes=True)


class ChapterVersionCreate(BaseModel):
    """Schema for creating chapter versions"""
    article_id: UUID
    safe_through_chapter: int = Field(..., ge=1, description="Last chapter this version is safe for")
    content: str = Field(..., min_length=1, description="Version content")
    summary: Optional[str] = None
    ai_guidance: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ChapterVersionUpdate(BaseModel):
    """Schema for updating chapter versions"""
    safe_through_chapter: Optional[int] = Field(None, ge=1, description="Last chapter this version is safe for")
    content: Optional[str] = Field(None, min_length=1, description="Version content")
    summary: Optional[str] = None
    ai_guidance: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ChapterVersion(BaseModel):
    """Wiki content version safe through specific chapter"""
    id: UUID
    article_id: UUID
    safe_through_chapter: int = Field(..., description="Last chapter this version is safe for")
    content: str
    summary: Optional[str] = None
    ai_guidance: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class CurrentVersionCreate(BaseModel):
    """Schema for creating current versions"""
    article_id: UUID
    content: str = Field(..., min_length=1, description="Current version content")
    user_notes: Optional[str] = None
    ai_guidance: Optional[str] = None
    is_generated: bool = Field(default=False, description="Whether this version was AI-generated")
    
    model_config = ConfigDict(from_attributes=True)


class CurrentVersionUpdate(BaseModel):
    """Schema for updating current versions"""
    content: Optional[str] = Field(None, min_length=1, description="Current version content")
    user_notes: Optional[str] = None
    ai_guidance: Optional[str] = None
    is_generated: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)


class CurrentVersion(BaseModel):
    """Current/living version with user guidance for AI evolution"""
    id: UUID
    article_id: UUID
    content: str
    user_notes: Optional[str] = None
    ai_guidance: Optional[str] = None
    is_generated: bool = Field(default=False, description="Whether this version was AI-generated")
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class WikiArticle(BaseModel):
    """Complete wiki article with versioning"""
    id: UUID
    workspace_id: UUID
    title: str
    article_type: WikiArticleType
    content: str
    summary: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    safe_through_chapter: Optional[int] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class WikiArticleCreate(BaseModel):
    """Schema for creating wiki articles"""
    title: str = Field(..., min_length=1, description="Article title")
    article_type: WikiArticleType
    content: str = Field(..., min_length=1, description="Article content")
    summary: Optional[str] = None
    tags: List[str] = Field(default_factory=list, description="Article tags")
    safe_through_chapter: Optional[int] = Field(None, ge=1, description="Chapter this article is safe through")
    
    model_config = ConfigDict(from_attributes=True)


class WikiArticleUpdate(BaseModel):
    """Schema for updating wiki articles"""
    title: Optional[str] = Field(None, min_length=1, description="Article title")
    article_type: Optional[WikiArticleType] = None
    content: Optional[str] = Field(None, min_length=1, description="Article content") 
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    safe_through_chapter: Optional[int] = Field(None, ge=1, description="Chapter this article is safe through")
    
    model_config = ConfigDict(from_attributes=True) 