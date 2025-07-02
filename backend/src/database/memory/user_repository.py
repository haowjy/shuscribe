"""Memory-based user repository implementation for testing and development."""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import UTC, datetime

from src.database.interfaces.user_repository import IUserRepository
from src.schemas.db.user import SubscriptionTier, User, UserCreate, UserUpdate, UserAPIKey, UserAPIKeyCreate


class MemoryUserRepository(IUserRepository):
    """In-memory implementation of user repository for testing."""
    
    def __init__(self):
        self._users: Dict[UUID, User] = {}
        self._api_keys: Dict[str, UserAPIKey] = {}  # composite_key -> UserAPIKey
    
    # User CRUD
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        user_id = uuid4()
        now = datetime.now(UTC)
        
        user = User(
            id=user_id,
            email=user_data.email,
            display_name=user_data.display_name,
            subscription_tier=user_data.subscription_tier,
            preferences=user_data.preferences,
            created_at=now,
            updated_at=now
        )
        
        self._users[user_id] = user
        return user
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID"""
        return self._users.get(user_id)
    
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update an existing user"""
        user = self._users.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        update_dict = user_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        updated_user = user.model_copy(update=update_dict)
        self._users[user_id] = updated_user
        return updated_user
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user"""
        if user_id in self._users:
            # Also delete associated API keys
            keys_to_delete = [
                key for key in self._api_keys.keys() 
                if key.startswith(str(user_id))
            ]
            for key in keys_to_delete:
                del self._api_keys[key]
            
            del self._users[user_id]
            return True
        return False
    
    # Simple User Queries
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address"""
        for user in self._users.values():
            if user.email == email:
                return user
        return None
    
    async def get_users_by_subscription_tier(self, tier: SubscriptionTier) -> List[User]:
        """Get users filtered by subscription tier"""
        return [
            user for user in self._users.values() 
            if user.subscription_tier == tier
        ]
    
    async def get_users(
        self, offset: int = 0, limit: int = 100
    ) -> List[User]:
        """Get paginated list of users"""
        all_users = list(self._users.values())
        # Sort by created_at for consistent pagination
        all_users.sort(key=lambda u: u.created_at)
        return all_users[offset:offset + limit]
    
    # BYOK API Key Management
    async def store_api_key(
        self, user_id: UUID, api_key_data: UserAPIKeyCreate, encrypted_key: str
    ) -> UserAPIKey:
        """Store an encrypted API key"""
        now = datetime.now(UTC)
        
        api_key = UserAPIKey(
            user_id=user_id,
            provider=api_key_data.provider,
            encrypted_api_key=encrypted_key,
            provider_metadata=api_key_data.provider_metadata,
            validation_status="pending",
            last_validated_at=None,
            created_at=now,
            updated_at=now
        )
        
        self._api_keys[api_key.composite_key] = api_key
        return api_key
    
    async def get_api_key(
        self, user_id: UUID, provider: str
    ) -> Optional[UserAPIKey]:
        """Get an API key for a specific user and provider"""
        composite_key = f"{user_id}::{provider}"
        return self._api_keys.get(composite_key)
    
    async def update_api_key_validation(
        self, user_id: UUID, provider: str, status: str
    ) -> UserAPIKey:
        """Update API key validation status"""
        composite_key = f"{user_id}::{provider}"
        api_key = self._api_keys.get(composite_key)
        if not api_key:
            raise ValueError(f"API key not found for user {user_id}, provider {provider}")
        
        updated_api_key = api_key.model_copy(update={
            'validation_status': status,
            'last_validated_at': datetime.now(UTC),
            'updated_at': datetime.now(UTC)
        })
        
        self._api_keys[composite_key] = updated_api_key
        return updated_api_key
    
    async def delete_api_key(self, user_id: UUID, provider: str) -> bool:
        """Delete an API key"""
        composite_key = f"{user_id}::{provider}"
        if composite_key in self._api_keys:
            del self._api_keys[composite_key]
            return True
        return False
    
    async def get_user_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get all API keys for a user"""
        return [
            api_key for api_key in self._api_keys.values()
            if api_key.user_id == user_id
        ]
    
    async def get_validated_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get only validated API keys for a user"""
        return [
            api_key for api_key in self._api_keys.values()
            if api_key.user_id == user_id and api_key.validation_status == "valid"
        ]