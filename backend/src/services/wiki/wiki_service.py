"""
Wiki Service - Business logic for wiki articles, versioning, and connections.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from src.database.interfaces.wiki_repository import IWikiRepository
from src.database.interfaces.workspace_repository import IWorkspaceRepository
from src.schemas.db.wiki import (
    WikiArticle, WikiArticleCreate, WikiArticleUpdate, WikiArticleType,
    WikiPage, WikiPageCreate, WikiPageUpdate,
    WikiPageArticleLink, WikiPageArticleLinkCreate, WikiPageArticleLinkUpdate,
    ChapterVersion, ChapterVersionCreate, ChapterVersionUpdate,
    CurrentVersion, CurrentVersionCreate, CurrentVersionUpdate,
    ArticleConnection, ArticleConnectionCreate
)


class WikiService:
    """Service layer for wiki management with business logic."""
    
    def __init__(
        self, 
        wiki_repository: IWikiRepository,
        workspace_repository: IWorkspaceRepository
    ):
        self.wiki_repository = wiki_repository
        self.workspace_repository = workspace_repository
    
    # Wiki Article Management
    async def create_article(self, article_data: WikiArticleCreate) -> WikiArticle:
        """Create a new wiki article with validation."""
        # Verify workspace exists
        workspace = await self.workspace_repository.get_workspace(article_data.workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {article_data.workspace_id} not found")
        
        # Check for duplicate titles within workspace
        existing_article = await self.wiki_repository.get_article_by_title(
            article_data.workspace_id, article_data.title
        )
        if existing_article:
            raise ValueError(f"Article '{article_data.title}' already exists in workspace")
        
        # Create the article
        article = await self.wiki_repository.create_article(article_data)
        
        # Create initial current version
        current_version_data = CurrentVersionCreate(
            article_id=article.id,
            content=article.content,
            user_notes="",
            ai_guidance="",
            is_generated=True
        )
        await self.wiki_repository.create_current_version(current_version_data)
        
        return article
    
    async def get_article(self, article_id: UUID) -> Optional[WikiArticle]:
        """Get article by ID."""
        return await self.wiki_repository.get_article(article_id)
    
    async def get_article_by_title(self, workspace_id: UUID, title: str) -> Optional[WikiArticle]:
        """Get article by title within workspace."""
        return await self.wiki_repository.get_article_by_title(workspace_id, title)
    
    async def update_article(self, article_id: UUID, article_data: WikiArticleUpdate) -> WikiArticle:
        """Update article with validation."""
        # Verify article exists
        existing_article = await self.wiki_repository.get_article(article_id)
        if not existing_article:
            raise ValueError(f"Article {article_id} not found")
        
        # Check for title conflicts if title is being changed
        if article_data.title and article_data.title != existing_article.title:
            existing_by_title = await self.wiki_repository.get_article_by_title(
                existing_article.workspace_id, article_data.title
            )
            if existing_by_title:
                raise ValueError(f"Article '{article_data.title}' already exists in workspace")
        
        # Update the article
        updated_article = await self.wiki_repository.update_article(article_id, article_data)
        
        # Update current version if content changed
        if article_data.content:
            current_version = await self.wiki_repository.get_current_version(article_id)
            if current_version:
                version_update = CurrentVersionUpdate(
                    content=article_data.content,
                    is_generated=False  # Manual edit
                )
                await self.wiki_repository.update_current_version(article_id, version_update)
        
        return updated_article
    
    async def delete_article(self, article_id: UUID) -> bool:
        """Delete article and cleanup related data."""
        # Verify article exists
        existing_article = await self.wiki_repository.get_article(article_id)
        if not existing_article:
            return False
        
        # Repository handles cleanup of related data
        return await self.wiki_repository.delete_article(article_id)
    
    async def get_articles_by_workspace(
        self, workspace_id: UUID, article_type: Optional[WikiArticleType] = None
    ) -> List[WikiArticle]:
        """Get articles for a workspace, optionally filtered by type."""
        return await self.wiki_repository.get_articles_by_workspace(workspace_id, article_type)
    
    async def search_articles(self, workspace_id: UUID, query: str) -> List[WikiArticle]:
        """Search articles by title, content, and tags."""
        return await self.wiki_repository.search_articles(workspace_id, query)
    
    async def get_articles_by_tags(self, workspace_id: UUID, tags: List[str]) -> List[WikiArticle]:
        """Get articles that have any of the specified tags."""
        all_articles = await self.wiki_repository.get_articles_by_workspace(workspace_id)
        matching_articles = []
        
        for article in all_articles:
            # Check if article has any of the requested tags
            if any(tag in article.tags for tag in tags):
                matching_articles.append(article)
        
        # Sort by title for consistent ordering
        matching_articles.sort(key=lambda a: a.title.lower())
        return matching_articles
    
    async def get_articles_safe_through_chapter(
        self, workspace_id: UUID, max_chapter: int
    ) -> List[WikiArticle]:
        """Get articles that are safe to read through a specific chapter."""
        # Filter articles by safety through repository query
        articles = await self.wiki_repository.get_articles_by_workspace(workspace_id)
        return [a for a in articles if a.safe_through_chapter is None or a.safe_through_chapter <= max_chapter]
    
    # Chapter Versioning
    async def create_chapter_version(
        self, article_id: UUID, chapter_number: int, content: str, summary: str = ""
    ) -> ChapterVersion:
        """Create a chapter-specific version of an article."""
        # Verify article exists
        article = await self.wiki_repository.get_article(article_id)
        if not article:
            raise ValueError(f"Article {article_id} not found")
        
        # Check if version already exists for this chapter
        existing_version = await self.wiki_repository.get_exact_chapter_version(
            article_id, chapter_number
        )
        if existing_version:
            raise ValueError(f"Chapter version {chapter_number} already exists for article {article_id}")
        
        version_data = ChapterVersionCreate(
            article_id=article_id,
            safe_through_chapter=chapter_number,
            content=content,
            summary=summary,
            ai_guidance=""
        )
        
        return await self.wiki_repository.create_chapter_version(version_data)
    
    async def get_article_at_chapter(
        self, article_id: UUID, chapter_number: int
    ) -> Optional[ChapterVersion]:
        """Get the version of an article safe through a specific chapter."""
        return await self.wiki_repository.get_chapter_version_by_article_and_chapter(
            article_id, chapter_number
        )
    
    async def get_chapter_versions(self, article_id: UUID) -> List[ChapterVersion]:
        """Get all chapter versions for an article."""
        return await self.wiki_repository.get_chapter_versions_by_article(article_id)
    
    async def update_current_version(
        self, article_id: UUID, content: str, user_notes: str = ""
    ) -> CurrentVersion:
        """Update the living current version of an article."""
        current_version = await self.wiki_repository.get_current_version(article_id)
        if not current_version:
            # Create if doesn't exist
            version_data = CurrentVersionCreate(
                article_id=article_id,
                content=content,
                user_notes=user_notes,
                ai_guidance="",
                is_generated=False
            )
            return await self.wiki_repository.create_current_version(version_data)
        else:
            # Update existing
            version_update = CurrentVersionUpdate(
                content=content,
                user_notes=user_notes,
                is_generated=False
            )
            return await self.wiki_repository.update_current_version(article_id, version_update)
    
    # Article Connections
    async def create_connection(
        self, from_article_id: UUID, to_article_id: UUID, 
        connection_type: str, description: str = "", strength: float = 1.0
    ) -> ArticleConnection:
        """Create a connection between two articles."""
        # Verify both articles exist
        from_article = await self.wiki_repository.get_article(from_article_id)
        to_article = await self.wiki_repository.get_article(to_article_id)
        
        if not from_article:
            raise ValueError(f"From article {from_article_id} not found")
        if not to_article:
            raise ValueError(f"To article {to_article_id} not found")
        
        # Prevent self-connections
        if from_article_id == to_article_id:
            raise ValueError("Cannot create connection from article to itself")
        
        connection_data = ArticleConnectionCreate(
            from_article_id=from_article_id,
            to_article_id=to_article_id,
            connection_type=connection_type,
            description=description,
            strength=strength
        )
        
        return await self.wiki_repository.create_connection(connection_data)
    
    async def get_article_connections(
        self, article_id: UUID, include_incoming: bool = True
    ) -> List[ArticleConnection]:
        """Get all connections for an article."""
        return await self.wiki_repository.get_connections_by_article(article_id)
    
    async def delete_connection(self, connection_id: UUID) -> bool:
        """Delete an article connection."""
        return await self.wiki_repository.delete_connection(connection_id)
    
    # Wiki Pages (Collections) - Not implemented in current interface
    async def create_wiki_page(self, page_data: WikiPageCreate) -> WikiPage:
        """Create a new wiki page (collection of articles)."""
        raise NotImplementedError("Wiki pages not implemented in current repository interface")
    
    async def add_article_to_page(
        self, page_id: UUID, article_id: UUID, display_order: int = 0, is_featured: bool = False
    ) -> WikiPageArticleLink:
        """Add an article to a wiki page."""
        raise NotImplementedError("Wiki page links not implemented in current repository interface")
    
    # Bulk Operations
    async def bulk_create_articles(
        self, articles: List[WikiArticleCreate]
    ) -> List[WikiArticle]:
        """Create multiple articles efficiently."""
        if not articles:
            return []
        
        # Get workspace_id from first article (all should have same workspace)
        workspace_id = articles[0].workspace_id
        
        # Verify workspace exists
        workspace = await self.workspace_repository.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        # Verify all articles are for the same workspace
        for article_data in articles:
            if article_data.workspace_id != workspace_id:
                raise ValueError("All articles must be for the same workspace")
        
        # Check for duplicate titles
        existing_articles = await self.wiki_repository.get_articles_by_workspace(workspace_id)
        existing_titles = {a.title.lower() for a in existing_articles}
        
        for article_data in articles:
            if article_data.title.lower() in existing_titles:
                raise ValueError(f"Article '{article_data.title}' already exists in workspace")
        
        return await self.wiki_repository.bulk_create_articles(articles)
    
    async def bulk_create_chapter_versions(
        self, versions: List[ChapterVersionCreate]
    ) -> List[ChapterVersion]:
        """Create multiple chapter versions efficiently."""
        # Verify all articles exist
        article_ids = {v.article_id for v in versions}
        for article_id in article_ids:
            article = await self.wiki_repository.get_article(article_id)
            if not article:
                raise ValueError(f"Article {article_id} not found")
        
        return await self.wiki_repository.bulk_create_chapter_versions(versions)
    
    # Analytics and Statistics
    async def get_wiki_statistics(self, workspace_id: UUID) -> Dict[str, Any]:
        """Get comprehensive wiki statistics for a workspace."""
        articles = await self.wiki_repository.get_articles_by_workspace(workspace_id)
        connections = await self.wiki_repository.get_connections_by_workspace(workspace_id)
        # Note: Wiki pages not implemented in current interface
        pages = []
        
        # Count by article type
        type_counts = {}
        total_content_length = 0
        
        for article in articles:
            article_type = article.article_type.value if article.article_type else "unknown"
            type_counts[article_type] = type_counts.get(article_type, 0) + 1
            total_content_length += len(article.content)
        
        return {
            "workspace_id": workspace_id,
            "total_articles": len(articles),
            "total_connections": len(connections),
            "total_pages": len(pages),
            "articles_by_type": type_counts,
            "character_count": type_counts.get("character", 0),
            "location_count": type_counts.get("location", 0),
            "concept_count": type_counts.get("concept", 0),
            "event_count": type_counts.get("event", 0),
            "organization_count": type_counts.get("organization", 0),
            "object_count": type_counts.get("object", 0),
            "average_article_length": total_content_length // len(articles) if articles else 0,
            "total_content_length": total_content_length
        }
    
    async def find_orphaned_articles(self, workspace_id: UUID) -> List[WikiArticle]:
        """Find articles with no incoming or outgoing connections."""
        articles = await self.wiki_repository.get_articles_by_workspace(workspace_id)
        connections = await self.wiki_repository.get_connections_by_workspace(workspace_id)
        
        connected_article_ids = set()
        for conn in connections:
            connected_article_ids.add(conn.from_article_id)
            connected_article_ids.add(conn.to_article_id)
        
        return [a for a in articles if a.id not in connected_article_ids]
    
    async def get_most_connected_articles(
        self, workspace_id: UUID, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get articles with the most connections."""
        articles = await self.wiki_repository.get_articles_by_workspace(workspace_id)
        
        article_connection_counts = {}
        for article in articles:
            connections = await self.wiki_repository.get_connections_by_article(article.id)
            article_connection_counts[article.id] = {
                "article": article,
                "connection_count": len(connections)
            }
        
        # Sort by connection count
        sorted_articles = sorted(
            article_connection_counts.values(),
            key=lambda x: x["connection_count"],
            reverse=True
        )
        
        return sorted_articles[:limit]