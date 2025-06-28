"""
Abstract Base Class for WikiPage Repositories
Handles wiki pages, articles, and page-article associations
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.schemas.wiki import (
    WikiPage, WikiPageCreate, WikiPageUpdate,
    WikiArticle, WikiArticleCreate, WikiArticleUpdate,
    WikiPageArticleLink, WikiPageArticleLinkCreate, WikiPageArticleLinkUpdate,
    WikiArchive, ArticleType
)


class AbstractWikiPageRepository(ABC):
    """Abstract interface for wiki page repository operations"""

    # WikiPage CRUD operations
    @abstractmethod
    async def get_wiki_page(self, wiki_page_id: UUID) -> WikiPage:
        """Get a wiki page by ID - returns empty page if not found"""
        ...

    @abstractmethod
    async def get_wiki_pages_by_creator(self, creator_id: UUID) -> List[WikiPage]:
        """Get all wiki pages created by a user"""
        ...

    @abstractmethod
    async def create_wiki_page(self, wiki_page_create: WikiPageCreate) -> WikiPage:
        """Create a new wiki page"""
        ...

    @abstractmethod
    async def update_wiki_page(self, wiki_page_id: UUID, wiki_page_update: WikiPageUpdate) -> Optional[WikiPage]:
        """Update an existing wiki page"""
        ...

    @abstractmethod
    async def delete_wiki_page(self, wiki_page_id: UUID) -> bool:
        """Delete a wiki page and all its article links"""
        ...

    # WikiArticle CRUD operations (articles are shared across wiki pages)
    @abstractmethod
    async def get_wiki_article(self, article_id: UUID) -> Optional[WikiArticle]:
        """Get a wiki article by ID"""
        ...

    @abstractmethod
    async def get_wiki_article_by_slug(self, slug: str) -> Optional[WikiArticle]:
        """Get a wiki article by slug"""
        ...

    @abstractmethod
    async def create_wiki_article(self, article_create: WikiArticleCreate) -> WikiArticle:
        """Create a new wiki article"""
        ...

    @abstractmethod
    async def update_wiki_article(self, article_id: UUID, article_update: WikiArticleUpdate) -> Optional[WikiArticle]:
        """Update an existing wiki article"""
        ...

    @abstractmethod
    async def delete_wiki_article(self, article_id: UUID) -> bool:
        """Delete a wiki article (only if not linked to any wiki pages)"""
        ...

    @abstractmethod
    async def create_wiki_articles_bulk(self, articles_create: List[WikiArticleCreate]) -> List[WikiArticle]:
        """Create multiple wiki articles in bulk"""
        ...

    # WikiPage-Article Link operations
    @abstractmethod
    async def get_wiki_page_articles(self, wiki_page_id: UUID, max_chapter: Optional[int] = None) -> List[WikiArticle]:
        """Get all articles for a wiki page, optionally filtered by chapter safety"""
        ...

    @abstractmethod
    async def get_article_wiki_pages(self, article_id: UUID) -> List[WikiPage]:
        """Get all wiki pages that contain a specific article"""
        ...

    @abstractmethod
    async def create_page_article_link(self, link_create: WikiPageArticleLinkCreate) -> WikiPageArticleLink:
        """Link an article to a wiki page"""
        ...

    @abstractmethod
    async def update_page_article_link(self, link_id: UUID, link_update: WikiPageArticleLinkUpdate) -> Optional[WikiPageArticleLink]:
        """Update a page-article link"""
        ...

    @abstractmethod
    async def delete_page_article_link(self, link_id: UUID) -> bool:
        """Remove an article from a wiki page"""
        ...

    # High-level operations
    @abstractmethod
    async def get_wiki_archive(self, wiki_page_id: UUID, max_chapter: int) -> Optional[WikiArchive]:
        """
        Get a complete wiki archive safe through a specific chapter
        
        Args:
            wiki_page_id: The wiki page ID
            max_chapter: Maximum chapter number to include
            
        Returns:
            Complete wiki archive or None if not found
        """
        ...

    @abstractmethod
    async def load_from_directory(self, wiki_directory_path: str, wiki_page_id: UUID) -> bool:
        """
        Load wiki articles from a directory structure into a wiki page
        
        Args:
            wiki_directory_path: Path to the wiki directory
            wiki_page_id: Wiki page to associate articles with
            
        Returns:
            True if successful, False otherwise
        """
        ...

    @abstractmethod
    async def save_to_directory(self, wiki_page_id: UUID, wiki_directory_path: str, max_chapter: Optional[int] = None) -> bool:
        """
        Save wiki page articles to a directory structure
        
        Args:
            wiki_page_id: Wiki page to save
            wiki_directory_path: Directory to save to
            max_chapter: Optional chapter limit for spoiler prevention
            
        Returns:
            True if successful, False otherwise
        """
        ...

    # Search operations
    @abstractmethod
    async def search_articles(
        self, 
        wiki_page_id: UUID,
        query: str, 
        max_chapter: Optional[int] = None,
        article_types: Optional[List[ArticleType]] = None,
        limit: int = 10
    ) -> List[WikiArticle]:
        """
        Search articles within a wiki page
        
        Args:
            wiki_page_id: Wiki page to search in
            query: Search query
            max_chapter: Optional maximum chapter number for filtering
            article_types: Optional list of article types to filter by
            limit: Maximum number of results
            
        Returns:
            List of matching articles
        """
        ... 