"""
Domain Models for ShuScribe Storage Architecture

All Pydantic models organized by domain for clean separation of concerns.
"""

# Re-export all models for convenient importing
# Note: Only importing existing models, others are commented out until created
# from src.schemas.db.user import User, UserAPIKey, UserCreate, UserUpdate, UserAPIKeyCreate, SubscriptionTier
# from src.schemas.db.workspace import Workspace, Arc, WorkspaceCreate, WorkspaceUpdate
# from src.schemas.db.story import (
#     Chapter, ChapterCreate, ChapterUpdate, ChapterStatus,
#     StoryMetadata, StoryMetadataCreate, StoryMetadataUpdate,
#     FullStoryBase
# )
# from src.schemas.db.wiki import (
#     WikiArticle, WikiArticleCreate, WikiArticleUpdate, WikiArticleType,
#     ChapterVersion, ChapterVersionCreate, ChapterVersionUpdate,
#     CurrentVersion, CurrentVersionCreate, CurrentVersionUpdate,
#     ArticleConnection, ArticleConnectionCreate,
#     WikiPage, WikiPageCreate, WikiPageUpdate,
#     WikiArchive, WikiArchiveMetadata,
#     WikiPageArticleLink, WikiPageArticleLinkCreate, WikiPageArticleLinkUpdate
# )
from src.schemas.db.writing import AuthorNote, ResearchItem, CharacterProfile


__all__ = [
    # Writing domain - only available models
    "AuthorNote",
    "ResearchItem",
    "CharacterProfile",
    
    # Other domains commented out until models are created
    # # User domain
    # "User",
    # "UserAPIKey", 
    # "UserCreate",
    # "UserUpdate",
    # "UserAPIKeyCreate",
    # "SubscriptionTier",
    
    # # Workspace domain
    # "Workspace",
    # "Arc",
    # "WorkspaceCreate",
    # "WorkspaceUpdate",
    
    # # Story domain
    # "Chapter",
    # "ChapterCreate",
    # "ChapterUpdate",
    # "ChapterStatus",
    # "StoryMetadata",
    # "StoryMetadataCreate",
    # "StoryMetadataUpdate",
    # "FullStoryBase",
    
    # # Wiki domain
    # "WikiArticle",
    # "WikiArticleCreate", 
    # "WikiArticleUpdate",
    # "WikiArticleType",
    # "ChapterVersion",
    # "ChapterVersionCreate",
    # "ChapterVersionUpdate",
    # "CurrentVersion",
    # "CurrentVersionCreate",
    # "CurrentVersionUpdate",
    # "ArticleConnection",
    # "ArticleConnectionCreate",
    # "WikiPage",
    # "WikiPageCreate",
    # "WikiPageUpdate",
    # "WikiArchive",
    # "WikiArchiveMetadata",
    # "WikiPageArticleLink",
    # "WikiPageArticleLinkCreate",
    # "WikiPageArticleLinkUpdate",
] 