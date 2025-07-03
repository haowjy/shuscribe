"""
Comprehensive tests for UserService with memory repositories
"""

import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock

from src.schemas.db.user import SubscriptionTier, User, UserCreate, UserUpdate, UserAPIKeyCreate
from src.services.user.user_service import UserService
from src.database.factory import RepositoryContainer


@pytest.fixture
async def user_service(repository_container: RepositoryContainer) -> UserService:
    """Provide UserService with memory repository."""
    return UserService(user_repository=repository_container.user)


@pytest.fixture
async def sample_user(user_service: UserService) -> User:
    """Create a sample user for testing."""
    user_data = UserCreate(
        email="sample@example.com",
        display_name="Sample User"
    )
    return await user_service.create_user(user_data)


class TestUserManagement:
    """Test user CRUD operations"""
    
    async def test_create_user_success(self, user_service: UserService):
        """Test creating a new user"""
        user_data = UserCreate(
            email="newuser@example.com",
            display_name="New User"
        )
        
        user = await user_service.create_user(user_data)
        
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.display_name == "New User"
        assert user.created_at is not None
    
    async def test_create_user_duplicate_email(self, user_service: UserService):
        """Test error when creating user with duplicate email"""
        # Create first user
        user_data = UserCreate(
            email="duplicate@example.com",
            display_name="First User"
        )
        await user_service.create_user(user_data)
        
        # Try to create another with same email
        duplicate_data = UserCreate(
            email="duplicate@example.com",
            display_name="Second User"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await user_service.create_user(duplicate_data)
        
        assert "User with email duplicate@example.com already exists" in str(exc_info.value)
    
    async def test_get_user_by_id(self, user_service: UserService, sample_user: User):
        """Test retrieving user by ID"""
        retrieved_user = await user_service.get_user(sample_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == sample_user.id
        assert retrieved_user.email == sample_user.email
    
    async def test_get_user_not_found(self, user_service: UserService):
        """Test retrieving non-existent user returns None"""
        fake_id = uuid4()
        user = await user_service.get_user(fake_id)
        assert user is None
    
    async def test_get_user_by_email(self, user_service: UserService, sample_user: User):
        """Test retrieving user by email"""
        user = await user_service.get_user_by_email(sample_user.email)
        
        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email
    
    async def test_update_user_success(self, user_service: UserService, sample_user: User):
        """Test updating user information"""
        update_data = UserUpdate(
            display_name="Updated Name",
            subscription_tier=SubscriptionTier.PREMIUM
        )
        
        updated_user = await user_service.update_user(sample_user.id, update_data)
        
        assert updated_user.display_name == "Updated Name"
        assert updated_user.subscription_tier == SubscriptionTier.PREMIUM
        assert updated_user.email == sample_user.email  # Unchanged
    
    async def test_update_user_email_change(self, user_service: UserService, sample_user: User):
        """Test changing user email"""
        update_data = UserUpdate(email="newemail@example.com")
        
        updated_user = await user_service.update_user(sample_user.id, update_data)
        
        assert updated_user.email == "newemail@example.com"
        assert updated_user.id == sample_user.id
    
    async def test_update_user_email_conflict(self, user_service: UserService, sample_user: User):
        """Test error when changing email to existing one"""
        # Create another user
        other_user_data = UserCreate(
            email="other@example.com",
            display_name="Other User"
        )
        await user_service.create_user(other_user_data)
        
        # Try to update first user's email to match second
        update_data = UserUpdate(email="other@example.com")
        
        with pytest.raises(ValueError) as exc_info:
            await user_service.update_user(sample_user.id, update_data)
        
        assert "Email other@example.com is already in use" in str(exc_info.value)
    
    async def test_update_user_not_found(self, user_service: UserService):
        """Test error when updating non-existent user"""
        fake_id = uuid4()
        update_data = UserUpdate(display_name="New Name")
        
        with pytest.raises(ValueError) as exc_info:
            await user_service.update_user(fake_id, update_data)
        
        assert f"User {fake_id} not found" in str(exc_info.value)
    
    async def test_delete_user_success(self, user_service: UserService, sample_user: User):
        """Test deleting an existing user"""
        result = await user_service.delete_user(sample_user.id)
        assert result is True
        
        # Verify user is gone
        retrieved = await user_service.get_user(sample_user.id)
        assert retrieved is None
    
    async def test_delete_user_not_found(self, user_service: UserService):
        """Test deleting non-existent user returns False"""
        fake_id = uuid4()
        result = await user_service.delete_user(fake_id)
        assert result is False
    
    async def test_list_users(self, user_service: UserService):
        """Test listing users with pagination"""
        # Create multiple users
        for i in range(5):
            await user_service.create_user(UserCreate(
                email=f"user{i}@example.com",
                display_name=f"User {i}"
            ))
        
        # Get first page
        users = await user_service.list_users(offset=0, limit=3)
        assert len(users) == 3
        
        # Get second page
        users = await user_service.list_users(offset=3, limit=3)
        assert len(users) == 2
    
    async def test_list_users_limit_cap(self, user_service: UserService):
        """Test that list users caps limit at 1000"""
        users = await user_service.list_users(offset=0, limit=2000)
        # Should work without error, limit internally capped
        assert isinstance(users, list)
    
    async def test_get_users_by_subscription_tier(self, user_service: UserService):
        """Test filtering users by subscription tier"""
        # Create users with different tiers
        await user_service.create_user(UserCreate(
            email="free1@example.com",
            display_name="Free User 1",
            subscription_tier=SubscriptionTier.FREE_BYOK
        ))
        await user_service.create_user(UserCreate(
            email="premium1@example.com",
            display_name="Premium User 1",
            subscription_tier=SubscriptionTier.PREMIUM
        ))
        await user_service.create_user(UserCreate(
            email="free2@example.com",
            display_name="Free User 2",
            subscription_tier=SubscriptionTier.FREE_BYOK
        ))
        
        # Get free tier users
        free_users = await user_service.get_users_by_subscription_tier(SubscriptionTier.FREE_BYOK)
        assert len(free_users) == 2
        assert all(u.subscription_tier == SubscriptionTier.FREE_BYOK for u in free_users)


class TestAPIKeyManagement:
    """Test BYOK API key operations"""
    
    async def test_store_api_key_success(self, user_service: UserService, sample_user: User):
        """Test storing and encrypting an API key"""
        api_key = "sk-test-1234567890abcdef"
        provider = "openai"
        metadata = {"model": "gpt-4", "org_id": "org-123"}
        
        stored_key = await user_service.store_api_key(
            sample_user.id,
            provider,
            api_key,
            metadata
        )
        
        assert stored_key.user_id == sample_user.id
        assert stored_key.provider == provider
        assert stored_key.provider_metadata == metadata
        assert stored_key.validation_status == "pending"
        # Key should be encrypted
        assert stored_key.encrypted_api_key != api_key
    
    async def test_store_api_key_data_success(self, user_service: UserService, sample_user: User):
        """Test storing API key using UserAPIKeyCreate object"""
        api_key_data = UserAPIKeyCreate(
            provider="anthropic",
            api_key="sk-ant-1234567890",
            provider_metadata={"tier": "pro"}
        )
        
        stored_key = await user_service.store_api_key_data(
            sample_user.id,
            api_key_data
        )
        
        assert stored_key.provider == "anthropic"
        assert stored_key.encrypted_api_key != "sk-ant-1234567890"
    
    async def test_store_api_key_user_not_found(self, user_service: UserService):
        """Test error when storing key for non-existent user"""
        fake_user_id = uuid4()
        
        with pytest.raises(ValueError) as exc_info:
            await user_service.store_api_key(
                fake_user_id,
                "openai",
                "sk-test-123"
            )
        
        assert f"User {fake_user_id} not found" in str(exc_info.value)
    
    async def test_get_api_key_success(self, user_service: UserService, sample_user: User):
        """Test retrieving and decrypting an API key"""
        # Store a key
        original_key = "sk-test-secret-key"
        await user_service.store_api_key(
            sample_user.id,
            "openai",
            original_key
        )
        
        # Retrieve it
        retrieved = await user_service.get_api_key(sample_user.id, "openai")
        
        assert retrieved is not None
        assert retrieved.encrypted_api_key == original_key  # Should be decrypted
        assert retrieved.provider == "openai"
    
    async def test_get_api_key_not_found(self, user_service: UserService, sample_user: User):
        """Test retrieving non-existent API key returns None"""
        key = await user_service.get_api_key(sample_user.id, "nonexistent") # type: ignore
        assert key is None
    
    @patch('src.services.user.user_service.decrypt_api_key')
    async def test_get_api_key_decryption_failure(self, mock_decrypt: MagicMock, user_service: UserService, sample_user: User):
        """Test handling of decryption failure"""
        # Store a key
        await user_service.store_api_key(
            sample_user.id,
            "openai",
            "sk-test-123"
        )
        
        # Mock decryption failure
        mock_decrypt.side_effect = Exception("Decryption failed")
        
        # Try to retrieve
        key = await user_service.get_api_key(sample_user.id, "openai")
        assert key is None
        
        # Verify status was updated to invalid
        repo_key = await user_service.user_repository.get_api_key(sample_user.id, "openai")
        assert repo_key.validation_status == "invalid" if repo_key else None
    
    async def test_update_api_key_validation(self, user_service: UserService, sample_user: User):
        """Test updating API key validation status"""
        # Store a key
        await user_service.store_api_key(
            sample_user.id,
            "openai",
            "sk-test-123"
        )
        
        # Update validation status
        updated = await user_service.update_api_key_validation(
            sample_user.id,
            "openai",
            "valid"
        )
        
        assert updated.validation_status == "valid"
    
    async def test_update_api_key_validation_invalid_status(self, user_service: UserService, sample_user: User):
        """Test error for invalid validation status"""
        with pytest.raises(ValueError) as exc_info:
            await user_service.update_api_key_validation(
                sample_user.id,
                "openai",
                "bad_status"
            )
        
        assert "Invalid validation status: bad_status" in str(exc_info.value)
    
    async def test_delete_api_key_success(self, user_service: UserService, sample_user: User):
        """Test deleting an API key"""
        # Store a key
        await user_service.store_api_key(
            sample_user.id,
            "openai",
            "sk-test-123"
        )
        
        # Delete it
        result = await user_service.delete_api_key(sample_user.id, "openai")
        assert result is True
        
        # Verify it's gone
        key = await user_service.get_api_key(sample_user.id, "openai")
        assert key is None
    
    async def test_get_user_api_keys(self, user_service: UserService, sample_user: User):
        """Test retrieving all API keys for a user"""
        # Store multiple keys
        await user_service.store_api_key(sample_user.id, "openai", "sk-openai-123")
        await user_service.store_api_key(sample_user.id, "anthropic", "sk-ant-456")
        
        # Get all keys
        keys = await user_service.get_user_api_keys(sample_user.id)
        
        assert len(keys) == 2
        providers = [k.provider for k in keys]
        assert "openai" in providers
        assert "anthropic" in providers
        # Keys should be decrypted
        assert any(k.encrypted_api_key == "sk-openai-123" for k in keys)
        assert any(k.encrypted_api_key == "sk-ant-456" for k in keys)
    
    @patch('src.services.user.user_service.decrypt_api_key')
    async def test_get_user_api_keys_skip_undecryptable(self, mock_decrypt: MagicMock, user_service: UserService, sample_user: User):
        """Test that undecryptable keys are skipped"""
        # Store two keys
        await user_service.store_api_key(sample_user.id, "openai", "sk-openai-123")
        await user_service.store_api_key(sample_user.id, "anthropic", "sk-ant-456")
        
        # Mock decrypt to fail for first key
        mock_decrypt.side_effect = [Exception("Failed"), "sk-ant-456"]
        
        # Get all keys
        keys = await user_service.get_user_api_keys(sample_user.id)
        
        # Should only get the second key
        assert len(keys) == 1
        assert keys[0].provider == "anthropic"
    
    async def test_get_validated_api_keys(self, user_service: UserService, sample_user: User):
        """Test retrieving only validated API keys"""
        # Store keys with different validation statuses
        key1 = await user_service.store_api_key(sample_user.id, "openai", "sk-1")
        await user_service.update_api_key_validation(sample_user.id, "openai", "valid")
        
        key2 = await user_service.store_api_key(sample_user.id, "anthropic", "sk-2")
        await user_service.update_api_key_validation(sample_user.id, "anthropic", "invalid")
        
        key3 = await user_service.store_api_key(sample_user.id, "cohere", "sk-3")
        await user_service.update_api_key_validation(sample_user.id, "cohere", "valid")
        
        # Get validated keys
        validated = await user_service.get_validated_api_keys(sample_user.id)
        
        assert len(validated) == 2
        providers = [k.provider for k in validated]
        assert "openai" in providers
        assert "cohere" in providers
        assert "anthropic" not in providers
    
    async def test_validate_api_key(self, user_service: UserService, sample_user: User):
        """Test API key validation (currently just marks as valid)"""
        # Store a key
        await user_service.store_api_key(sample_user.id, "openai", "sk-test")
        
        # Validate it
        result = await user_service.validate_api_key(sample_user.id, "openai")
        assert result is True
        
        # Check status
        key = await user_service.get_api_key(sample_user.id, "openai")
        assert key.validation_status == "valid" if key else None
    
    async def test_validate_api_key_not_found(self, user_service: UserService, sample_user: User):
        """Test validation of non-existent key returns False"""
        result = await user_service.validate_api_key(sample_user.id, "nonexistent") # type: ignore
        assert result is False


class TestIntegration:
    """Integration tests for user workflows"""
    
    async def test_full_user_workflow(self, user_service: UserService):
        """Test complete user lifecycle"""
        # 1. Create user
        user = await user_service.create_user(UserCreate(
            email="workflow@example.com",
            display_name="Workflow User"
        ))
        
        # 2. Store multiple API keys
        await user_service.store_api_key(user.id, "openai", "sk-openai-123")
        await user_service.store_api_key(user.id, "anthropic", "sk-ant-456")
        
        # 3. Validate one key
        await user_service.validate_api_key(user.id, "openai")
        
        # 4. Update user to premium
        await user_service.update_user(user.id, UserUpdate(subscription_tier=SubscriptionTier.PREMIUM))
        
        # 5. Get validated keys
        validated_keys = await user_service.get_validated_api_keys(user.id)
        assert len(validated_keys) == 1
        assert validated_keys[0].provider == "openai"
        
        # 6. Delete one key
        await user_service.delete_api_key(user.id, "anthropic")
        
        # 7. Verify final state
        user = await user_service.get_user(user.id)
        assert user is not None
        assert user.subscription_tier == SubscriptionTier.PREMIUM
        
        all_keys = await user_service.get_user_api_keys(user.id)
        assert len(all_keys) == 1
        assert all_keys[0].provider == "openai"