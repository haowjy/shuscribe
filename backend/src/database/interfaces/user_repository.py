"""
User repository interface for user data and API key management
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import UTC, datetime

from src.core.constants import PROVIDER_ID


class UserAPIKey:
    """User API key model for LLM providers"""
    def __init__(
        self, 
        user_id: str,
        provider: PROVIDER_ID,
        encrypted_api_key: str,
        validation_status: str = "unknown",
        last_validated_at: Optional[datetime] = None,
        provider_metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.user_id: str = user_id
        self.provider: PROVIDER_ID = provider
        self.encrypted_api_key: str = encrypted_api_key
        self.validation_status: str = validation_status
        self.last_validated_at: Optional[datetime] = last_validated_at
        self.provider_metadata: Optional[Dict[str, Any]] = provider_metadata or {}
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at: Optional[datetime] = updated_at


class User:
    """User model"""
    def __init__(
        self,
        user_id: str,
        email: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.user_id = user_id
        self.email = email
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at
        self.metadata = metadata or {}


class IUserRepository(ABC):
    """
    User repository interface for managing user data and API keys.
    
    This interface supports the frontend-first philosophy where:
    - User authentication is handled by Supabase on frontend
    - Backend stores user-specific data (API keys, preferences)
    - API keys are encrypted at rest for security
    """

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: The user's UUID from Supabase
            
        Returns:
            User object if found, None otherwise
        """
        pass

    @abstractmethod
    async def create_or_update_user(self, user_id: str, email: str, metadata: Optional[Dict[str, Any]] = None) -> User:
        """
        Create a new user or update existing user data.
        
        Args:
            user_id: The user's UUID from Supabase
            email: User's email address
            metadata: Optional metadata from Supabase auth
            
        Returns:
            User object
        """
        pass

    @abstractmethod
    async def get_api_key(self, user_id: str, provider: PROVIDER_ID) -> Optional[UserAPIKey]:
        """
        Get encrypted API key for a specific provider.
        
        Args:
            user_id: The user's UUID
            provider: The LLM provider ID (e.g., 'openai', 'anthropic')
            
        Returns:
            UserAPIKey object if found, None otherwise
        """
        pass

    @abstractmethod
    async def store_api_key(
        self, 
        user_id: str, 
        provider: PROVIDER_ID, 
        encrypted_api_key: str,
        validation_status: str = "unknown",
        provider_metadata: Optional[Dict[str, Any]] = None
    ) -> UserAPIKey:
        """
        Store or update an encrypted API key for a user.
        
        Args:
            user_id: The user's UUID
            provider: The LLM provider ID
            encrypted_api_key: The encrypted API key
            validation_status: Validation status ('valid', 'invalid', 'unknown')
            provider_metadata: Optional provider-specific settings
            
        Returns:
            UserAPIKey object
        """
        pass

    @abstractmethod
    async def delete_api_key(self, user_id: str, provider: PROVIDER_ID) -> bool:
        """
        Delete an API key for a user.
        
        Args:
            user_id: The user's UUID
            provider: The LLM provider ID
            
        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def list_user_api_keys(self, user_id: str) -> List[UserAPIKey]:
        """
        List all API keys for a user.
        
        Args:
            user_id: The user's UUID
            
        Returns:
            List of UserAPIKey objects
        """
        pass

    @abstractmethod
    async def update_api_key_validation(
        self, 
        user_id: str, 
        provider: PROVIDER_ID, 
        validation_status: str,
        last_validated_at: Optional[datetime] = None
    ) -> bool:
        """
        Update the validation status of an API key.
        
        Args:
            user_id: The user's UUID
            provider: The LLM provider ID
            validation_status: New validation status
            last_validated_at: When the validation occurred
            
        Returns:
            True if updated, False if not found
        """
        pass