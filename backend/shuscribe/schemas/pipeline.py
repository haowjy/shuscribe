from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field

#
# ENUMS
# 

class EntitySignificanceLevel(str, Enum):
    CENTRAL = "central"
    MAJOR = "major"
    SUPPORTING = "supporting"
    MINOR = "minor"
    BACKGROUND = "background"
    PERIPHERAL = "peripheral"
    
    def to_int(self) -> int:
        return {
            self.CENTRAL: 5,
            self.MAJOR: 4,
            self.SUPPORTING: 3,
            self.MINOR: 2,
            self.BACKGROUND: 1,
            self.PERIPHERAL: 0,
        }[self]
    
    def __gt__(self, other: "EntitySignificanceLevel") -> bool:
        return self.to_int() > other.to_int()
    
    def __ge__(self, other: "EntitySignificanceLevel") -> bool:
        return self.to_int() >= other.to_int()
    
    def __lt__(self, other: "EntitySignificanceLevel") -> bool:
        return self.to_int() < other.to_int()
    
    def __le__(self, other: "EntitySignificanceLevel") -> bool:
        return self.to_int() <= other.to_int()

class WikiArticleType(str, Enum):
    """Types of wiki articles that can be generated"""
    MAIN = "main"
    CHARACTER = "character"
    LOCATION = "location"
    ITEM = "item"
    CONCEPT = "concept"
    
# 
# INPUTS
#

class Promptable(BaseModel):
    """Base class for all promptable objects"""
    @abstractmethod
    def to_prompt(self) -> str:
        pass

class Chapter(Promptable):
    title: Optional[str] = Field(default=None, description="Title of the chapter")
    id: int = Field(description="Unique self-incrementing identifier for the chapter")
    content: str = Field(description="Content of the chapter")
    
    def to_prompt(self) -> str:
        if self.title:
            return f"### Chapter {self.id}: {self.title}\n\n<Chapter>\n{self.content}\n</Chapter>"
        else:
            return f"### Chapter {self.id}\n\n<Chapter>\n{self.content}\n</Chapter>"
    
    
class ChapterSummary(Promptable):
    chapter_id: int
    summary: str
    
    def to_prompt(self) -> str:
        return f"Chapter {self.chapter_id}: {self.summary}"
    
    

# 
# OUTPUT
#

class Entity(BaseModel):
    id: str
    name: str
    aliases: List[str] = Field(default_factory=list)
    type: str
    description: str
    significance: EntitySignificanceLevel 
    first_appearance: str  # Chapter ID
    last_appearance: str  # Chapter ID
    appearances: List[str] = Field(default_factory=list)  # Chapter IDs
    relationships: Dict[str, str] = Field(default_factory=dict)  # entity_id -> relationship

class EntityList(BaseModel):
    entities: List[Entity]
    
class WikiArticle(BaseModel):
    entity_id: Optional[str] = None  # None for main wiki article
    title: str
    content: str = Field(default="", description="Markdown formatted content for the wiki article")
    related_entities: List[str] = Field(default_factory=list)  # entity_ids
    last_updated_chapter: str




#
# CONFIG
#


class ProcessingConfig(BaseModel):
    """Configuration for the processing pipeline"""
    provider_name: str
    model: str
    max_previous_chapters: int = 5
    generate_entity_articles_threshold: EntitySignificanceLevel = EntitySignificanceLevel.SUPPORTING
    focus_genre: Optional[str] = None  # For genre-specific entity extraction