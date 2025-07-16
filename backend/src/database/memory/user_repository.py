"""
In-memory user repository implementation for development and testing
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, UTC

from src.core.constants import PROVIDER_ID
from src.database.interfaces.user_repository import IUserRepository, User, UserAPIKey


class MemoryUserRepository(IUserRepository):
    """
    In-memory implementation of user repository.
    
    Used for development and testing. Data is lost when the application restarts.
    """

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._api_keys: Dict[str, Dict[str, UserAPIKey]] = {}  # user_id -> provider -> UserAPIKey

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(user_id)

    async def create_or_update_user(self, user_id: str, email: str, metadata: Optional[Dict[str, Any]] = None) -> User:
        """Create a new user or update existing user data."""
        existing_user = self._users.get(user_id)
        
        if existing_user:
            # Update existing user
            existing_user.email = email
            existing_user.metadata = metadata or {}
            existing_user.updated_at = datetime.now(UTC)
            return existing_user
        else:
            # Create new user
            user = User(
                user_id=user_id,
                email=email,
                created_at=datetime.now(UTC),
                metadata=metadata or {}
            )
            self._users[user_id] = user
            return user

    async def get_api_key(self, user_id: str, provider: PROVIDER_ID) -> Optional[UserAPIKey]:
        """Get encrypted API key for a specific provider."""
        user_keys = self._api_keys.get(user_id, {})
        return user_keys.get(provider)

    async def store_api_key(
        self, 
        user_id: str, 
        provider: PROVIDER_ID, 
        encrypted_api_key: str,
        validation_status: str = "unknown",
        provider_metadata: Optional[Dict[str, Any]] = None
    ) -> UserAPIKey:
        """Store or update an encrypted API key for a user."""
        if user_id not in self._api_keys:
            self._api_keys[user_id] = {}
        
        existing_key = self._api_keys[user_id].get(provider)
        
        if existing_key:
            # Update existing key
            existing_key.encrypted_api_key = encrypted_api_key
            existing_key.validation_status = validation_status
            existing_key.provider_metadata = provider_metadata or {}
            existing_key.updated_at = datetime.now(UTC)
            return existing_key
        else:
            # Create new key
            api_key = UserAPIKey(
                user_id=user_id,
                provider=provider,
                encrypted_api_key=encrypted_api_key,
                validation_status=validation_status,
                provider_metadata=provider_metadata or {},
                created_at=datetime.now(UTC)
            )
            self._api_keys[user_id][provider] = api_key
            return api_key

    async def delete_api_key(self, user_id: str, provider: PROVIDER_ID) -> bool:
        """Delete an API key for a user."""
        user_keys = self._api_keys.get(user_id, {})
        if provider in user_keys:
            del user_keys[provider]
            return True
        return False

    async def list_user_api_keys(self, user_id: str) -> List[UserAPIKey]:
        """List all API keys for a user."""
        user_keys = self._api_keys.get(user_id, {})
        return list(user_keys.values())

    async def update_api_key_validation(
        self, 
        user_id: str, 
        provider: PROVIDER_ID, 
        validation_status: str,
        last_validated_at: Optional[datetime] = None
    ) -> bool:
        """Update the validation status of an API key."""
        user_keys = self._api_keys.get(user_id, {})
        api_key = user_keys.get(provider)
        
        if api_key:
            api_key.validation_status = validation_status
            api_key.last_validated_at = last_validated_at or datetime.now(UTC)
            api_key.updated_at = datetime.now(UTC)
            return True
        return False
    
    def clear_all_data(self):
        """Clear all data (useful for testing)."""
        self._users.clear()
        self._api_keys.clear()