"""
UserFactory for creating User and UserAPIKey domain models in tests.
"""
import uuid
from datetime import datetime, UTC
from typing import Optional, Dict, Any

from src.database.interfaces.models import User, UserAPIKey


class UserFactory:
    """Factory for creating User domain models with realistic test data."""
    
    @staticmethod
    def create(
        id: Optional[str] = None,
        email: Optional[str] = None,
        name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs
    ) -> User:
        """
        Create a User domain model with sensible defaults.
        
        Args:
            id: User ID (auto-generated UUID if not provided)
            email: User email (auto-generated if not provided)
            name: User display name (auto-generated based on email if not provided)
            avatar_url: User avatar URL (default None)
            metadata: User metadata dict (default empty)
            created_at: Creation timestamp (current time if not provided)
            updated_at: Update timestamp (current time if not provided)
            **kwargs: Additional keyword arguments
            
        Returns:
            Properly constructed User domain model
        """
        # Generate defaults
        user_id = id or str(uuid.uuid4())
        user_email = email or f"test_user_{user_id[:8]}@example.com"
        user_name = name or f"Test User {user_id[:8]}"
        now = datetime.now(UTC).replace(tzinfo=None)
        
        # Default metadata
        if metadata is None:
            metadata = {
                "registration_source": "test",
                "preferences": {
                    "theme": "dark",
                    "notifications": True
                }
            }
        
        return User(
            id=user_id,
            email=user_email,
            name=user_name,
            avatar_url=avatar_url,
            metadata=metadata,
            created_at=created_at or now,
            updated_at=updated_at or now,
        )
    
    @staticmethod
    def create_author() -> User:
        """Create a user representing a fantasy author."""
        return UserFactory.create(
            email="author@fantasywriter.com",
            name="Epic Fantasy Author",
            avatar_url="https://example.com/author-avatar.jpg",
            metadata={
                "role": "author",
                "genres": ["fantasy", "adventure", "epic"],
                "writing_goals": {
                    "daily_words": 1000,
                    "projects_per_year": 2
                },
                "preferences": {
                    "theme": "dark",
                    "auto_save": True,
                    "word_count_visible": True
                }
            }
        )
    
    @staticmethod
    def create_editor() -> User:
        """Create a user representing an editor."""
        return UserFactory.create(
            email="editor@publishing.com",
            name="Professional Editor",
            avatar_url="https://example.com/editor-avatar.jpg",
            metadata={
                "role": "editor",
                "specializations": ["fantasy", "sci-fi", "young-adult"],
                "experience_years": 10,
                "preferences": {
                    "theme": "light",
                    "show_tracking_changes": True,
                    "highlight_suggestions": True
                }
            }
        )
    
    @staticmethod
    def create_with_minimal_data() -> User:
        """Create a user with only required fields."""
        return UserFactory.create(
            name=None,
            avatar_url=None,
            metadata={}
        )


class UserAPIKeyFactory:
    """Factory for creating UserAPIKey domain models with realistic test data."""
    
    @staticmethod
    def create(
        user_id: Optional[str] = None,
        provider: str = "openai",
        encrypted_api_key: str = "encrypted_key_data_123",
        validation_status: str = "valid",
        last_validated_at: Optional[datetime] = None,
        provider_metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs
    ) -> UserAPIKey:
        """
        Create a UserAPIKey domain model with sensible defaults.
        
        Args:
            user_id: User ID (auto-generated UUID if not provided)
            provider: LLM provider ID (default "openai")
            encrypted_api_key: Encrypted API key string (default test value)
            validation_status: Validation status (default "valid")
            last_validated_at: Last validation timestamp (current time if not provided)
            provider_metadata: Provider-specific metadata (default empty)
            created_at: Creation timestamp (current time if not provided)
            updated_at: Update timestamp (current time if not provided)
            **kwargs: Additional keyword arguments
            
        Returns:
            Properly constructed UserAPIKey domain model
        """
        # Generate defaults
        key_user_id = user_id or str(uuid.uuid4())
        now = datetime.now(UTC).replace(tzinfo=None)
        
        # Default provider metadata
        if provider_metadata is None:
            provider_metadata = {
                "model_access": ["gpt-3.5-turbo", "gpt-4"],
                "rate_limits": {
                    "requests_per_minute": 60,
                    "tokens_per_minute": 60000
                },
                "organization_id": None
            }
        
        return UserAPIKey(
            user_id=key_user_id,
            provider=provider,
            encrypted_api_key=encrypted_api_key,
            validation_status=validation_status,
            last_validated_at=last_validated_at or now,
            provider_metadata=provider_metadata,
            created_at=created_at or now,
            updated_at=updated_at or now,
        )
    
    @staticmethod
    def create_openai_key(user_id: Optional[str] = None) -> UserAPIKey:
        """Create an OpenAI API key with realistic metadata."""
        return UserAPIKeyFactory.create(
            user_id=user_id,
            provider="openai",
            encrypted_api_key="encrypted_openai_key_12345",
            validation_status="valid",
            provider_metadata={
                "model_access": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                "rate_limits": {
                    "requests_per_minute": 500,
                    "tokens_per_minute": 80000
                },
                "organization_id": "org-123456789",
                "usage_tier": "tier-2"
            }
        )
    
    @staticmethod
    def create_anthropic_key(user_id: Optional[str] = None) -> UserAPIKey:
        """Create an Anthropic API key with realistic metadata."""
        return UserAPIKeyFactory.create(
            user_id=user_id,
            provider="anthropic",
            encrypted_api_key="encrypted_anthropic_key_67890",
            validation_status="valid",
            provider_metadata={
                "model_access": ["claude-3-sonnet-20240229", "claude-3-opus-20240229"],
                "rate_limits": {
                    "requests_per_minute": 60,
                    "tokens_per_minute": 40000
                },
                "usage_tier": "standard"
            }
        )
    
    @staticmethod
    def create_invalid_key(user_id: Optional[str] = None) -> UserAPIKey:
        """Create an invalid API key for testing error scenarios."""
        past_time = datetime.now(UTC).replace(tzinfo=None)
        
        return UserAPIKeyFactory.create(
            user_id=user_id,
            provider="openai",
            encrypted_api_key="encrypted_invalid_key_999",
            validation_status="invalid",
            last_validated_at=past_time,
            provider_metadata={
                "error": "Invalid API key",
                "error_code": "invalid_api_key",
                "last_error_at": past_time.isoformat()
            }
        )
    
    @staticmethod
    def create_expired_key(user_id: Optional[str] = None) -> UserAPIKey:
        """Create an expired API key for testing expiration scenarios."""
        past_time = datetime.now(UTC).replace(tzinfo=None)
        
        return UserAPIKeyFactory.create(
            user_id=user_id,
            provider="openai",
            encrypted_api_key="encrypted_expired_key_555",
            validation_status="expired",
            last_validated_at=past_time,
            provider_metadata={
                "error": "API key expired",
                "error_code": "api_key_expired",
                "expires_at": past_time.isoformat()
            }
        )