# backend/src/database/repositories/__init__.py
"""
Repository layer for database access
Provides abstract interfaces and concrete implementations for data access
"""
from typing import Union

from src.config import settings
from src.database.repositories.user.user_abc import AbstractUserRepository
from src.database.repositories.user.user_in_memory import InMemoryUserRepository
from src.database.repositories.user.user_supabase import SupabaseUserRepository

# Story repositories
from src.database.repositories.story.story_abc import AbstractStoryRepository
from src.database.repositories.story.story_in_memory import InMemoryStoryRepository

# A single, lazily-initialized in-memory repository instance
_in_memory_user_repo: Union[InMemoryUserRepository, None] = None


def get_user_repository(supabase_client=None) -> AbstractUserRepository:
    """
    Factory function to get the appropriate user repository implementation
    based on configuration settings.
    
    Args:
        supabase_client: Supabase client for web deployment (ignored for local mode)
        
    Returns:
        AbstractUserRepository: Appropriate repository implementation
    """
    global _in_memory_user_repo

    if settings.SKIP_DATABASE:
        if _in_memory_user_repo is None:
            _in_memory_user_repo = InMemoryUserRepository()
        return _in_memory_user_repo
    else:
        if supabase_client is None:
            raise ValueError("A Supabase client is required for the database repository.")
        
        # Import here to avoid circular imports and missing dependency issues
        return SupabaseUserRepository(supabase_client)


def get_story_repository(supabase_client=None) -> AbstractStoryRepository:
    """
    Factory function to get the appropriate story repository implementation
    based on configuration settings.
    
    Args:
        supabase_client: Supabase client for web deployment (ignored for local mode)
        
    Returns:
        AbstractStoryRepository: Appropriate repository implementation
    """
    if settings.SKIP_DATABASE:
        # Return singleton for local mode to maintain state across calls
        if not hasattr(get_story_repository, '_in_memory_instance'):
            get_story_repository._in_memory_instance = InMemoryStoryRepository()
        return get_story_repository._in_memory_instance
    else:
        # TODO: Implement SupabaseStoryRepository when ready for web deployment
        raise NotImplementedError("Supabase story repository not yet implemented")


__all__ = [
    'AbstractUserRepository',
    'InMemoryUserRepository', 
    'SupabaseUserRepository',
    'AbstractStoryRepository',
    'InMemoryStoryRepository',
    'get_user_repository',
    'get_story_repository',
    # New repository functions (imported on demand)
    # 'get_wikipage_repository' - from .wikipage import get_wikipage_repository
    # 'get_writing_repository' - from .writing import get_writing_repository
]
