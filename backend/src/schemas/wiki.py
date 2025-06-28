"""
Wiki schemas for ShuScribe
Defines schemas for wiki articles, pages, and wiki-related processing
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema, TimestampSchema, UUIDSchema


class ArticleType(str, Enum):
    """Types of wiki articles"""
    MAIN = "main"           # Main story wiki page
    CHARACTER = "character"  # Character articles
    LOCATION = "location"    # Location/setting articles
    CONCEPT = "concept"      # Concepts, magic systems, etc.
    EVENT = "event"         # Important events
    TIMELINE = "timeline"    # Timeline/chronology articles


# Standalone Wiki Articles (not tied to specific stories)
class WikiArticleBase(BaseSchema):
    """Base wiki article schema - articles can be shared across stories"""
    title: str = Field(..., description="Human-readable title for wikilinks")
    slug: str = Field(..., description="URL-friendly unique identifier")
    article_type: ArticleType
    content: str = Field(..., description="Full article content in Markdown")
    preview: str = Field("", description="Short preview for tooltips")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Structured metadata about the entity")


class WikiArticleCreate(WikiArticleBase):
    """Schema for creating a wiki article"""
    pass


class WikiArticleUpdate(BaseSchema):
    """Schema for updating a wiki article"""
    title: Optional[str] = None
    content: Optional[str] = None
    preview: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class WikiArticle(WikiArticleBase, UUIDSchema, TimestampSchema):
    """Complete wiki article with database fields"""
    embedding: Optional[List[float]] = Field(None, description="Vector embedding for semantic search")


# Wiki Pages (each story has one or more wiki pages that link to articles)
class WikiPageBase(BaseSchema):
    """Base wiki page schema - contains articles for a specific story context"""
    title: str = Field("Untitled Wiki", description="Wiki page title (usually story title)")
    description: str = Field("", description="Description of this wiki page")
    is_public: bool = Field(False, description="Whether this wiki page is publicly accessible")
    safe_through_chapter: int = Field(0, description="Highest chapter number safe to read with this wiki")


class WikiPageCreate(WikiPageBase):
    """Schema for creating a wiki page"""
    creator_id: UUID


class WikiPageUpdate(BaseSchema):
    """Schema for updating a wiki page"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    safe_through_chapter: Optional[int] = None


class WikiPage(WikiPageBase, UUIDSchema, TimestampSchema):
    """Complete wiki page with database fields"""
    creator_id: UUID

    @classmethod
    def create_empty(cls, creator_id: UUID) -> 'WikiPage':
        """Create an empty wiki page instance"""
        return cls(
            title="",
            description="",
            is_public=False,
            safe_through_chapter=0,
            creator_id=creator_id,
            id=UUID(int=0),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )


# Note: WikiPageArticleLink classes moved to end of file to use article snapshots


# Wiki Archive Schemas (complete wikis safe through specific chapters)
class WikiArchiveMetadata(BaseSchema):
    """Metadata for a wiki archive safe through a specific chapter"""
    wiki_page_id: UUID
    wiki_page_title: str
    safe_through_chapter: int = Field(..., description="Highest chapter number safe to read with this wiki")
    total_articles: int
    generation_timestamp: datetime
    source_arc_id: Optional[UUID] = Field(None, description="Arc that generated this archive (for processing context)")
    source_arc_title: Optional[str] = Field(None, description="Title of the arc that generated this archive")


class WikiArchive(BaseSchema):
    """Complete wiki archive safe through a specific chapter"""
    metadata: WikiArchiveMetadata
    articles: List[WikiArticle]
    article_links: List['WikiPageArticleLink']  # Links with chapter safety info - forward reference
    file_structure: Dict[str, str] = Field(default_factory=dict, description="Map of article titles to file paths")
    
    def get_article_by_title(self, title: str) -> Optional[WikiArticle]:
        """Get article by title"""
        return next((article for article in self.articles if article.title == title), None)
    
    def get_article_by_slug(self, slug: str) -> Optional[WikiArticle]:
        """Get article by slug"""
        return next((article for article in self.articles if article.slug == slug), None)
    
    def get_articles_by_type(self, article_type: ArticleType) -> List[WikiArticle]:
        """Get all articles of a specific type"""
        return [article for article in self.articles if article.article_type == article_type]
    
    def get_safe_articles(self, through_chapter: int) -> List[WikiArticle]:
        """Get articles safe through a specific chapter"""
        # Note: This method needs to be updated when WikiArchive is refactored for snapshots
        # For now, return all articles as this is used with the old schema
        return self.articles


# Wiki Structure and Planning Schemas
class ArticlePlan(BaseSchema):
    """Plan for a single wiki article"""
    title: str
    article_type: ArticleType
    file_path: str = Field(..., description="Intended file path in wiki structure")
    preview: str = Field("", description="Brief description of planned content")
    structure: str = Field("", description="Planned article structure/outline")
    priority: int = Field(1, description="Processing priority (1=highest)")
    last_safe_chapter: int = Field(0, description="Last chapter this article is safe through")


class WikiPlan(BaseSchema):
    """Complete wiki planning structure"""
    wiki_page_id: UUID
    story_title: str
    arc_number: int
    arc_title: str
    articles: List[ArticlePlan]
    file_structure: Dict[str, Any] = Field(default_factory=dict, description="Directory structure for wiki files")
    processing_notes: str = Field("", description="Notes for article generation")


# Wiki Generation Request/Response Schemas
class WikiGenerationRequest(BaseSchema):
    """Request to generate wiki for a story"""
    story_id: UUID
    user_id: UUID
    provider: str
    model: str
    processing_mode: str = "fresh"  # fresh, update, reprocess
    arc_numbers: Optional[List[int]] = Field(None, description="Specific arcs to process (None = all)")


class WikiGenerationResponse(BaseSchema):
    """Response from wiki generation"""
    story_id: UUID
    wiki_page_id: UUID
    processing_status: str
    arcs_processed: List[int]
    total_articles_generated: int
    processing_time_seconds: float
    error_message: Optional[str] = None


# Search and Discovery Schemas
class WikiSearchResult(BaseSchema):
    """Result from wiki search"""
    article: WikiArticle
    relevance_score: float
    snippet: str = Field("", description="Relevant content snippet")
    wiki_page_titles: List[str] = Field(default_factory=list, description="Wiki pages that contain this article")


class WikiSearchRequest(BaseSchema):
    """Request for wiki search"""
    query: str
    wiki_page_id: Optional[UUID] = Field(None, description="Specific wiki page to search within")
    max_chapter: Optional[int] = Field(None, description="Maximum chapter to search through (spoiler prevention)")
    article_types: Optional[List[ArticleType]] = Field(None, description="Filter by article types")
    limit: int = Field(10, ge=1, le=50)


# Core Article (conceptual entity that can have multiple snapshots)
class ArticleBase(BaseSchema):
    """Base article schema - represents a conceptual entity (character, location, etc.)"""
    title: str = Field(..., description="Article title (e.g., 'Harry Potter', 'Hogwarts')")
    slug: str = Field(..., description="URL-friendly slug")
    article_type: ArticleType = Field(..., description="Type of article")
    
    # Metadata about the conceptual entity
    canonical_name: str = Field("", description="Canonical name if different from title")
    aliases: List[str] = Field(default_factory=list, description="Alternative names/spellings")
    tags: List[str] = Field(default_factory=list, description="Classification tags")


class ArticleCreate(ArticleBase):
    """Schema for creating a new conceptual article"""
    creator_id: UUID


class ArticleUpdate(BaseSchema):
    """Schema for updating a conceptual article"""
    title: Optional[str] = None
    canonical_name: Optional[str] = None
    aliases: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class Article(ArticleBase, UUIDSchema, TimestampSchema):
    """Complete conceptual article entity"""
    creator_id: UUID
    
    @classmethod
    def create_empty(cls) -> 'Article':
        """Create an empty article instance"""
        return cls(
            id=UUID(int=0),
            title="",
            slug="",
            article_type=ArticleType.MAIN,
            canonical_name="",
            creator_id=UUID(int=0),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )


# Article Snapshots (versioned content for specific story contexts)
class ArticleSnapshotBase(BaseSchema):
    """Base schema for article snapshots - specific versions of article content"""
    article_id: UUID = Field(..., description="Reference to the conceptual article")
    
    # Content for this specific snapshot
    content: str = Field(..., description="Markdown content for this version")
    preview: str = Field("", description="Brief preview/summary")
    
    # Context about when/why this snapshot was created
    last_safe_chapter: int = Field(0, description="Last chapter this snapshot is safe through")
    source_story_id: UUID = Field(..., description="Story that this snapshot was generated for")
    generation_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Context about how this snapshot was created")
    
    # Versioning information
    version_number: int = Field(1, description="Version number within this article")
    parent_snapshot_id: Optional[UUID] = Field(None, description="Previous snapshot this was based on")


class ArticleSnapshotCreate(ArticleSnapshotBase):
    """Schema for creating a new article snapshot"""
    pass


class ArticleSnapshotUpdate(BaseSchema):
    """Schema for updating an article snapshot"""
    content: Optional[str] = None
    preview: Optional[str] = None
    last_safe_chapter: Optional[int] = None
    generation_context: Optional[Dict[str, Any]] = None


class ArticleSnapshot(ArticleSnapshotBase, UUIDSchema, TimestampSchema):
    """Complete article snapshot with database fields"""
    
    @classmethod
    def create_empty(cls) -> 'ArticleSnapshot':
        """Create an empty snapshot instance"""
        return cls(
            id=UUID(int=0),
            article_id=UUID(int=0),
            content="",
            preview="",
            last_safe_chapter=0,
            source_story_id=UUID(int=0),
            version_number=1,
            parent_snapshot_id=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )


# Article-Story Associations (backlinking)
class ArticleStoryAssociationBase(BaseSchema):
    """Base schema for linking articles to stories they appear in"""
    article_id: UUID
    story_id: UUID
    first_mentioned_chapter: int = Field(0, description="First chapter where this article's subject appears")
    importance_level: int = Field(1, description="1=Critical, 2=Major, 3=Minor, 4=Reference")
    relationship_type: str = Field("appears_in", description="How this article relates to the story")


class ArticleStoryAssociationCreate(ArticleStoryAssociationBase):
    """Schema for creating article-story associations"""
    pass


class ArticleStoryAssociation(ArticleStoryAssociationBase, UUIDSchema, TimestampSchema):
    """Complete article-story association with database fields"""
    pass


# Updated WikiPage Article Links (now links to snapshots)
class WikiPageArticleLinkBase(BaseSchema):
    """Base schema for linking wiki pages to article snapshots"""
    wiki_page_id: UUID
    article_snapshot_id: UUID = Field(..., description="Links to specific snapshot, not base article")
    display_order: int = Field(0, description="Order to display this article in the wiki page")
    is_featured: bool = Field(False, description="Whether this article is featured on the wiki page")


class WikiPageArticleLinkCreate(WikiPageArticleLinkBase):
    """Schema for creating a wiki page article link"""
    pass


class WikiPageArticleLinkUpdate(BaseSchema):
    """Schema for updating a wiki page article link"""
    display_order: Optional[int] = None
    is_featured: Optional[bool] = None


class WikiPageArticleLink(WikiPageArticleLinkBase, UUIDSchema, TimestampSchema):
    """Complete wiki page article link with database fields"""
    pass
