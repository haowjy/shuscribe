"""
Writing Domain Models

Handles author notes, prompts, research, character profiles, and plot outlines.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema


class AuthorNote(BaseSchema):
    """Author note for story development"""
    id: UUID
    workspace_id: UUID
    title: str
    content: str
    note_type: Optional[str] = None  # "plot", "character", "world", "chapter", etc.
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_private: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None


class AuthorNoteCreate(BaseModel):
    """Data for creating author notes"""
    workspace_id: UUID
    title: str
    content: str
    note_type: Optional[str] = None  # "plot", "character", "world", "chapter", etc.
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_private: bool = True


class AuthorNoteUpdate(BaseModel):
    """Data for updating author notes"""
    title: Optional[str] = None
    content: Optional[str] = None
    note_type: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_private: Optional[bool] = None


class WritingPrompt(BaseSchema):
    """Writing prompt for inspiration"""
    id: UUID
    workspace_id: UUID
    title: str
    prompt_text: str
    category: str = "general"
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class WritingPromptCreate(BaseModel):
    """Data for creating writing prompts"""
    workspace_id: UUID
    title: str
    prompt_text: str
    category: str = "general"
    tags: List[str] = Field(default_factory=list)


class WritingPromptUpdate(BaseModel):
    """Data for updating writing prompts"""
    title: Optional[str] = None
    prompt_text: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class ResearchItem(BaseSchema):
    """Research item for story development"""
    id: UUID
    workspace_id: UUID
    title: str
    content: str
    source_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None


class ResearchItemCreate(BaseModel):
    """Data for creating research items"""
    workspace_id: UUID
    title: str
    content: str
    source_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class ResearchItemUpdate(BaseModel):
    """Data for updating research items"""
    title: Optional[str] = None
    content: Optional[str] = None
    source_url: Optional[str] = None
    tags: Optional[List[str]] = None


class CharacterProfile(BaseSchema):
    """Character profile for story development"""
    id: UUID
    workspace_id: UUID
    name: str
    description: str
    physical_description: Optional[str] = None
    personality: Optional[str] = None
    backstory: Optional[str] = None
    relationships: Dict[str, str] = Field(default_factory=dict)
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class CharacterProfileCreate(BaseModel):
    """Data for creating character profiles"""
    workspace_id: UUID
    name: str
    description: str
    physical_description: Optional[str] = None
    personality: Optional[str] = None
    backstory: Optional[str] = None
    relationships: Dict[str, str] = Field(default_factory=dict)
    notes: Optional[str] = None


class CharacterProfileUpdate(BaseModel):
    """Data for updating character profiles"""
    name: Optional[str] = None
    description: Optional[str] = None
    physical_description: Optional[str] = None
    personality: Optional[str] = None
    backstory: Optional[str] = None
    relationships: Optional[Dict[str, str]] = None
    notes: Optional[str] = None


class PlotOutline(BaseSchema):
    """Plot outline for story structure"""
    id: UUID
    workspace_id: UUID
    title: str
    description: str
    structure: Dict[str, Any] = Field(default_factory=dict)  # Flexible structure for different outline types
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class PlotOutlineCreate(BaseModel):
    """Data for creating plot outlines"""
    workspace_id: UUID
    title: str
    description: str
    structure: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


class PlotOutlineUpdate(BaseModel):
    """Data for updating plot outlines"""
    title: Optional[str] = None
    description: Optional[str] = None
    structure: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None