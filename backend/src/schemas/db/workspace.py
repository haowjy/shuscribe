"""
Workspace Domain Models

Handles workspace management, story arcs, and processing state.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class Arc(BaseModel):
    """Story arc definition for batch processing"""
    name: str
    description: Optional[str] = None
    start_chapter: int = Field(..., description="First chapter in arc (1-based)")
    end_chapter: int = Field(..., description="Last chapter in arc (1-based)")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.name} (Ch. {self.start_chapter}-{self.end_chapter})"


class WorkspaceBase(BaseModel):
    """Base workspace schema"""
    name: str = Field(..., description="Workspace/project name")
    description: str = Field(default="", description="Workspace/project description")
    arcs: List[Arc] = Field(default_factory=list, description="Story arcs for processing")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Workspace-specific settings")


class WorkspaceCreate(WorkspaceBase):
    """Schema for creating new workspaces"""
    owner_id: UUID


class WorkspaceUpdate(BaseModel):
    """Schema for updating workspaces (all fields optional)"""
    name: Optional[str] = None
    description: Optional[str] = None
    arcs: Optional[List[Arc]] = None
    settings: Optional[Dict[str, Any]] = None


class Workspace(WorkspaceBase):
    """Complete workspace model"""
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @property
    def total_chapters(self) -> int:
        """Calculate total chapters from arcs"""
        if not self.arcs:
            return 0
        return max(arc.end_chapter for arc in self.arcs) if self.arcs else 0
    
    @property
    def current_arc(self) -> Optional[Arc]:
        """Get the currently active arc"""
        # Simple implementation - could be enhanced with processing state
        return self.arcs[0] if self.arcs else None
    
    def get_arc_by_chapter(self, chapter_number: int) -> Optional[Arc]:
        """Find which arc contains a specific chapter"""
        for arc in self.arcs:
            if arc.start_chapter <= chapter_number <= arc.end_chapter:
                return arc
        return None
    
    model_config = ConfigDict(from_attributes=True)