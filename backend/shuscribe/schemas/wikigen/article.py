

from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field

# TODO: Implement this

# class WikiArticleType(str, Enum):
#     """Types of wiki articles that can be generated"""
#     MAIN = "main"
#     CHARACTER = "character"
#     LOCATION = "location"
#     ITEM = "item"
#     CONCEPT = "concept"
    
# class WikiArticle(BaseModel):
#     entity_id: Optional[str] = None  # None for main wiki article
#     title: str
#     content: str = Field(default="", description="Markdown formatted content for the wiki article")
#     related_entities: List[str] = Field(default_factory=list)  # entity_ids
#     last_updated_chapter: str

