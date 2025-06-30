"""
Domain Models for ShuScribe Storage Architecture

All Pydantic models organized by domain for clean separation of concerns.
"""

# Re-export all models for convenient importing
from src.database.models.user import User, UserAPIKey, UserCreate, UserUpdate, UserAPIKeyCreate, SubscriptionTier
from src.database.models.workspace import Workspace, Arc, WorkspaceCreate, WorkspaceUpdate
from src.database.models.story import (
    Chapter, ChapterCreate, ChapterUpdate, ChapterStatus,
    StoryMetadata, StoryMetadataCreate, StoryMetadataUpdate
)
from src.database.models.wiki import (
    WikiArticle, WikiArticleCreate, WikiArticleUpdate, WikiArticleType,
    ChapterVersion, ChapterVersionCreate, ChapterVersionUpdate,
    CurrentVersion, CurrentVersionCreate, CurrentVersionUpdate,
    ArticleConnection, ArticleConnectionCreate
)


__all__ = [
    # User domain
    "User",
    "UserAPIKey", 
    "UserCreate",
    "UserUpdate",
    "UserAPIKeyCreate",
    "SubscriptionTier",
    
    # Workspace domain
    "Workspace",
    "Arc",
    "WorkspaceCreate",
    "WorkspaceUpdate",
    
    # Story domain
    "Chapter",
    "ChapterCreate",
    "ChapterUpdate",
    "ChapterStatus",
    "StoryMetadata",
    "StoryMetadataCreate",
    "StoryMetadataUpdate",
    
    # Wiki domain
    "WikiArticle",
    "WikiArticleCreate", 
    "WikiArticleUpdate",
    "WikiArticleType",
    "ChapterVersion",
    "ChapterVersionCreate",
    "ChapterVersionUpdate",
    "CurrentVersion",
    "CurrentVersionCreate",
    "CurrentVersionUpdate",
    "ArticleConnection",
    "ArticleConnectionCreate",
] 