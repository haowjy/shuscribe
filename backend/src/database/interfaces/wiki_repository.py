from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.schemas.db.wiki import (
    WikiArticle,
    WikiArticleCreate,
    WikiArticleUpdate,
    WikiArticleType,
    ArticleConnection,
    ArticleConnectionCreate,
    ChapterVersion,
    ChapterVersionCreate,
    ChapterVersionUpdate,
    CurrentVersion,
    CurrentVersionCreate,
    CurrentVersionUpdate,
)


class IWikiRepository(ABC):
    """Abstract interface for wiki repository - pure CRUD + simple queries"""

    # Wiki Article CRUD
    @abstractmethod
    async def create_article(self, article_data: WikiArticleCreate) -> WikiArticle:
        """Create a new wiki article"""
        pass

    @abstractmethod
    async def get_article(self, article_id: UUID) -> Optional[WikiArticle]:
        """Get a wiki article by ID"""
        pass

    @abstractmethod
    async def update_article(
        self, article_id: UUID, article_data: WikiArticleUpdate
    ) -> WikiArticle:
        """Update an existing wiki article"""
        pass

    @abstractmethod
    async def delete_article(self, article_id: UUID) -> bool:
        """Delete a wiki article"""
        pass

    # Simple Article Queries
    @abstractmethod
    async def get_articles_by_workspace(
        self,
        workspace_id: UUID,
        article_type: Optional[WikiArticleType] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[WikiArticle]:
        """Get wiki articles for a workspace, optionally filtered by type"""
        pass

    @abstractmethod
    async def get_article_by_title(
        self, workspace_id: UUID, title: str
    ) -> Optional[WikiArticle]:
        """Get article by title within a workspace"""
        pass

    @abstractmethod
    async def search_articles(
        self, workspace_id: UUID, query: str
    ) -> List[WikiArticle]:
        """Search articles by title and content"""
        pass

    # Chapter Version CRUD
    @abstractmethod
    async def create_chapter_version(
        self, version_data: ChapterVersionCreate
    ) -> ChapterVersion:
        """Create a chapter-specific version of an article"""
        pass

    @abstractmethod
    async def get_chapter_version(
        self, version_id: UUID
    ) -> Optional[ChapterVersion]:
        """Get a chapter version by ID"""
        pass

    @abstractmethod
    async def update_chapter_version(
        self, version_id: UUID, version_data: ChapterVersionUpdate
    ) -> ChapterVersion:
        """Update a chapter version"""
        pass

    @abstractmethod
    async def delete_chapter_version(self, version_id: UUID) -> bool:
        """Delete a chapter version"""
        pass

    # Simple Chapter Version Queries
    @abstractmethod
    async def get_chapter_versions_by_article(
        self, article_id: UUID
    ) -> List[ChapterVersion]:
        """Get all chapter versions for an article"""
        pass

    @abstractmethod
    async def get_chapter_version_by_article_and_chapter(
        self, article_id: UUID, chapter: int
    ) -> Optional[ChapterVersion]:
        """Get chapter version safe through the specified chapter (highest version <= chapter)"""
        pass
    
    @abstractmethod
    async def get_exact_chapter_version(
        self, article_id: UUID, chapter: int
    ) -> Optional[ChapterVersion]:
        """Get chapter version with exact chapter number match"""
        pass

    @abstractmethod
    async def get_chapter_versions_by_workspace(
        self, workspace_id: UUID, chapter: Optional[int] = None
    ) -> List[ChapterVersion]:
        """Get chapter versions for workspace, optionally filtered by chapter"""
        pass

    # Current Version CRUD
    @abstractmethod
    async def create_current_version(
        self, version_data: CurrentVersionCreate
    ) -> CurrentVersion:
        """Create a current version for an article"""
        pass

    @abstractmethod
    async def get_current_version(self, article_id: UUID) -> Optional[CurrentVersion]:
        """Get the current working version of an article"""
        pass

    @abstractmethod
    async def update_current_version(
        self, article_id: UUID, version_data: CurrentVersionUpdate
    ) -> CurrentVersion:
        """Update the current version of an article"""
        pass

    @abstractmethod
    async def delete_current_version(self, article_id: UUID) -> bool:
        """Delete the current version of an article"""
        pass

    # Simple Current Version Queries
    @abstractmethod
    async def get_current_versions_by_workspace(
        self, workspace_id: UUID
    ) -> List[CurrentVersion]:
        """Get all current versions for a workspace"""
        pass

    # Article Connection CRUD
    @abstractmethod
    async def create_connection(
        self, connection_data: ArticleConnectionCreate
    ) -> ArticleConnection:
        """Create a connection between articles"""
        pass

    @abstractmethod
    async def get_connection(self, connection_id: UUID) -> Optional[ArticleConnection]:
        """Get an article connection by ID"""
        pass

    @abstractmethod
    async def delete_connection(self, connection_id: UUID) -> bool:
        """Delete an article connection"""
        pass

    # Simple Connection Queries
    @abstractmethod
    async def get_connections_by_article(
        self, article_id: UUID, connection_type: Optional[str] = None
    ) -> List[ArticleConnection]:
        """Get connections for an article, optionally filtered by type"""
        pass

    @abstractmethod
    async def get_connections_by_workspace(
        self, workspace_id: UUID
    ) -> List[ArticleConnection]:
        """Get all connections in a workspace"""
        pass

    # Bulk Operations
    @abstractmethod
    async def bulk_create_chapter_versions(
        self, versions: List[ChapterVersionCreate]
    ) -> List[ChapterVersion]:
        """Create multiple chapter versions in one operation"""
        pass

    @abstractmethod
    async def bulk_create_articles(
        self, articles: List[WikiArticleCreate]
    ) -> List[WikiArticle]:
        """Create multiple articles in one operation"""
        pass