"""
Pydantic models for writing-related API responses.
"""
from typing import List
from uuid import UUID

from pydantic import BaseModel

from src.schemas.db.writing import AuthorNote, ResearchItem, CharacterProfile


class SearchAllResult(BaseModel):
    """Response model for a full content search."""
    notes: List[AuthorNote]
    research: List[ResearchItem]
    characters: List[CharacterProfile]

class TaggedContentResult(BaseModel):
    """Response model for content filtered by tags."""
    notes: List[AuthorNote]
    research: List[ResearchItem]

