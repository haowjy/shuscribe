"""
Wiki Repository Interface

Abstract interface for wiki operations including articles, versioning, and connections.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.database.models.wiki import (
    WikiArticle, WikiArticleCreate, WikiArticleUpdate,
    ChapterVersion, CurrentVersion, ArticleConnection
)


class IWikiRepository(ABC):
    """Abstract interface for wiki repository"""

    # Article operations
    @abstractmethod
    async def get_article(self, id: UUID) -> Optional[WikiArticle]:
        """Retrieve an article by ID"""
        pass

    @abstractmethod
    async def get_articles_by_workspace(self, workspace_id: UUID) -> List[WikiArticle]:
        """Get all articles for a workspace"""
        pass

    @abstractmethod
    async def get_articles_by_type(self, workspace_id: UUID, article_type: str) -> List[WikiArticle]:
        """Get articles by type (character, location, etc.)"""
        pass

    @abstractmethod
    async def create_article(self, workspace_id: UUID, article_data: WikiArticleCreate) -> WikiArticle:
        """Create a new wiki article"""
        pass
    
    @abstractmethod
    async def update_article(self, article_id: UUID, article_data: WikiArticleUpdate) -> WikiArticle:
        """Update an existing article"""
        pass

    @abstractmethod
    async def delete_article(self, article_id: UUID) -> bool:
        """Delete an article"""
        pass

    # Chapter versioning
    @abstractmethod
    async def create_chapter_version(
        self, 
        article_id: UUID, 
        content: str, 
        safe_through_chapter: int,
        **metadata
    ) -> ChapterVersion:
        """Create a new chapter version for an article"""
        pass

    @abstractmethod
    async def get_version_for_chapter(
        self, 
        article_id: UUID, 
        chapter_number: int
    ) -> Optional[ChapterVersion]:
        """Get the appropriate version for a specific chapter"""
        pass

    @abstractmethod
    async def get_all_versions(self, article_id: UUID) -> List[ChapterVersion]:
        """Get all chapter versions for an article"""
        pass

    # Current version management
    @abstractmethod
    async def create_current_version(
        self, 
        article_id: UUID, 
        content: str,
        user_notes: str = ""
    ) -> CurrentVersion:
        """Create or update current working version"""
        pass

    @abstractmethod
    async def get_current_version(self, article_id: UUID) -> Optional[CurrentVersion]:
        """Get current working version"""
        pass

    @abstractmethod
    async def update_current_version(
        self, 
        article_id: UUID, 
        content: Optional[str] = None,
        user_notes: Optional[str] = None,
        **updates
    ) -> CurrentVersion:
        """Update current working version"""
        pass

    # Article connections
    @abstractmethod
    async def create_connection(
        self,
        from_article_id: UUID,
        to_article_id: UUID,
        connection_type: str = "related",
        strength: float = 1.0,
        context: Optional[str] = None
    ) -> ArticleConnection:
        """Create connection between articles"""
        pass

    @abstractmethod
    async def get_connections_from(self, article_id: UUID) -> List[ArticleConnection]:
        """Get all connections from an article"""
        pass

    @abstractmethod
    async def get_connections_to(self, article_id: UUID) -> List[ArticleConnection]:
        """Get all connections to an article"""
        pass

    @abstractmethod
    async def delete_connection(self, from_article_id: UUID, to_article_id: UUID) -> bool:
        """Delete connection between articles"""
        pass 