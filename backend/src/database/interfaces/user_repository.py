from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.schemas.db.user import SubscriptionTier, User, UserAPIKey, UserCreate, UserUpdate, UserAPIKeyCreate


class IUserRepository(ABC):
    """Abstract interface for user repository - pure CRUD + simple queries"""

    # User CRUD
    @abstractmethod
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        pass

    @abstractmethod
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID"""
        pass

    @abstractmethod
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update an existing user"""
        pass

    @abstractmethod
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user"""
        pass

    # Simple User Queries
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address"""
        pass

    @abstractmethod
    async def get_users_by_subscription_tier(self, tier: SubscriptionTier) -> List[User]:
        """Get users filtered by subscription tier"""
        pass

    @abstractmethod
    async def get_users(
        self, offset: int = 0, limit: int = 100
    ) -> List[User]:
        """Get paginated list of users"""
        pass

    # BYOK API Key Management
    @abstractmethod
    async def store_api_key(
        self, user_id: UUID, api_key_data: UserAPIKeyCreate, encrypted_key: str
    ) -> UserAPIKey:
        """Store an encrypted API key"""
        pass

    @abstractmethod
    async def get_api_key(
        self, user_id: UUID, provider: str
    ) -> Optional[UserAPIKey]:
        """Get an API key for a specific user and provider"""
        pass

    @abstractmethod
    async def update_api_key_validation(
        self, user_id: UUID, provider: str, status: str
    ) -> UserAPIKey:
        """Update API key validation status"""
        pass

    @abstractmethod
    async def delete_api_key(self, user_id: UUID, provider: str) -> bool:
        """Delete an API key"""
        pass

    @abstractmethod
    async def get_user_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get all API keys for a user"""
        pass

    @abstractmethod
    async def get_validated_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get only validated API keys for a user"""
        pass