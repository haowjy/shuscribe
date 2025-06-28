# backend/src/database/repositories/__init__.py
"""
This module contains the repository implementations and the factory to access them.
"""
from typing import Union, Optional

from src.config import settings
from src.database.repositories.user_abc import AbstractUserRepository
from src.database.repositories.user_in_memory import InMemoryUserRepository

# A single, lazily-initialized in-memory repository instance
_in_memory_user_repo: Union[InMemoryUserRepository, None] = None


def get_user_repository(supabase_client=None) -> AbstractUserRepository:
    """
    Factory function to get the appropriate user repository based on settings.

    If SKIP_DATABASE is True, it returns a singleton in-memory repository.
    Otherwise, it returns a new Supabase-backed repository instance.
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
        from src.database.repositories.user_supabase import SupabaseUserRepository
        return SupabaseUserRepository(supabase_client)
