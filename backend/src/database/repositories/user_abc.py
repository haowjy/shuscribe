# backend/src/database/repositories/user_abc.py
"""Abstract Base Class for User Repositories"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.schemas.user import User, UserAPIKey


class AbstractUserRepository(ABC):
    """Abstract interface for a user repository."""

    @abstractmethod
    async def get(self, id: UUID) -> Optional[User]:
        """Retrieve a single user by their ID."""
        ...

    @abstractmethod
    async def get_multi(self, *, offset: int = 0, limit: int = 100) -> List[User]:
        """Retrieve multiple users with pagination."""
        ...

    @abstractmethod
    async def create(self, obj_in: dict) -> User:
        """Create a new user."""
        ...
    
    @abstractmethod
    async def update(self, db_obj: User, obj_in: dict) -> User:
        """Update an existing user."""
        ...

    @abstractmethod
    async def delete(self, db_obj: User) -> None:
        """Delete a user."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address."""
        ...

    @abstractmethod
    async def get_api_key(self, user_id: UUID, provider: str) -> Optional[UserAPIKey]:
        """Get user's API key for a specific provider."""
        ...

    @abstractmethod
    async def get_all_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get all API keys for a user."""
        ...

    @abstractmethod
    async def store_api_key(
        self,
        user_id: UUID,
        provider: str,
        encrypted_key: str,
        provider_metadata: Optional[dict] = None,
        validation_status: str = "pending",
        last_validated_at: Optional[datetime] = None,
    ) -> UserAPIKey:
        """Store or update user's API key for a provider."""
        ...

    @abstractmethod
    async def delete_api_key(self, user_id: UUID, provider: str) -> bool:
        """Delete user's API key for a provider."""
        ...
