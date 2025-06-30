"""
User Repository Interface

Abstract interface for user operations including BYOK API key management.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.database.models.user import User, UserAPIKey, UserCreate, UserUpdate, UserAPIKeyCreate


class IUserRepository(ABC):
    """Abstract interface for user repository with BYOK support"""

    @abstractmethod
    async def get(self, id: UUID) -> Optional[User]:
        """Retrieve a user by ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        pass

    @abstractmethod
    async def get_multi(self, *, offset: int = 0, limit: int = 100) -> List[User]:
        """Retrieve multiple users with pagination"""
        pass

    @abstractmethod
    async def create(self, user_data: UserCreate) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def update(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update an existing user"""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user"""
        pass

    # BYOK API Key Management
    @abstractmethod
    async def get_api_key(self, user_id: UUID, provider: str) -> Optional[UserAPIKey]:
        """Get user's API key for a specific provider"""
        pass

    @abstractmethod
    async def get_all_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get all API keys for a user"""
        pass

    @abstractmethod
    async def store_api_key(self, user_id: UUID, api_key_data: UserAPIKeyCreate) -> UserAPIKey:
        """Store or update user's API key for a provider"""
        pass

    @abstractmethod
    async def delete_api_key(self, user_id: UUID, provider: str) -> bool:
        """Delete user's API key for a provider"""
        pass

    @abstractmethod
    async def validate_api_key(self, user_id: UUID, provider: str) -> bool:
        """Validate user's API key for a provider"""
        pass 