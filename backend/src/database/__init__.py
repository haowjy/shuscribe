"""
ShuScribe Database Package

Clean architecture with domain separation and multiple backend support.
"""

# Core models by domain
from src.database.models import (
    # User domain
    User, UserAPIKey, UserCreate, UserUpdate, UserAPIKeyCreate, SubscriptionTier,
    
    # Workspace domain  
    Workspace, Arc, WorkspaceCreate, WorkspaceUpdate,
    
    # Story domain
    Chapter, ChapterCreate, ChapterUpdate, ChapterStatus,
    StoryMetadata, StoryMetadataCreate, StoryMetadataUpdate,
    
    # Wiki domain
    WikiArticle, WikiArticleCreate, WikiArticleUpdate, WikiArticleType,
    ChapterVersion, ChapterVersionCreate, ChapterVersionUpdate,
    CurrentVersion, CurrentVersionCreate, CurrentVersionUpdate,
    ArticleConnection, ArticleConnectionCreate
)

# Repository interfaces
from src.database.interfaces import (
    IUserRepository, IWorkspaceRepository, IStoryRepository, IWikiRepository
)

# Repository implementations - file-based is now the default

# Factory for easy repository creation
from src.database.factory import RepositoryFactory, get_repositories

__all__ = [
    # Models
    "User", "UserAPIKey", "UserCreate", "UserUpdate", "UserAPIKeyCreate", "SubscriptionTier",
    "Workspace", "Arc", "WorkspaceCreate", "WorkspaceUpdate", 
    "Chapter", "ChapterCreate", "ChapterUpdate", "ChapterStatus",
    "StoryMetadata", "StoryMetadataCreate", "StoryMetadataUpdate",
    "WikiArticle", "WikiArticleCreate", "WikiArticleUpdate", "WikiArticleType",
    "ChapterVersion", "ChapterVersionCreate", "ChapterVersionUpdate",
    "CurrentVersion", "CurrentVersionCreate", "CurrentVersionUpdate",
    "ArticleConnection", "ArticleConnectionCreate",
    
    # Interfaces
    "IUserRepository", "IWorkspaceRepository", "IStoryRepository", "IWikiRepository",
    
    # Implementations are created via factory
    
    # Factory
    "RepositoryFactory", "get_repositories",
]
