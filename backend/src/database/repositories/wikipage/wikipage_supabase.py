"""
Supabase WikiPage Repository Implementation (STUB)
Will be implemented when web deployment is needed
"""
from typing import List, Optional
from uuid import UUID

from src.database.repositories.wikipage.wikipage_abc import AbstractWikiPageRepository
from src.schemas.wiki import (
    WikiPage, WikiPageCreate, WikiPageUpdate,
    WikiArticle, WikiArticleCreate, WikiArticleUpdate,
    WikiPageArticleLink, WikiPageArticleLinkCreate, WikiPageArticleLinkUpdate,
    WikiArchive, ArticleType
)


class SupabaseWikiPageRepository(AbstractWikiPageRepository):
    """Supabase implementation of wiki page repository - STUB FOR FUTURE IMPLEMENTATION"""
    
    def __init__(self):
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    # All methods raise NotImplementedError for now
    async def get_wiki_page(self, wiki_page_id: UUID) -> WikiPage:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def get_wiki_pages_by_creator(self, creator_id: UUID) -> List[WikiPage]:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def create_wiki_page(self, wiki_page_create: WikiPageCreate) -> WikiPage:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def update_wiki_page(self, wiki_page_id: UUID, wiki_page_update: WikiPageUpdate) -> Optional[WikiPage]:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def delete_wiki_page(self, wiki_page_id: UUID) -> bool:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def get_wiki_article(self, article_id: UUID) -> Optional[WikiArticle]:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def get_wiki_article_by_slug(self, slug: str) -> Optional[WikiArticle]:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def create_wiki_article(self, article_create: WikiArticleCreate) -> WikiArticle:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def update_wiki_article(self, article_id: UUID, article_update: WikiArticleUpdate) -> Optional[WikiArticle]:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def delete_wiki_article(self, article_id: UUID) -> bool:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def create_wiki_articles_bulk(self, articles_create: List[WikiArticleCreate]) -> List[WikiArticle]:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def get_wiki_page_articles(self, wiki_page_id: UUID, max_chapter: Optional[int] = None) -> List[WikiArticle]:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def get_article_wiki_pages(self, article_id: UUID) -> List[WikiPage]:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def create_page_article_link(self, link_create: WikiPageArticleLinkCreate) -> WikiPageArticleLink:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def update_page_article_link(self, link_id: UUID, link_update: WikiPageArticleLinkUpdate) -> Optional[WikiPageArticleLink]:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def delete_page_article_link(self, link_id: UUID) -> bool:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def get_wiki_archive(self, wiki_page_id: UUID, max_chapter: int) -> Optional[WikiArchive]:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def load_from_directory(self, wiki_directory_path: str, wiki_page_id: UUID) -> bool:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def save_to_directory(self, wiki_page_id: UUID, wiki_directory_path: str, max_chapter: Optional[int] = None) -> bool:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented")

    async def search_articles(
        self, 
        wiki_page_id: UUID,
        query: str, 
        max_chapter: Optional[int] = None,
        article_types: Optional[List[ArticleType]] = None,
        limit: int = 10
    ) -> List[WikiArticle]:
        raise NotImplementedError("Supabase WikiPage repository not yet implemented") 