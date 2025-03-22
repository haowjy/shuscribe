from abc import ABC, abstractmethod
from enum import Enum
import re
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field

from shuscribe.schemas.base import Promptable
from shuscribe.schemas.wikigen.entity import EntitySigLvl

# 
# SHARED INPUTS
#

class Chapter(Promptable):
    title: Optional[str] = Field(default=None, description="Title of the chapter")
    id: int = Field(description="Unique self-incrementing identifier for the chapter")
    content: str = Field(description="Content of the chapter")
    
    def to_prompt(self) -> str:
        if self.title:
            return f"\n### [{self.id}] {self.title}\n<Content>\n{self.content}\n</Content>"
        else:
            return f"\n<Content>\n{self.content}\n</Content>"

class StoryMetadata(Promptable):
    title: str
    description: Optional[str] = None
    author: Optional[str] = None
    word_count: Optional[int] = None
    genres: Optional[List[str]] = None
    additional_tags: Optional[List[str]] = None
    
    def to_prompt(self) -> str:
        p = (
            f"Title: {self.title}\n" +
            (f"Genres: {self.genres}\n" if self.genres else "") +
            (f"Additional Tags: {self.additional_tags}\n" if self.additional_tags else "") +
            (f"Description: |\n{self.description}" if self.description else "")
        )
        return p
    
#
# CONFIG
#


class ProcessingConfig(BaseModel):
    """Configuration for the processing pipeline"""
    provider_name: str
    model: str
    max_previous_chapters: int = 5
    generate_entity_articles_threshold: EntitySigLvl = EntitySigLvl.SUPPORTING
    focus_genre: Optional[str] = None  # For genre-specific entity extraction