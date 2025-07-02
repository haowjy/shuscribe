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
    updated_at: datetime
    
    @property
    def chapter_number(self) -> int:
        """Alias for safe_through_chapter for backward compatibility"""
        return self.safe_through_chapter
    
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
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the article")
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @property
    def slug(self) -> str:
        """Generate URL-friendly slug from title"""
        import re
        return re.sub(r'[^a-zA-Z0-9-]', '-', self.title.lower()).strip('-')
    
    @property
    def preview(self) -> str:
        """Generate preview from content (first 150 chars)"""
        if not self.content:
            return ""
        # Remove markdown formatting for preview
        import re
        clean_content = re.sub(r'[#*_`\[\]()]', '', self.content)
        return clean_content[:150].strip() + ("..." if len(clean_content) > 150 else "")
    
    @classmethod
    def create_empty(cls, workspace_id: UUID) -> 'WikiArticle':
        """Create an empty wiki article instance"""
        return cls(
            id=UUID('00000000-0000-0000-0000-000000000000'),
            workspace_id=workspace_id,
            title="",
            article_type=WikiArticleType.CHARACTER,
            content="",
            created_at=datetime.now()
        )
    
    model_config = ConfigDict(from_attributes=True)


class WikiArticleCreate(BaseModel):
    """Schema for creating wiki articles"""
    workspace_id: UUID
    title: str = Field(..., min_length=1, description="Article title")
    article_type: WikiArticleType
    content: str = Field(..., min_length=1, description="Article content")
    summary: Optional[str] = None
    tags: List[str] = Field(default_factory=list, description="Article tags")
    safe_through_chapter: Optional[int] = Field(default=None, description="Chapter this article is safe through")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the article")
    
    model_config = ConfigDict(from_attributes=True)


class WikiArticleUpdate(BaseModel):
    """Schema for updating wiki articles"""
    title: Optional[str] = Field(default=None, min_length=1, description="Article title")
    article_type: Optional[WikiArticleType] = None
    content: Optional[str] = Field(default=None, min_length=1, description="Article content") 
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    safe_through_chapter: Optional[int] = Field(default=None, description="Chapter this article is safe through")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the article")
    
    model_config = ConfigDict(from_attributes=True)


class WikiPageBase(BaseModel):
    """Base wiki page schema - contains articles for a specific story context"""
    title: str = Field("Untitled Wiki", description="Wiki page title (usually story title)")
    description: str = Field("", description="Description of this wiki page")
    is_public: bool = Field(False, description="Whether this wiki page is publicly accessible")
    safe_through_chapter: int = Field(0, description="Highest chapter number safe to read with this wiki")


class WikiPageCreate(WikiPageBase):
    """Schema for creating a wiki page"""
    workspace_id: UUID


class WikiPageUpdate(BaseModel):
    """Schema for updating a wiki page"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    safe_through_chapter: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class WikiPage(WikiPageBase):
    """Complete wiki page with database fields"""
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def create_empty(cls, workspace_id: UUID) -> 'WikiPage':
        """Create an empty wiki page instance"""
        return cls(
            id=UUID('00000000-0000-0000-0000-000000000000'),
            workspace_id=workspace_id,
            title="",
            description="",
            is_public=False,
            safe_through_chapter=0,
            created_at=datetime.now()
        )
    
    model_config = ConfigDict(from_attributes=True)


class WikiArchiveMetadata(BaseModel):
    """Metadata for a wiki archive safe through a specific chapter"""
    wiki_page_id: UUID
    wiki_page_title: str
    safe_through_chapter: int = Field(..., description="Highest chapter number safe to read with this wiki")
    total_articles: int
    generation_timestamp: datetime
    source_arc_id: Optional[UUID] = Field(None, description="Arc that generated this archive (for processing context)")
    source_arc_title: Optional[str] = Field(None, description="Title of the arc that generated this archive")
    
    model_config = ConfigDict(from_attributes=True)


class WikiArchive(BaseModel):
    """Complete wiki archive safe through a specific chapter"""
    metadata: WikiArchiveMetadata
    articles: List[WikiArticle]
    article_links: List['WikiPageArticleLink'] = Field(default_factory=list)
    file_structure: Dict[str, str] = Field(default_factory=dict, description="Map of article titles to file paths")
    
    def get_article_by_title(self, title: str) -> Optional[WikiArticle]:
        """Get article by title"""
        return next((article for article in self.articles if article.title == title), None)
    
    def get_article_by_slug(self, slug: str) -> Optional[WikiArticle]:
        """Get article by slug"""
        return next((article for article in self.articles if article.slug == slug), None)
    
    def get_articles_by_type(self, article_type: WikiArticleType) -> List[WikiArticle]:
        """Get all articles of a specific type"""
        return [article for article in self.articles if article.article_type == article_type]
    
    def get_safe_articles(self, through_chapter: int) -> List[WikiArticle]:
        """Get articles safe through a specific chapter"""
        return [article for article in self.articles 
                if article.safe_through_chapter is None or article.safe_through_chapter <= through_chapter]
    
    model_config = ConfigDict(from_attributes=True)


class WikiPageArticleLinkBase(BaseModel):
    """Base schema for linking wiki pages to articles"""
    wiki_page_id: UUID
    article_id: UUID
    display_order: int = Field(0, description="Order to display this article in the wiki page")
    is_featured: bool = Field(False, description="Whether this article is featured on the wiki page")
    
    model_config = ConfigDict(from_attributes=True)


class WikiPageArticleLinkCreate(WikiPageArticleLinkBase):
    """Schema for creating a wiki page article link"""
    pass


class WikiPageArticleLinkUpdate(BaseModel):
    """Schema for updating a wiki page article link"""
    display_order: Optional[int] = None
    is_featured: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)


class WikiPageArticleLink(WikiPageArticleLinkBase):
    """Complete wiki page article link with database fields"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True) 