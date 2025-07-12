"""
Database schema models for writing-related entities.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema


class AuthorNote(BaseSchema):
    """Author note model for the writing system"""
    id: UUID
    title: str
    content: str
    tags: List[str] = Field(default_factory=list)
    project_id: str = Field(alias="projectId")
    document_id: Optional[str] = Field(None, alias="documentId")
    priority: str = Field(default="normal")  # low, normal, high
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    
    
class ResearchItem(BaseSchema):
    """Research item model for the writing system"""
    id: UUID
    title: str
    content: str
    source: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    project_id: str = Field(alias="projectId")
    category: str = Field(default="general")  # general, worldbuilding, character, plot
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    
    
class CharacterProfile(BaseSchema):
    """Character profile model for the writing system"""
    id: UUID
    name: str
    description: str
    traits: Dict[str, Any] = Field(default_factory=dict)
    relationships: Dict[str, Any] = Field(default_factory=dict)
    backstory: str = Field(default="")
    tags: List[str] = Field(default_factory=list)
    project_id: str = Field(alias="projectId")
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")