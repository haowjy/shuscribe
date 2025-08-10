# backend/src/database/memory/repositories/user_repository.py
"""
Memory User repository implementation
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, UTC

from src.core.constants import PROVIDER_ID
from src.database.interfaces.user_repository import IUserRepository
from src.database.interfaces.models import User as DomainUser, UserAPIKey as DomainUserAPIKey


class MemoryUserRepository(IUserRepository):
    """
    In-memory implementation of user repository.
    
    Used for development and testing. Data is lost when the application restarts.
    """

    def __init__(self):
        self._users: Dict[str, DomainUser] = {}
        self._api_keys: Dict[str, Dict[str, DomainUserAPIKey]] = {}  # user_id -> provider -> UserAPIKey

    async def get_user_by_id(self, user_id: str) -> Optional[DomainUser]:
        """Get user by ID."""
        return self._users.get(user_id)

    async def create_or_update_user(self, user_id: str, email: str, metadata: Optional[Dict[str, Any]] = None) -> DomainUser:
        """Create a new user or update existing user data."""
        existing_user = self._users.get(user_id)
        now = datetime.now(UTC).replace(tzinfo=None)
        
        if existing_user:
            # Create updated user (dataclass is immutable)
            updated_user = DomainUser(
                id=existing_user.id,
                email=email,
                name=existing_user.name,
                avatar_url=existing_user.avatar_url,
                metadata=metadata or {},
                created_at=existing_user.created_at,
                updated_at=now,
            )
            self._users[user_id] = updated_user
            return updated_user
        else:
            # Create new user
            user = DomainUser(
                id=user_id,
                email=email,
                name=None,
                avatar_url=None,
                metadata=metadata or {},
                created_at=now,
                updated_at=now,
            )
            self._users[user_id] = user
            return user

    async def get_api_key(self, user_id: str, provider: PROVIDER_ID) -> Optional[DomainUserAPIKey]:
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
    ) -> DomainUserAPIKey:
        """Store or update an encrypted API key for a user."""
        if user_id not in self._api_keys:
            self._api_keys[user_id] = {}
        
        existing_key = self._api_keys[user_id].get(provider)
        now = datetime.now(UTC).replace(tzinfo=None)
        
        if existing_key:
            # Create updated API key (dataclass is immutable)
            updated_key = DomainUserAPIKey(
                user_id=existing_key.user_id,
                provider=existing_key.provider,
                encrypted_api_key=encrypted_api_key,
                validation_status=validation_status,
                last_validated_at=existing_key.last_validated_at,
                provider_metadata=provider_metadata or {},
                created_at=existing_key.created_at,
                updated_at=now,
            )
            self._api_keys[user_id][provider] = updated_key
            return updated_key
        else:
            # Create new key
            api_key = DomainUserAPIKey(
                user_id=user_id,
                provider=provider,
                encrypted_api_key=encrypted_api_key,
                validation_status=validation_status,
                last_validated_at=None,
                provider_metadata=provider_metadata or {},
                created_at=now,
                updated_at=now,
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

    async def list_user_api_keys(self, user_id: str) -> List[DomainUserAPIKey]:
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
            # Create updated API key (dataclass is immutable)
            updated_key = DomainUserAPIKey(
                user_id=api_key.user_id,
                provider=api_key.provider,
                encrypted_api_key=api_key.encrypted_api_key,
                validation_status=validation_status,
                last_validated_at=last_validated_at or datetime.now(UTC).replace(tzinfo=None),
                provider_metadata=api_key.provider_metadata,
                created_at=api_key.created_at,
                updated_at=datetime.now(UTC).replace(tzinfo=None),
            )
            self._api_keys[user_id][provider] = updated_key
            return True
        return False
    
    def clear_all_data(self):
        """Clear all data (useful for testing)."""
        self._users.clear()
        self._api_keys.clear()