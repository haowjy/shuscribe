"""
In-Memory WikiPage Repository Implementation
Handles wiki pages, articles, snapshots, and directory operations for local usage
"""
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from src.database.repositories.wikipage.wikipage_abc import AbstractWikiPageRepository
from src.schemas.wiki import (
    WikiPage, WikiPageCreate, WikiPageUpdate,
    Article, ArticleCreate, ArticleUpdate,
    ArticleSnapshot, ArticleSnapshotCreate, ArticleSnapshotUpdate,
    ArticleStoryAssociation, ArticleStoryAssociationCreate,
    WikiPageArticleLink, WikiPageArticleLinkCreate, WikiPageArticleLinkUpdate,
    WikiArchive, WikiArchiveMetadata, ArticleType,
    # Keep old WikiArticle for compatibility during transition
    WikiArticle, WikiArticleCreate, WikiArticleUpdate
)


class InMemoryWikiPageRepository(AbstractWikiPageRepository):
    """In-memory implementation of wiki page repository with article snapshot support"""
    
    def __init__(self):
        # Primary data stores
        self._wiki_pages: Dict[UUID, WikiPage] = {}
        
        # New snapshot-based architecture
        self._articles: Dict[UUID, Article] = {}  # Base conceptual articles
        self._article_snapshots: Dict[UUID, ArticleSnapshot] = {}  # Versioned content
        self._article_story_associations: Dict[UUID, ArticleStoryAssociation] = {}
        self._page_article_links: Dict[UUID, WikiPageArticleLink] = {}  # Links to snapshots
        
        # Legacy support (for old WikiArticle system during transition)
        self._wiki_articles: Dict[UUID, WikiArticle] = {}
        
        # Index mappings for efficient lookups
        self._pages_by_creator: Dict[UUID, List[UUID]] = {}
        self._articles_by_slug: Dict[str, UUID] = {}  # slug -> article_id
        self._snapshots_by_article: Dict[UUID, List[UUID]] = {}  # article_id -> [snapshot_ids]
        self._snapshots_by_story: Dict[UUID, List[UUID]] = {}  # story_id -> [snapshot_ids]
        self._associations_by_article: Dict[UUID, List[UUID]] = {}  # article_id -> [association_ids]
        self._associations_by_story: Dict[UUID, List[UUID]] = {}  # story_id -> [association_ids]
        self._links_by_page: Dict[UUID, List[UUID]] = {}  # page_id -> [link_ids]
        self._links_by_snapshot: Dict[UUID, List[UUID]] = {}  # snapshot_id -> [link_ids]

    def _add_to_index(self, index_dict: Dict[UUID, List[UUID]], key: UUID, value: UUID):
        """Helper to add value to index list"""
        if key not in index_dict:
            index_dict[key] = []
        if value not in index_dict[key]:
            index_dict[key].append(value)

    def _remove_from_index(self, index_dict: Dict[UUID, List[UUID]], key: UUID, value: UUID):
        """Helper to remove value from index list"""
        if key in index_dict and value in index_dict[key]:
            index_dict[key].remove(value)

    # WikiPage CRUD operations
    async def get_wiki_page(self, wiki_page_id: UUID) -> WikiPage:
        """Get a wiki page by ID - returns empty page if not found"""
        wiki_page = self._wiki_pages.get(wiki_page_id)
        if wiki_page is None:
            return WikiPage.create_empty(creator_id=uuid4())
        return wiki_page

    async def get_wiki_pages_by_creator(self, creator_id: UUID) -> List[WikiPage]:
        """Get all wiki pages created by a user"""
        page_ids = self._pages_by_creator.get(creator_id, [])
        return [self._wiki_pages[page_id] for page_id in page_ids if page_id in self._wiki_pages]

    async def create_wiki_page(self, wiki_page_create: WikiPageCreate) -> WikiPage:
        """Create a new wiki page"""
        page_id = uuid4()
        now = datetime.now(timezone.utc)
        
        wiki_page = WikiPage(
            title=wiki_page_create.title,
            description=wiki_page_create.description,
            is_public=wiki_page_create.is_public,
            safe_through_chapter=wiki_page_create.safe_through_chapter,
            creator_id=wiki_page_create.creator_id,
            id=page_id,
            created_at=now,
            updated_at=now
        )
        
        self._wiki_pages[page_id] = wiki_page
        self._add_to_index(self._pages_by_creator, wiki_page_create.creator_id, page_id)
        
        return wiki_page

    async def update_wiki_page(self, wiki_page_id: UUID, wiki_page_update: WikiPageUpdate) -> WikiPage:
        """Update an existing wiki page"""
        wiki_page = await self.get_wiki_page(wiki_page_id)
        if wiki_page.id == UUID(int=0):  # Empty page
            return wiki_page
            
        update_data = wiki_page_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(wiki_page, field, value)
        
        wiki_page.updated_at = datetime.now(timezone.utc)
        return wiki_page

    async def delete_wiki_page(self, wiki_page_id: UUID) -> bool:
        """Delete a wiki page and all its article links"""
        if wiki_page_id not in self._wiki_pages:
            return False
            
        wiki_page = self._wiki_pages[wiki_page_id]
        
        # Remove from creator index
        self._remove_from_index(self._pages_by_creator, wiki_page.creator_id, wiki_page_id)
        
        # Delete all page-article links
        link_ids = self._links_by_page.get(wiki_page_id, []).copy()
        for link_id in link_ids:
            if link_id in self._page_article_links:
                link = self._page_article_links[link_id]
                self._remove_from_index(self._links_by_snapshot, link.article_snapshot_id, link_id)
                del self._page_article_links[link_id]
        self._links_by_page.pop(wiki_page_id, None)
        
        # Finally delete the wiki page
        del self._wiki_pages[wiki_page_id]
        return True

    # Article operations (base conceptual articles)
    async def get_article(self, article_id: UUID) -> Article:
        """Get a base article by ID"""
        if article := self._articles.get(article_id):
            return article
        return Article.create_empty()

    async def get_article_by_slug(self, slug: str) -> Article:
        """Get article by slug"""
        article_id = self._articles_by_slug.get(slug)
        if article_id and article_id in self._articles:
            return self._articles[article_id]
        return Article.create_empty()

    async def create_article(self, article_create: ArticleCreate) -> Article:
        """Create a new base article"""
        article_id = uuid4()
        now = datetime.now(timezone.utc)
        
        article = Article(
            id=article_id,
            title=article_create.title,
            slug=article_create.slug,
            article_type=article_create.article_type,
            canonical_name=article_create.canonical_name,
            aliases=article_create.aliases,
            tags=article_create.tags,
            creator_id=article_create.creator_id,
            created_at=now,
            updated_at=now
        )
        
        self._articles[article_id] = article
        self._articles_by_slug[article_create.slug] = article_id
        
        return article

    async def update_article(self, article_id: UUID, article_update: ArticleUpdate) -> Article:
        """Update a base article"""
        article = await self.get_article(article_id)
        if article.id == UUID(int=0):  # Empty article
            return article
            
        update_data = article_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(article, field, value)
        
        article.updated_at = datetime.now(timezone.utc)
        return article

    # Article Snapshot operations (versioned content)
    async def get_article_snapshot(self, snapshot_id: UUID) -> ArticleSnapshot:
        """Get an article snapshot by ID"""
        if snapshot := self._article_snapshots.get(snapshot_id):
            return snapshot
        return ArticleSnapshot.create_empty()

    async def get_article_snapshots(self, article_id: UUID, story_id: Optional[UUID] = None) -> List[ArticleSnapshot]:
        """Get all snapshots for an article, optionally filtered by story"""
        snapshot_ids = self._snapshots_by_article.get(article_id, [])
        snapshots = [self._article_snapshots[sid] for sid in snapshot_ids if sid in self._article_snapshots]
        
        if story_id:
            snapshots = [s for s in snapshots if s.source_story_id == story_id]
        
        return sorted(snapshots, key=lambda s: s.version_number)

    async def create_article_snapshot(self, snapshot_create: ArticleSnapshotCreate) -> ArticleSnapshot:
        """Create a new article snapshot"""
        snapshot_id = uuid4()
        now = datetime.now(timezone.utc)
        
        snapshot = ArticleSnapshot(
            id=snapshot_id,
            article_id=snapshot_create.article_id,
            content=snapshot_create.content,
            preview=snapshot_create.preview,
            last_safe_chapter=snapshot_create.last_safe_chapter,
            source_story_id=snapshot_create.source_story_id,
            generation_context=snapshot_create.generation_context,
            version_number=snapshot_create.version_number,
            parent_snapshot_id=snapshot_create.parent_snapshot_id,
            created_at=now,
            updated_at=now
        )
        
        self._article_snapshots[snapshot_id] = snapshot
        self._add_to_index(self._snapshots_by_article, snapshot_create.article_id, snapshot_id)
        self._add_to_index(self._snapshots_by_story, snapshot_create.source_story_id, snapshot_id)
        
        return snapshot

    async def update_article_snapshot(self, snapshot_id: UUID, snapshot_update: ArticleSnapshotUpdate) -> ArticleSnapshot:
        """Update an article snapshot"""
        snapshot = await self.get_article_snapshot(snapshot_id)
        if snapshot.id == UUID(int=0):  # Empty snapshot
            return snapshot
            
        update_data = snapshot_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(snapshot, field, value)
        
        snapshot.updated_at = datetime.now(timezone.utc)
        return snapshot

    # Article-Story Association operations (backlinking)
    async def get_article_story_associations(self, article_id: Optional[UUID] = None, story_id: Optional[UUID] = None) -> List[ArticleStoryAssociation]:
        """Get article-story associations"""
        if article_id:
            association_ids = self._associations_by_article.get(article_id, [])
        elif story_id:
            association_ids = self._associations_by_story.get(story_id, [])
        else:
            association_ids = list(self._article_story_associations.keys())
        
        return [self._article_story_associations[aid] for aid in association_ids if aid in self._article_story_associations]

    async def create_article_story_association(self, association_create: ArticleStoryAssociationCreate) -> ArticleStoryAssociation:
        """Create an article-story association"""
        association_id = uuid4()
        now = datetime.now(timezone.utc)
        
        association = ArticleStoryAssociation(
            id=association_id,
            article_id=association_create.article_id,
            story_id=association_create.story_id,
            first_mentioned_chapter=association_create.first_mentioned_chapter,
            importance_level=association_create.importance_level,
            relationship_type=association_create.relationship_type,
            created_at=now,
            updated_at=now
        )
        
        self._article_story_associations[association_id] = association
        self._add_to_index(self._associations_by_article, association_create.article_id, association_id)
        self._add_to_index(self._associations_by_story, association_create.story_id, association_id)
        
        return association

    # WikiPage-ArticleSnapshot Link operations
    async def get_wiki_page_snapshots(self, wiki_page_id: UUID, max_chapter: Optional[int] = None) -> List[ArticleSnapshot]:
        """Get all article snapshots for a wiki page, optionally filtered by chapter safety"""
        link_ids = self._links_by_page.get(wiki_page_id, [])
        links = [self._page_article_links[link_id] for link_id in link_ids if link_id in self._page_article_links]
        
        # Get snapshots and filter by chapter safety
        snapshots = []
        for link in sorted(links, key=lambda l: l.display_order):
            if link.article_snapshot_id in self._article_snapshots:
                snapshot = self._article_snapshots[link.article_snapshot_id]
                if max_chapter is None or snapshot.last_safe_chapter <= max_chapter:
                    snapshots.append(snapshot)
        
        return snapshots

    async def create_page_snapshot_link(self, link_create: WikiPageArticleLinkCreate) -> WikiPageArticleLink:
        """Link an article snapshot to a wiki page"""
        link_id = uuid4()
        now = datetime.now(timezone.utc)
        
        link = WikiPageArticleLink(
            id=link_id,
            wiki_page_id=link_create.wiki_page_id,
            article_snapshot_id=link_create.article_snapshot_id,
            display_order=link_create.display_order,
            is_featured=link_create.is_featured,
            created_at=now,
            updated_at=now
        )
        
        self._page_article_links[link_id] = link
        self._add_to_index(self._links_by_page, link_create.wiki_page_id, link_id)
        self._add_to_index(self._links_by_snapshot, link_create.article_snapshot_id, link_id)
        
        return link

    async def update_page_snapshot_link(self, link_id: UUID, link_update: WikiPageArticleLinkUpdate) -> WikiPageArticleLink:
        """Update a page-snapshot link"""
        if link_id not in self._page_article_links:
            return WikiPageArticleLink(
                id=UUID(int=0),
                wiki_page_id=UUID(int=0),
                article_snapshot_id=UUID(int=0),
                display_order=0,
                is_featured=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
        link = self._page_article_links[link_id]
        update_data = link_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(link, field, value)
        
        link.updated_at = datetime.now(timezone.utc)
        return link

    async def delete_page_snapshot_link(self, link_id: UUID) -> bool:
        """Remove a snapshot from a wiki page"""
        if link_id not in self._page_article_links:
            return False
            
        link = self._page_article_links[link_id]
        self._remove_from_index(self._links_by_page, link.wiki_page_id, link_id)
        self._remove_from_index(self._links_by_snapshot, link.article_snapshot_id, link_id)
        del self._page_article_links[link_id]
        return True

    # Legacy WikiArticle support (for transition period)
    async def get_wiki_article(self, article_id: UUID) -> Optional[WikiArticle]:
        """Get a wiki article by ID (legacy)"""
        return self._wiki_articles.get(article_id)

    async def get_wiki_article_by_slug(self, slug: str) -> Optional[WikiArticle]:
        """Get a wiki article by slug (legacy)"""
        article_id = self._articles_by_slug.get(slug)
        return self._wiki_articles.get(article_id) if article_id else None

    async def create_wiki_article(self, article_create: WikiArticleCreate) -> WikiArticle:
        """Create a new wiki article (legacy)"""
        article_id = uuid4()
        now = datetime.now(timezone.utc)
        
        article = WikiArticle(
            title=article_create.title,
            slug=article_create.slug,
            article_type=article_create.article_type,
            content=article_create.content,
            preview=article_create.preview,
            metadata=article_create.metadata,
            id=article_id,
            created_at=now,
            updated_at=now,
            embedding=None
        )
        
        self._wiki_articles[article_id] = article
        self._articles_by_slug[article_create.slug] = article_id
        
        return article

    async def update_wiki_article(self, article_id: UUID, article_update: WikiArticleUpdate) -> Optional[WikiArticle]:
        """Update an existing wiki article (legacy)"""
        if article_id not in self._wiki_articles:
            return None
            
        article = self._wiki_articles[article_id]
        update_data = article_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(article, field, value)
        
        article.updated_at = datetime.now(timezone.utc)
        return article

    async def delete_wiki_article(self, article_id: UUID) -> bool:
        """Delete a wiki article (legacy)"""
        if article_id not in self._wiki_articles:
            return False
            
        article = self._wiki_articles[article_id]
        self._articles_by_slug.pop(article.slug, None)
        del self._wiki_articles[article_id]
        return True

    async def create_wiki_articles_bulk(self, articles_create: List[WikiArticleCreate]) -> List[WikiArticle]:
        """Create multiple wiki articles in bulk (legacy)"""
        articles = []
        for article_create in articles_create:
            article = await self.create_wiki_article(article_create)
            articles.append(article)
        return articles

    async def get_article_wiki_pages(self, article_id: UUID) -> List[WikiPage]:
        """Get all wiki pages that contain a specific article (legacy)"""
        # For legacy compatibility, return empty list
        return []

    async def create_page_article_link(self, link_create: WikiPageArticleLinkCreate) -> WikiPageArticleLink:
        """Create page-article link (legacy compatibility)"""
        return await self.create_page_snapshot_link(link_create)

    async def update_page_article_link(self, link_id: UUID, link_update: WikiPageArticleLinkUpdate) -> Optional[WikiPageArticleLink]:
        """Update page-article link (legacy compatibility)"""
        result = await self.update_page_snapshot_link(link_id, link_update)
        return result if result.id != UUID(int=0) else None

    async def delete_page_article_link(self, link_id: UUID) -> bool:
        """Delete page-article link (legacy compatibility)"""
        return await self.delete_page_snapshot_link(link_id)

    async def search_articles(
        self, 
        wiki_page_id: UUID,
        query: str, 
        max_chapter: Optional[int] = None,
        article_types: Optional[List[ArticleType]] = None,
        limit: int = 10
    ) -> List[WikiArticle]:
        """Search articles within a wiki page (legacy)"""
        articles = await self.get_wiki_page_articles(wiki_page_id, max_chapter)
        
        # Filter by article types
        if article_types:
            articles = [a for a in articles if a.article_type in article_types]
        
        # Simple text search
        query_lower = query.lower()
        matching_articles = []
        for article in articles:
            if (query_lower in article.title.lower() or 
                query_lower in article.content.lower() or 
                query_lower in article.preview.lower()):
                matching_articles.append(article)
        
        return matching_articles[:limit]

    # High-level operations
    async def get_wiki_archive(self, wiki_page_id: UUID, max_chapter: int) -> Optional[WikiArchive]:
        """Get a complete wiki archive safe through a specific chapter"""
        wiki_page = await self.get_wiki_page(wiki_page_id)
        if wiki_page.id == UUID(int=0):  # Empty page
            return None
        
        # Get snapshots for this page
        snapshots = await self.get_wiki_page_snapshots(wiki_page_id, max_chapter)
        
        # Convert snapshots to legacy WikiArticle format for compatibility
        articles = []
        for snapshot in snapshots:
            base_article = await self.get_article(snapshot.article_id)
            if base_article.id != UUID(int=0):
                wiki_article = WikiArticle(
                    id=snapshot.id,  # Use snapshot ID for compatibility
                    title=base_article.title,
                    slug=base_article.slug,
                    article_type=base_article.article_type,
                    content=snapshot.content,
                    preview=snapshot.preview,
                    metadata={"snapshot_id": str(snapshot.id), "article_id": str(base_article.id)},
                    created_at=snapshot.created_at,
                    updated_at=snapshot.updated_at,
                    embedding=None
                )
                articles.append(wiki_article)
        
        # Get links for this page
        link_ids = self._links_by_page.get(wiki_page_id, [])
        links = [self._page_article_links[link_id] for link_id in link_ids if link_id in self._page_article_links]
        
        metadata = WikiArchiveMetadata(
            wiki_page_id=wiki_page_id,
            wiki_page_title=wiki_page.title,
            safe_through_chapter=max_chapter,
            total_articles=len(articles),
            generation_timestamp=datetime.now(timezone.utc),
            source_arc_id=None,
            source_arc_title=None
        )
        
        file_structure = {article.title: f"{article.article_type.value}s/{article.slug}.md" for article in articles}
        
        return WikiArchive(
            metadata=metadata,
            articles=articles,
            article_links=links,
            file_structure=file_structure
        )

    # Legacy methods for compatibility
    async def get_wiki_page_articles(self, wiki_page_id: UUID, max_chapter: Optional[int] = None) -> List[WikiArticle]:
        """Get all articles for a wiki page (legacy compatibility)"""
        snapshots = await self.get_wiki_page_snapshots(wiki_page_id, max_chapter)
        
        articles = []
        for snapshot in snapshots:
            base_article = await self.get_article(snapshot.article_id)
            if base_article.id != UUID(int=0):
                wiki_article = WikiArticle(
                    id=snapshot.id,
                    title=base_article.title,
                    slug=base_article.slug,
                    article_type=base_article.article_type,
                    content=snapshot.content,
                    preview=snapshot.preview,
                    metadata={"snapshot_id": str(snapshot.id)},
                    created_at=snapshot.created_at,
                    updated_at=snapshot.updated_at,
                    embedding=None
                )
                articles.append(wiki_article)
        
        return articles

    async def load_from_directory(self, wiki_directory_path: str, wiki_page_id: UUID) -> bool:
        """Load wiki articles from a directory structure into a wiki page"""
        try:
            wiki_dir = Path(wiki_directory_path)
            if not wiki_dir.exists():
                return False
            
            # Scan for markdown files
            for md_file in wiki_dir.rglob("*.md"):
                if md_file.is_file():
                    # Determine article type from directory structure
                    relative_path = md_file.relative_to(wiki_dir)
                    if len(relative_path.parts) == 1:
                        article_type = ArticleType.MAIN
                    else:
                        folder_name = relative_path.parts[0].rstrip('s')  # Remove plural
                        article_type = ArticleType(folder_name) if folder_name in ArticleType._value2member_map_ else ArticleType.MAIN
                    
                    # Read content
                    content = md_file.read_text(encoding='utf-8')
                    title = md_file.stem.replace('_', ' ').title()
                    slug = md_file.stem
                    
                    # Get or create base article
                    base_article = await self.get_article_by_slug(slug)
                    if base_article.id == UUID(int=0):  # Not found
                        article_create = ArticleCreate(
                            title=title,
                            slug=slug,
                            article_type=article_type,
                            canonical_name=title,
                            creator_id=uuid4()  # Default creator
                        )
                        base_article = await self.create_article(article_create)
                    
                    # Create snapshot
                    snapshot_create = ArticleSnapshotCreate(
                        article_id=base_article.id,
                        content=content,
                        preview=content[:200] + "..." if len(content) > 200 else content,
                        last_safe_chapter=0,  # Default to chapter 0
                        source_story_id=uuid4(),  # Default story ID
                        version_number=1,
                        parent_snapshot_id=None
                    )
                    snapshot = await self.create_article_snapshot(snapshot_create)
                    
                    # Link snapshot to wiki page
                    link_create = WikiPageArticleLinkCreate(
                        wiki_page_id=wiki_page_id,
                        article_snapshot_id=snapshot.id,
                        display_order=0,
                        is_featured=False
                    )
                    await self.create_page_snapshot_link(link_create)
            
            return True
            
        except Exception:
            return False

    async def save_to_directory(self, wiki_page_id: UUID, wiki_directory_path: str, max_chapter: Optional[int] = None) -> bool:
        """Save wiki page snapshots to a directory structure"""
        try:
            wiki_dir = Path(wiki_directory_path)
            wiki_dir.mkdir(parents=True, exist_ok=True)
            
            snapshots = await self.get_wiki_page_snapshots(wiki_page_id, max_chapter)
            
            for snapshot in snapshots:
                base_article = await self.get_article(snapshot.article_id)
                if base_article.id == UUID(int=0):  # Skip if base article not found
                    continue
                
                # Create directory structure
                if base_article.article_type == ArticleType.MAIN:
                    file_path = wiki_dir / f"{base_article.slug}.md"
                else:
                    type_dir = wiki_dir / f"{base_article.article_type.value}s"
                    type_dir.mkdir(exist_ok=True)
                    file_path = type_dir / f"{base_article.slug}.md"
                
                # Write content
                file_path.write_text(snapshot.content, encoding='utf-8')
            
            return True
            
        except Exception:
            return False

    # Alias methods for test compatibility
    async def create_wiki_page_article_link(self, link_create: WikiPageArticleLinkCreate) -> WikiPageArticleLink:
        """Alias for create_page_snapshot_link for test compatibility"""
        return await self.create_page_snapshot_link(link_create)

    async def get_wiki_page_article_links(self, wiki_page_id: UUID) -> List[WikiPageArticleLink]:
        """Get all article links for a wiki page"""
        link_ids = self._links_by_page.get(wiki_page_id, [])
        links = [self._page_article_links[link_id] for link_id in link_ids if link_id in self._page_article_links]
        return sorted(links, key=lambda l: l.display_order) 