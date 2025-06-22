# backend/src/api/dependencies.py
"""
FastAPI dependencies
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.database.connection import get_db_session
from src.database.repositories.user import UserRepository
from src.core.security import get_current_user_id

async def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    """Get user repository instance"""
    return UserRepository(session)

async def get_current_user_id_dependency() -> UUID:
    """Get current user ID (placeholder until auth is implemented)"""
    # For now, return a mock UUID for testing
    from uuid import uuid4
    return uuid4()