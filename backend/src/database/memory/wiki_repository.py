"""Memory-based wiki repository implementation for testing and development."""
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from datetime import UTC, datetime

from src.database.interfaces.wiki_repository import IWikiRepository
from src.schemas.db.wiki import (
    WikiArticle,
    WikiArticleCreate,
    WikiArticleUpdate,
    WikiPage,
    WikiPageCreate,
    WikiPageUpdate,
    WikiPageArticleLink,
    WikiPageArticleLinkCreate,
    WikiPageArticleLinkUpdate,
    ChapterVersion,
    ChapterVersionCreate,
    ChapterVersionUpdate,
    CurrentVersion,
    CurrentVersionCreate,
    CurrentVersionUpdate,
    ArticleConnection,
    ArticleConnectionCreate,
    WikiArticleType,
)


class MemoryWikiRepository(IWikiRepository):
    """In-memory implementation of wiki repository for testing."""
    
    def __init__(self):
        self._articles: Dict[UUID, WikiArticle] = {}
        self._wiki_pages: Dict[UUID, WikiPage] = {}
        self._page_article_links: Dict[UUID, WikiPageArticleLink] = {}
        self._chapter_versions: Dict[UUID, ChapterVersion] = {}
        self._current_versions: Dict[UUID, CurrentVersion] = {}  # article_id -> CurrentVersion
        self._article_connections: Dict[UUID, ArticleConnection] = {}
    
    # Wiki Article CRUD
    async def create_article(self, article_data: WikiArticleCreate) -> WikiArticle:
        """Create a new wiki article"""
        article_id = uuid4()
        now = datetime.now(UTC)
        
        article = WikiArticle(
            id=article_id,
            workspace_id=article_data.workspace_id,
            title=article_data.title,
            article_type=article_data.article_type,
            content=article_data.content,
            summary=article_data.summary,
            tags=article_data.tags,
            safe_through_chapter=article_data.safe_through_chapter,
            metadata=article_data.metadata,
            created_at=now,
            updated_at=now
        )
        
        self._articles[article_id] = article
        return article
    
    async def get_article(self, article_id: UUID) -> Optional[WikiArticle]:
        """Get a specific article by ID"""
        return self._articles.get(article_id)
    
    async def update_article(
        self, article_id: UUID, article_data: WikiArticleUpdate
    ) -> WikiArticle:
        """Update an existing article"""
        article = self._articles.get(article_id)
        if not article:
            raise ValueError(f"Article {article_id} not found")
        
        update_dict = article_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        updated_article = article.model_copy(update=update_dict)
        self._articles[article_id] = updated_article
        return updated_article
    
    async def delete_article(self, article_id: UUID) -> bool:
        """Delete an article"""
        if article_id in self._articles:
            # Clean up related data
            # Remove current version
            self._current_versions.pop(article_id, None)
            
            # Remove chapter versions
            versions_to_delete = [
                v_id for v_id, version in self._chapter_versions.items() 
                if version.article_id == article_id
            ]
            for v_id in versions_to_delete:
                del self._chapter_versions[v_id]
            
            # Remove connections
            connections_to_delete = [
                c_id for c_id, conn in self._article_connections.items()
                if conn.from_article_id == article_id or conn.to_article_id == article_id
            ]
            for c_id in connections_to_delete:
                del self._article_connections[c_id]
            
            # Remove page links
            links_to_delete = [
                l_id for l_id, link in self._page_article_links.items()
                if link.article_id == article_id
            ]
            for l_id in links_to_delete:
                del self._page_article_links[l_id]
            
            del self._articles[article_id]
            return True
        return False
    
    # Simple Article Queries
    async def get_articles_by_workspace(
        self, workspace_id: UUID, article_type: Optional[WikiArticleType] = None
    ) -> List[WikiArticle]:
        """Get articles for a workspace, optionally filtered by type"""
        articles = []
        for article in self._articles.values():
            if article.workspace_id == workspace_id:
                if article_type is None or article.article_type == article_type:
                    articles.append(article)
        
        # Sort by title for consistent ordering
        articles.sort(key=lambda a: a.title.lower())
        return articles
    
    async def get_article_by_title(
        self, workspace_id: UUID, title: str
    ) -> Optional[WikiArticle]:
        """Get an article by title within a workspace"""
        for article in self._articles.values():
            if (article.workspace_id == workspace_id and 
                article.title.lower() == title.lower()):
                return article
        return None
    
    async def search_articles(
        self, workspace_id: UUID, query: str
    ) -> List[WikiArticle]:
        """Search articles by title and content"""
        query_lower = query.lower()
        matching_articles = []
        
        for article in self._articles.values():
            if article.workspace_id == workspace_id:
                # Search in title, content, and tags
                if (query_lower in article.title.lower() or 
                    query_lower in article.content.lower() or
                    any(query_lower in tag.lower() for tag in article.tags)):
                    matching_articles.append(article)
        
        matching_articles.sort(key=lambda a: a.title.lower())
        return matching_articles
    
    async def get_articles_by_chapter_safety(
        self, workspace_id: UUID, max_chapter: int
    ) -> List[WikiArticle]:
        """Get articles safe through a specific chapter"""
        safe_articles = []
        for article in self._articles.values():
            if article.workspace_id == workspace_id:
                if (article.safe_through_chapter is None or 
                    article.safe_through_chapter <= max_chapter):
                    safe_articles.append(article)
        
        safe_articles.sort(key=lambda a: a.title.lower())
        return safe_articles
    
    # Wiki Page CRUD
    async def create_wiki_page(self, page_data: WikiPageCreate) -> WikiPage:
        """Create a new wiki page"""
        page_id = uuid4()
        now = datetime.now(UTC)
        
        page = WikiPage(
            id=page_id,
            workspace_id=page_data.workspace_id,
            title=page_data.title,
            description=page_data.description,
            is_public=page_data.is_public,
            safe_through_chapter=page_data.safe_through_chapter,
            created_at=now,
            updated_at=now
        )
        
        self._wiki_pages[page_id] = page
        return page
    
    async def get_wiki_page(self, page_id: UUID) -> Optional[WikiPage]:
        """Get a specific wiki page by ID"""
        return self._wiki_pages.get(page_id)
    
    async def update_wiki_page(
        self, page_id: UUID, page_data: WikiPageUpdate
    ) -> WikiPage:
        """Update an existing wiki page"""
        page = self._wiki_pages.get(page_id)
        if not page:
            raise ValueError(f"Wiki page {page_id} not found")
        
        update_dict = page_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        updated_page = page.model_copy(update=update_dict)
        self._wiki_pages[page_id] = updated_page
        return updated_page
    
    async def delete_wiki_page(self, page_id: UUID) -> bool:
        """Delete a wiki page"""
        if page_id in self._wiki_pages:
            # Clean up page-article links
            links_to_delete = [
                l_id for l_id, link in self._page_article_links.items()
                if link.wiki_page_id == page_id
            ]
            for l_id in links_to_delete:
                del self._page_article_links[l_id]
            
            del self._wiki_pages[page_id]
            return True
        return False
    
    async def get_wiki_pages_by_workspace(self, workspace_id: UUID) -> List[WikiPage]:
        """Get all wiki pages for a workspace"""
        pages = []
        for page in self._wiki_pages.values():
            if page.workspace_id == workspace_id:
                pages.append(page)
        
        # Sort by creation date
        pages.sort(key=lambda p: p.created_at)
        return pages
    
    # Page-Article Link CRUD
    async def create_page_article_link(
        self, link_data: WikiPageArticleLinkCreate
    ) -> WikiPageArticleLink:
        """Create a link between wiki page and article"""
        link_id = uuid4()
        now = datetime.now(UTC)
        
        link = WikiPageArticleLink(
            id=link_id,
            wiki_page_id=link_data.wiki_page_id,
            article_id=link_data.article_id,
            display_order=link_data.display_order,
            is_featured=link_data.is_featured,
            created_at=now,
            updated_at=now
        )
        
        self._page_article_links[link_id] = link
        return link
    
    async def get_page_article_link(self, link_id: UUID) -> Optional[WikiPageArticleLink]:
        """Get a specific page-article link by ID"""
        return self._page_article_links.get(link_id)
    
    async def update_page_article_link(
        self, link_id: UUID, link_data: WikiPageArticleLinkUpdate
    ) -> WikiPageArticleLink:
        """Update an existing page-article link"""
        link = self._page_article_links.get(link_id)
        if not link:
            raise ValueError(f"Page-article link {link_id} not found")
        
        update_dict = link_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        updated_link = link.model_copy(update=update_dict)
        self._page_article_links[link_id] = updated_link
        return updated_link
    
    async def delete_page_article_link(self, link_id: UUID) -> bool:
        """Delete a page-article link"""
        if link_id in self._page_article_links:
            del self._page_article_links[link_id]
            return True
        return False
    
    async def get_page_article_links_by_page(
        self, page_id: UUID
    ) -> List[WikiPageArticleLink]:
        """Get all article links for a page"""
        links = []
        for link in self._page_article_links.values():
            if link.wiki_page_id == page_id:
                links.append(link)
        
        # Sort by display order
        links.sort(key=lambda l: l.display_order)
        return links
    
    # Chapter Version CRUD
    async def create_chapter_version(
        self, version_data: ChapterVersionCreate
    ) -> ChapterVersion:
        """Create a new chapter version"""
        version_id = uuid4()
        now = datetime.now(UTC)
        
        version = ChapterVersion(
            id=version_id,
            article_id=version_data.article_id,
            safe_through_chapter=version_data.safe_through_chapter,
            content=version_data.content,
            summary=version_data.summary,
            ai_guidance=version_data.ai_guidance,
            created_at=now,
            updated_at=now
        )
        
        self._chapter_versions[version_id] = version
        return version
    
    async def get_chapter_version(self, version_id: UUID) -> Optional[ChapterVersion]:
        """Get a specific chapter version by ID"""
        return self._chapter_versions.get(version_id)
    
    async def update_chapter_version(
        self, version_id: UUID, version_data: ChapterVersionUpdate
    ) -> ChapterVersion:
        """Update an existing chapter version"""
        version = self._chapter_versions.get(version_id)
        if not version:
            raise ValueError(f"Chapter version {version_id} not found")
        
        update_dict = version_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        updated_version = version.model_copy(update=update_dict)
        self._chapter_versions[version_id] = updated_version
        return updated_version
    
    async def delete_chapter_version(self, version_id: UUID) -> bool:
        """Delete a chapter version"""
        if version_id in self._chapter_versions:
            del self._chapter_versions[version_id]
            return True
        return False
    
    async def get_chapter_versions_by_article(
        self, article_id: UUID
    ) -> List[ChapterVersion]:
        """Get all chapter versions for an article"""
        versions = []
        for version in self._chapter_versions.values():
            if version.article_id == article_id:
                versions.append(version)
        
        # Sort by safe_through_chapter descending (most recent first)
        versions.sort(key=lambda v: v.safe_through_chapter, reverse=True)
        return versions
    
    # Current Version CRUD
    async def create_current_version(
        self, version_data: CurrentVersionCreate
    ) -> CurrentVersion:
        """Create or update current version for an article"""
        now = datetime.now(UTC)
        
        # Check if current version already exists
        existing_version = self._current_versions.get(version_data.article_id)
        if existing_version:
            # Update existing
            update_dict = version_data.model_dump()
            update_dict['updated_at'] = now
            updated_version = existing_version.model_copy(update=update_dict)
            self._current_versions[version_data.article_id] = updated_version
            return updated_version
        else:
            # Create new
            version_id = uuid4()
            version = CurrentVersion(
                id=version_id,
                article_id=version_data.article_id,
                content=version_data.content,
                user_notes=version_data.user_notes,
                ai_guidance=version_data.ai_guidance,
                is_generated=version_data.is_generated,
                created_at=now,
                updated_at=now
            )
            
            self._current_versions[version_data.article_id] = version
            return version
    
    async def get_current_version(self, article_id: UUID) -> Optional[CurrentVersion]:
        """Get current version for an article"""
        return self._current_versions.get(article_id)
    
    async def update_current_version(
        self, article_id: UUID, version_data: CurrentVersionUpdate
    ) -> CurrentVersion:
        """Update current version for an article"""
        version = self._current_versions.get(article_id)
        if not version:
            raise ValueError(f"Current version not found for article {article_id}")
        
        update_dict = version_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        updated_version = version.model_copy(update=update_dict)
        self._current_versions[article_id] = updated_version
        return updated_version
    
    async def delete_current_version(self, article_id: UUID) -> bool:
        """Delete current version for an article"""
        if article_id in self._current_versions:
            del self._current_versions[article_id]
            return True
        return False
    
    # Article Connection CRUD
    async def create_article_connection(
        self, connection_data: ArticleConnectionCreate
    ) -> ArticleConnection:
        """Create a connection between articles"""
        connection_id = uuid4()
        now = datetime.now(UTC)
        
        connection = ArticleConnection(
            id=connection_id,
            from_article_id=connection_data.from_article_id,
            to_article_id=connection_data.to_article_id,
            connection_type=connection_data.connection_type,
            description=connection_data.description,
            strength=connection_data.strength,
            created_at=now,
            updated_at=now
        )
        
        self._article_connections[connection_id] = connection
        return connection
    
    async def get_article_connection(self, connection_id: UUID) -> Optional[ArticleConnection]:
        """Get a specific article connection by ID"""
        return self._article_connections.get(connection_id)
    
    async def delete_article_connection(self, connection_id: UUID) -> bool:
        """Delete an article connection"""
        if connection_id in self._article_connections:
            del self._article_connections[connection_id]
            return True
        return False
    
    async def get_article_connections(
        self, article_id: UUID, include_incoming: bool = True
    ) -> List[ArticleConnection]:
        """Get all connections for an article"""
        connections = []
        for connection in self._article_connections.values():
            if connection.from_article_id == article_id:
                connections.append(connection)
            elif include_incoming and connection.to_article_id == article_id:
                connections.append(connection)
        
        # Sort by strength descending
        connections.sort(key=lambda c: c.strength, reverse=True)
        return connections
    
    # Missing methods from interface
    async def get_chapter_version_by_article_and_chapter(
        self, article_id: UUID, chapter_number: int
    ) -> Optional[ChapterVersion]:
        """Get chapter version safe through the specified chapter (highest version <= chapter_number)"""
        matching_versions = []
        for version in self._chapter_versions.values():
            if (version.article_id == article_id and 
                version.safe_through_chapter <= chapter_number):
                matching_versions.append(version)
        
        if not matching_versions:
            return None
        
        # Return the version with the highest safe_through_chapter
        return max(matching_versions, key=lambda v: v.safe_through_chapter)
    
    async def get_exact_chapter_version(
        self, article_id: UUID, chapter_number: int
    ) -> Optional[ChapterVersion]:
        """Get chapter version with exact chapter number match"""
        for version in self._chapter_versions.values():
            if (version.article_id == article_id and 
                version.safe_through_chapter == chapter_number):
                return version
        return None
    
    async def get_chapter_versions_by_workspace(
        self, workspace_id: UUID
    ) -> List[ChapterVersion]:
        """Get all chapter versions for a workspace"""
        versions = []
        for version in self._chapter_versions.values():
            # Need to get the article to check workspace
            article = self._articles.get(version.article_id)
            if article and article.workspace_id == workspace_id:
                versions.append(version)
        
        versions.sort(key=lambda v: v.safe_through_chapter, reverse=True)
        return versions
    
    async def get_current_versions_by_workspace(
        self, workspace_id: UUID
    ) -> List[CurrentVersion]:
        """Get all current versions for a workspace"""
        versions = []
        for version in self._current_versions.values():
            # Need to get the article to check workspace
            article = self._articles.get(version.article_id)
            if article and article.workspace_id == workspace_id:
                versions.append(version)
        
        versions.sort(key=lambda v: v.created_at, reverse=True)
        return versions
    
    async def create_connection(
        self, connection_data: ArticleConnectionCreate
    ) -> ArticleConnection:
        """Create a connection between articles (alias for create_article_connection)"""
        return await self.create_article_connection(connection_data)
    
    async def get_connection(self, connection_id: UUID) -> Optional[ArticleConnection]:
        """Get a connection by ID (alias for get_article_connection)"""
        return await self.get_article_connection(connection_id)
    
    async def delete_connection(self, connection_id: UUID) -> bool:
        """Delete a connection (alias for delete_article_connection)"""
        return await self.delete_article_connection(connection_id)
    
    async def get_connections_by_article(
        self, article_id: UUID
    ) -> List[ArticleConnection]:
        """Get connections for an article (alias for get_article_connections)"""
        return await self.get_article_connections(article_id, include_incoming=True)
    
    async def get_connections_by_workspace(
        self, workspace_id: UUID
    ) -> List[ArticleConnection]:
        """Get all connections for a workspace"""
        connections = []
        for connection in self._article_connections.values():
            # Check if either article belongs to this workspace
            from_article = self._articles.get(connection.from_article_id)
            to_article = self._articles.get(connection.to_article_id)
            
            if ((from_article and from_article.workspace_id == workspace_id) or
                (to_article and to_article.workspace_id == workspace_id)):
                connections.append(connection)
        
        connections.sort(key=lambda c: c.strength, reverse=True)
        return connections
    
    # Bulk Operations
    async def bulk_create_articles(
        self, articles: List[WikiArticleCreate]
    ) -> List[WikiArticle]:
        """Create multiple articles in one operation"""
        created_articles = []
        for article_data in articles:
            article = await self.create_article(article_data)
            created_articles.append(article)
        return created_articles
    
    async def bulk_create_chapter_versions(
        self, versions: List[ChapterVersionCreate]
    ) -> List[ChapterVersion]:
        """Create multiple chapter versions in one operation"""
        created_versions = []
        for version_data in versions:
            version = await self.create_chapter_version(version_data)
            created_versions.append(version)
        return created_versions