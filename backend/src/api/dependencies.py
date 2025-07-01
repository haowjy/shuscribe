# backend/src/api/dependencies.py
"""
FastAPI dependencies
"""
from pathlib import Path
from typing import cast
from uuid import UUID

from src.database import get_repositories
from src.database.interfaces.user import IUserRepository
from src.database.models.repositories import FileRepositories


def get_user_repository_dependency() -> IUserRepository:
    """Get user repository instance based on configuration"""
    from src.config import settings

    if settings.SKIP_DATABASE:
        # Use file-based repository for local development
        workspace_path = Path("temp")  # Use temp directory
        repositories = get_repositories(
            backend="file", workspace_path=workspace_path
        )
        return repositories.user
    else:
        # TODO: Use database repository when implemented
        # For now, fall back to file-based even in database mode
        workspace_path = Path("temp")
        repositories = get_repositories(
            backend="file", workspace_path=workspace_path
        )
        return repositories.user


async def get_current_user_id_dependency() -> UUID:
    """Get current user ID based on repository type"""
    from src.config import settings

    if settings.SKIP_DATABASE:
        # For file-based repositories, get the current workspace user
        workspace_path = Path("temp")
        repositories = cast(FileRepositories, get_repositories(
            backend="file", workspace_path=workspace_path
        ))
        user = await repositories.user.get_current_user()
        return user.id
    else:
        # TODO: Implement proper auth when database is enabled
        # For now, return a mock UUID for testing
        from uuid import uuid4
        return uuid4()
