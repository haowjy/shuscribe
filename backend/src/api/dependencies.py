# backend/src/api/dependencies.py
"""
FastAPI dependencies
"""
from fastapi import Depends
from uuid import UUID

from src.database.supabase_connection import get_supabase_client
from src.database.repositories import get_user_repository
from src.database.repositories.user_abc import AbstractUserRepository
from src.core.security import get_current_user_id

def get_user_repository_dependency() -> AbstractUserRepository:
    """Get user repository instance"""
    # This will automatically use in-memory repository if SKIP_DATABASE is True
    # or Supabase repository if database is enabled
    if not hasattr(get_user_repository_dependency, '_skip_database_check'):
        from src.config import settings
        get_user_repository_dependency._skip_database_check = settings.SKIP_DATABASE
    
    if get_user_repository_dependency._skip_database_check:
        return get_user_repository()
    else:
        supabase_client = get_supabase_client()
        return get_user_repository(supabase_client)

async def get_current_user_id_dependency() -> UUID:
    """Get current user ID (placeholder until auth is implemented)"""
    # For now, return a mock UUID for testing
    from uuid import uuid4
    return uuid4()