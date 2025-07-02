"""
User Service - Business logic for user management and BYOK API keys.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from src.database.interfaces.user_repository import IUserRepository
from src.schemas.db.user import SubscriptionTier, User, UserAPIKey, UserCreate, UserUpdate, UserAPIKeyCreate
from src.core.encryption import encrypt_api_key, decrypt_api_key


class UserService:
    """Service layer for user management with business logic."""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    # User Management
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with validation."""
        # Check if user already exists
        existing_user = await self.user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError(f"User with email {user_data.email} already exists")
        
        return await self.user_repository.create_user(user_data)
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repository.get_user(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return await self.user_repository.get_user_by_email(email)
    
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update user with validation."""
        # Verify user exists
        existing_user = await self.user_repository.get_user(user_id)
        if not existing_user:
            raise ValueError(f"User {user_id} not found")
        
        # If email is being changed, check for conflicts
        if user_data.email and user_data.email != existing_user.email:
            email_conflict = await self.user_repository.get_user_by_email(user_data.email)
            if email_conflict:
                raise ValueError(f"Email {user_data.email} is already in use")
        
        return await self.user_repository.update_user(user_id, user_data)
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete user and cleanup related data."""
        # Verify user exists
        existing_user = await self.user_repository.get_user(user_id)
        if not existing_user:
            return False
        
        # TODO: Add cleanup logic for workspaces, stories, etc.
        # This should coordinate with other services to cleanup user data
        
        return await self.user_repository.delete_user(user_id)
    
    async def list_users(self, offset: int = 0, limit: int = 100) -> List[User]:
        """Get paginated list of users."""
        if limit > 1000:  # Prevent excessive queries
            limit = 1000
        
        return await self.user_repository.get_users(offset=offset, limit=limit)
    
    async def get_users_by_subscription_tier(self, tier: SubscriptionTier) -> List[User]:
        """Get users filtered by subscription tier."""
        return await self.user_repository.get_users_by_subscription_tier(tier)
    
    # BYOK API Key Management
    async def store_api_key(
        self, user_id: UUID, provider: str, api_key: str, 
        provider_metadata: Optional[Dict[str, Any]] = None
    ) -> UserAPIKey:
        """Store and encrypt user's API key (convenience method for API endpoints)."""
        # Create API key data object
        api_key_data = UserAPIKeyCreate(
            provider=provider,
            api_key=api_key,
            provider_metadata=provider_metadata or {}
        )
        
        return await self.store_api_key_data(user_id, api_key_data)
    
    async def store_api_key_data(
        self, user_id: UUID, api_key_data: UserAPIKeyCreate
    ) -> UserAPIKey:
        """Store and encrypt user's API key using UserAPIKeyCreate object."""
        # Verify user exists
        user = await self.user_repository.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Encrypt the API key
        encrypted_key = encrypt_api_key(api_key_data.api_key)
        
        # Store with encryption
        return await self.user_repository.store_api_key(
            user_id, api_key_data, encrypted_key
        )
    
    async def get_api_key(self, user_id: UUID, provider: str) -> Optional[UserAPIKey]:
        """Get decrypted API key for user and provider."""
        api_key = await self.user_repository.get_api_key(user_id, provider)
        if not api_key:
            return None
        
        # Decrypt the key for use
        try:
            decrypted_key = decrypt_api_key(api_key.encrypted_api_key)
            # Return copy with decrypted key
            return api_key.model_copy(update={"encrypted_api_key": decrypted_key})
        except Exception:
            # If decryption fails, mark as invalid
            await self.user_repository.update_api_key_validation(
                user_id, provider, "invalid"
            )
            return None
    
    async def update_api_key_validation(
        self, user_id: UUID, provider: str, status: str
    ) -> UserAPIKey:
        """Update API key validation status."""
        if status not in ["pending", "valid", "invalid", "expired"]:
            raise ValueError(f"Invalid validation status: {status}")
        
        return await self.user_repository.update_api_key_validation(
            user_id, provider, status
        )
    
    async def delete_api_key(self, user_id: UUID, provider: str) -> bool:
        """Delete user's API key for provider."""
        return await self.user_repository.delete_api_key(user_id, provider)
    
    async def get_user_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get all API keys for user (with keys decrypted)."""
        api_keys = await self.user_repository.get_user_api_keys(user_id)
        
        # Decrypt keys for use
        decrypted_keys = []
        for api_key in api_keys:
            try:
                decrypted_key = decrypt_api_key(api_key.encrypted_api_key)
                decrypted_keys.append(
                    api_key.model_copy(update={"encrypted_api_key": decrypted_key})
                )
            except Exception:
                # Skip keys that can't be decrypted
                continue
        
        return decrypted_keys
    
    async def get_validated_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get only validated API keys for user."""
        api_keys = await self.user_repository.get_validated_api_keys(user_id)
        
        # Decrypt keys for use
        decrypted_keys = []
        for api_key in api_keys:
            try:
                decrypted_key = decrypt_api_key(api_key.encrypted_api_key)
                decrypted_keys.append(
                    api_key.model_copy(update={"encrypted_api_key": decrypted_key})
                )
            except Exception:
                # Mark as invalid if decryption fails
                await self.user_repository.update_api_key_validation(
                    user_id, api_key.provider, "invalid"
                )
                continue
        
        return decrypted_keys
    
    async def validate_api_key(self, user_id: UUID, provider: str) -> bool:
        """Validate an API key by testing it with the provider."""
        api_key = await self.get_api_key(user_id, provider)
        if not api_key:
            return False
        
        # TODO: Implement actual validation by calling provider API
        # For now, just mark as valid
        await self.update_api_key_validation(user_id, provider, "valid")
        return True