"""
ShuScribe Database Package

Clean architecture with domain separation and multiple backend support.
"""

# Repository interfaces
from src.database.interfaces import (
    IUserRepository, IWorkspaceRepository, IStoryRepository, IWikiRepository
)

# Repository implementations - file-based is now the default

# Factory for easy repository creation
from src.database.factory import RepositoryFactory, get_repositories

__all__ = [
    # Interfaces
    "IUserRepository", "IWorkspaceRepository", "IStoryRepository", "IWikiRepository",
    
    # Implementations are created via factory
    
    # Factory
    "RepositoryFactory", "get_repositories",
]
