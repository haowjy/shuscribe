"""
Wiki management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List, Optional

from src.api.dependencies import (
    get_wiki_service_dependency,
    get_current_user_id_dependency
)
from src.services.wiki.wiki_service import WikiService
from src.schemas.db.wiki import (
    WikiArticle, WikiArticleCreate, WikiArticleUpdate, WikiArticleType,
    ChapterVersion, ChapterVersionCreate,
    CurrentVersion, CurrentVersionCreate, CurrentVersionUpdate,
    ArticleConnection, ArticleConnectionCreate
)

router = APIRouter()


@router.post("/articles", response_model=WikiArticle)
async def create_article(
    article_data: WikiArticleCreate,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    wiki_service: WikiService = Depends(get_wiki_service_dependency)
):
    """Create a new wiki article"""
    try:
        return await wiki_service.create_article(article_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create article: {str(e)}")


@router.get("/articles/{article_id}", response_model=WikiArticle)
async def get_article(
    article_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    wiki_service: WikiService = Depends(get_wiki_service_dependency)
):
    """Get article by ID"""
    article = await wiki_service.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.get("/workspaces/{workspace_id}/articles", response_model=List[WikiArticle])
async def get_articles_by_workspace(
    workspace_id: UUID,
    article_type: Optional[WikiArticleType] = None,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    wiki_service: WikiService = Depends(get_wiki_service_dependency)
):
    """Get articles for a workspace"""
    try:
        return await wiki_service.get_articles_by_workspace(workspace_id, article_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get articles: {str(e)}")


@router.put("/articles/{article_id}", response_model=WikiArticle)
async def update_article(
    article_id: UUID,
    article_data: WikiArticleUpdate,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    wiki_service: WikiService = Depends(get_wiki_service_dependency)
):
    """Update article"""
    try:
        return await wiki_service.update_article(article_id, article_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update article: {str(e)}")


@router.post("/articles/{article_id}/chapter-versions", response_model=ChapterVersion)
async def create_chapter_version(
    article_id: UUID,
    chapter_number: int,
    content: str,
    summary: str = "",
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    wiki_service: WikiService = Depends(get_wiki_service_dependency)
):
    """Create a chapter-specific version of an article"""
    try:
        return await wiki_service.create_chapter_version(article_id, chapter_number, content, summary)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chapter version: {str(e)}")


@router.get("/articles/{article_id}/chapter/{chapter_number}", response_model=ChapterVersion)
async def get_article_at_chapter(
    article_id: UUID,
    chapter_number: int,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    wiki_service: WikiService = Depends(get_wiki_service_dependency)
):
    """Get article version safe through specific chapter"""
    version = await wiki_service.get_article_at_chapter(article_id, chapter_number)
    if not version:
        raise HTTPException(status_code=404, detail="Chapter version not found")
    return version


@router.post("/connections", response_model=ArticleConnection)
async def create_connection(
    from_article_id: UUID,
    to_article_id: UUID,
    connection_type: str,
    description: str = "",
    strength: float = 1.0,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    wiki_service: WikiService = Depends(get_wiki_service_dependency)
):
    """Create connection between articles"""
    try:
        return await wiki_service.create_connection(
            from_article_id, to_article_id, connection_type, description, strength
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create connection: {str(e)}")


@router.get("/articles/{article_id}/connections", response_model=List[ArticleConnection])
async def get_article_connections(
    article_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    wiki_service: WikiService = Depends(get_wiki_service_dependency)
):
    """Get all connections for an article"""
    try:
        return await wiki_service.get_article_connections(article_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connections: {str(e)}")