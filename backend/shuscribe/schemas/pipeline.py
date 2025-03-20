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

class Chapter(BaseModel):
    id: str
    title: Optional[str] = None
    content: str
    order: int
    
    
class ChapterSummary(BaseModel):
    chapter_id: str
    summary: str

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