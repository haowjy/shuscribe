"""
Test suite for User Repository

Tests user CRUD operations, BYOK API key management, encryption, and edge cases.
"""

import json
import pytest
from datetime import datetime
from pathlib import Path
from typing import cast

from src.database.models.user import UserCreate, UserUpdate, UserAPIKeyCreate, SubscriptionTier
from src.database.file.user import FileUserRepository


class TestUserBasicOperations:
    """Test basic user CRUD operations."""
    
    async def test_get_current_user(self, user_repo):
        """Test getting the current user."""
        user = await cast(FileUserRepository, user_repo).get_current_user()
        
        assert user is not None
        assert user.email == "author@example.com"
        assert user.display_name == "Local Author"
        assert user.subscription_tier == SubscriptionTier.LOCAL
        assert user.id is not None
        assert user.created_at is not None
    
    async def test_create_user_updates_current(self, user_repo):
        """Test that creating a user updates the current user."""
        user_data = UserCreate(
            email="newauthor@example.com",
            display_name="New Author",
            subscription_tier=SubscriptionTier.LOCAL
        )
        
        created_user = await user_repo.create(user_data)
        current_user = await cast(FileUserRepository, user_repo).get_current_user()
        
        assert created_user.email == "newauthor@example.com"
        assert created_user.display_name == "New Author"
        assert current_user.email == created_user.email
        assert current_user.id == created_user.id
    
    async def test_get_user_by_id(self, user_repo):
        """Test getting user by ID."""
        current_user = await cast(FileUserRepository, user_repo).get_current_user()
        retrieved_user = await user_repo.get(current_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == current_user.id
        assert retrieved_user.email == current_user.email
    
    async def test_get_user_by_email(self, user_repo):
        """Test getting user by email."""
        current_user = await cast(FileUserRepository, user_repo).get_current_user()
        retrieved_user = await user_repo.get_by_email(current_user.email)
        
        assert retrieved_user is not None
        assert retrieved_user.id == current_user.id
        assert retrieved_user.email == current_user.email
    
    async def test_get_nonexistent_user(self, user_repo):
        """Test getting a user that doesn't exist."""
        from uuid import uuid4
        
        nonexistent_user = await user_repo.get(uuid4())
        assert nonexistent_user is None
    
    async def test_update_user(self, user_repo):
        """Test updating user information."""
        current_user = await cast(FileUserRepository, user_repo).get_current_user()
        
        update_data = UserUpdate(
            display_name="Updated Author",
            preferences={"theme": "dark", "auto_save": True}
        )
        
        updated_user = await user_repo.update(current_user.id, update_data)
        
        assert updated_user.display_name == "Updated Author"
        assert updated_user.preferences["theme"] == "dark"
        assert updated_user.preferences["auto_save"] is True
        assert updated_user.updated_at is not None
    
    async def test_get_multiple_users(self, user_repo):
        """Test getting multiple users (should return single user in local mode)."""
        users = await user_repo.get_multi()
        
        assert len(users) == 1
        assert users[0].email == "author@example.com"
    
    async def test_delete_user_resets_to_default(self, user_repo):
        """Test that deleting user resets to default configuration."""
        current_user = await cast(FileUserRepository, user_repo).get_current_user()
        
        # Update user first
        await user_repo.update(current_user.id, UserUpdate(
            display_name="To Be Deleted"
        ))
        
        # Delete user
        deleted = await user_repo.delete(current_user.id)
        assert deleted is True
        
        # Should have reset to default
        new_current = await cast(FileUserRepository, user_repo).get_current_user()
        assert new_current.display_name == "Local Author"
        assert new_current.id != current_user.id  # Should be new user


class TestAPIKeyManagement:
    """Test BYOK API key management functionality."""
    
    async def test_store_api_key(self, user_repo):
        """Test storing an API key."""
        user = await cast(FileUserRepository, user_repo).get_current_user()
        
        api_key_data = UserAPIKeyCreate(
            provider="openai",
            api_key="sk-test-123456",
            provider_metadata={"model": "gpt-4", "max_tokens": 4000}
        )
        
        stored_key = await user_repo.store_api_key(user.id, api_key_data)
        
        assert stored_key.provider == "openai"
        assert stored_key.encrypted_api_key == "sk-test-123456"
        assert stored_key.provider_metadata["model"] == "gpt-4"
        assert stored_key.validation_status == "pending"
    
    async def test_get_api_key(self, user_repo):
        """Test retrieving an API key."""
        user = await cast(FileUserRepository, user_repo).get_current_user()
        
        # Store key first
        api_key_data = UserAPIKeyCreate(
            provider="anthropic",
            api_key="sk-ant-789012",
            provider_metadata={"model": "claude-3-sonnet"}
        )
        await user_repo.store_api_key(user.id, api_key_data)
        
        # Retrieve key
        retrieved_key = await user_repo.get_api_key(user.id, "anthropic")
        
        assert retrieved_key is not None
        assert retrieved_key.provider == "anthropic"
        assert retrieved_key.encrypted_api_key == "sk-ant-789012"
        assert retrieved_key.provider_metadata["model"] == "claude-3-sonnet"
    
    async def test_get_all_api_keys(self, user_repo, sample_api_keys):
        """Test getting all API keys for a user."""
        user = await cast(FileUserRepository, user_repo).get_current_user()
        
        # Store multiple keys
        for api_key_data in sample_api_keys:
            await user_repo.store_api_key(user.id, api_key_data)
        
        # Get all keys
        all_keys = await user_repo.get_all_api_keys(user.id)
        
        assert len(all_keys) == 3
        providers = {key.provider for key in all_keys}
        assert providers == {"openai", "anthropic", "google"}
    
    async def test_update_existing_api_key(self, user_repo):
        """Test updating an existing API key."""
        user = await cast(FileUserRepository, user_repo).get_current_user()
        
        # Store initial key
        initial_key = UserAPIKeyCreate(
            provider="openai",
            api_key="sk-old-key",
            provider_metadata={"model": "gpt-3.5-turbo"}
        )
        await user_repo.store_api_key(user.id, initial_key)
        
        # Update with new key
        updated_key = UserAPIKeyCreate(
            provider="openai",
            api_key="sk-new-key",
            provider_metadata={"model": "gpt-4"}
        )
        result = await user_repo.store_api_key(user.id, updated_key)
        
        assert result.encrypted_api_key == "sk-new-key"
        assert result.provider_metadata["model"] == "gpt-4"
        
        # Verify only one key exists for this provider
        retrieved = await user_repo.get_api_key(user.id, "openai")
        assert retrieved.encrypted_api_key == "sk-new-key"
    
    async def test_delete_api_key(self, user_repo):
        """Test deleting an API key."""
        user = await cast(FileUserRepository, user_repo).get_current_user()
        
        # Store key first
        api_key_data = UserAPIKeyCreate(
            provider="test-provider",
            api_key="test-key"
        )
        await user_repo.store_api_key(user.id, api_key_data)
        
        # Verify key exists
        retrieved = await user_repo.get_api_key(user.id, "test-provider")
        assert retrieved is not None
        
        # Delete key
        deleted = await user_repo.delete_api_key(user.id, "test-provider")
        assert deleted is True
        
        # Verify key is gone
        retrieved = await user_repo.get_api_key(user.id, "test-provider")
        assert retrieved is None
    
    async def test_validate_api_key(self, user_repo):
        """Test API key validation."""
        user = await cast(FileUserRepository, user_repo).get_current_user()
        
        # Store key
        api_key_data = UserAPIKeyCreate(
            provider="test-provider",
            api_key="test-key"
        )
        await user_repo.store_api_key(user.id, api_key_data)
        
        # Validate key (this just marks it as valid in file storage)
        validated = await user_repo.validate_api_key(user.id, "test-provider")
        assert validated is True
        
        # Check that status was updated
        retrieved = await user_repo.get_api_key(user.id, "test-provider")
        assert retrieved.validation_status == "valid"


class TestEncryption:
    """Test API key encryption functionality."""
    
    async def test_api_key_encrypted_in_storage(self, temp_workspace_path, config_checker):
        """Test that API keys are encrypted when stored."""
        from src.database.factory import get_repositories
        
        repos = get_repositories(backend="file", workspace_path=temp_workspace_path)
        user = await cast(FileUserRepository, repos.user).get_current_user()
        
        # Store API key
        api_key_data = UserAPIKeyCreate(
            provider="test",
            api_key="sk-secret-key-12345"
        )
        await repos.user.store_api_key(user.id, api_key_data)
        
        # Check config file directly
        config_data = config_checker(temp_workspace_path)
        stored_key = config_data["api_keys"]["test"]["encrypted_key"]
        
        # Should be encrypted (not the original key)
        assert stored_key != "sk-secret-key-12345"
        assert len(stored_key) > 20  # Encrypted keys are longer
        assert stored_key.startswith("gAAAAA")  # Fernet token format
    
    async def test_api_key_decrypted_on_retrieval(self, user_repo):
        """Test that API keys are decrypted when retrieved."""
        user = await cast(FileUserRepository, user_repo).get_current_user()
        
        original_key = "sk-secret-key-98765"
        api_key_data = UserAPIKeyCreate(
            provider="decrypt-test",
            api_key=original_key
        )
        
        # Store encrypted
        await user_repo.store_api_key(user.id, api_key_data)
        
        # Retrieve decrypted
        retrieved = await user_repo.get_api_key(user.id, "decrypt-test")
        assert retrieved.encrypted_api_key == original_key
    
    async def test_config_file_permissions(self, temp_workspace_path):
        """Test that config files have secure permissions."""
        from src.database.factory import get_repositories
        import stat
        
        repos = get_repositories(backend="file", workspace_path=temp_workspace_path)
        await cast(FileUserRepository, repos.user).get_current_user()  # Creates config
        
        config_file = temp_workspace_path / ".shuscribe" / "config.json"
        assert config_file.exists()
        
        # Check permissions (should be 600 - owner read/write only)
        mode = config_file.stat().st_mode
        assert stat.S_IMODE(mode) == 0o600


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    async def test_nonexistent_user_api_operations(self, user_repo):
        """Test API operations on nonexistent users."""
        from uuid import uuid4
        
        fake_user_id = uuid4()
        
        # Should return None/False for nonexistent user
        key = await user_repo.get_api_key(fake_user_id, "openai")
        assert key is None
        
        all_keys = await user_repo.get_all_api_keys(fake_user_id)
        assert len(all_keys) == 0
        
        deleted = await user_repo.delete_api_key(fake_user_id, "openai")
        assert deleted is False
    
    async def test_invalid_provider_operations(self, user_repo):
        """Test operations on nonexistent providers."""
        user = await cast(FileUserRepository, user_repo).get_current_user()
        
        # Get nonexistent provider
        key = await user_repo.get_api_key(user.id, "nonexistent-provider")
        assert key is None
        
        # Delete nonexistent provider
        deleted = await user_repo.delete_api_key(user.id, "nonexistent-provider")
        assert deleted is False
    
    async def test_empty_api_key(self, user_repo):
        """Test storing empty API key."""
        user = await cast(FileUserRepository, user_repo).get_current_user()
        
        api_key_data = UserAPIKeyCreate(
            provider="empty-test",
            api_key=""
        )
        
        stored = await user_repo.store_api_key(user.id, api_key_data)
        assert stored.encrypted_api_key == ""
        
        retrieved = await user_repo.get_api_key(user.id, "empty-test")
        assert retrieved.encrypted_api_key == ""
    
    async def test_special_characters_in_api_key(self, user_repo):
        """Test API keys with special characters."""
        user = await cast(FileUserRepository, user_repo).get_current_user()
        
        special_key = "sk-test!@#$%^&*()_+-=[]{}|;':\",./<>?"
        api_key_data = UserAPIKeyCreate(
            provider="special-chars",
            api_key=special_key
        )
        
        stored = await user_repo.store_api_key(user.id, api_key_data)
        retrieved = await user_repo.get_api_key(user.id, "special-chars")
        
        assert retrieved.encrypted_api_key == special_key
    
    async def test_large_provider_metadata(self, user_repo):
        """Test storing large provider metadata."""
        user = await cast(FileUserRepository, user_repo).get_current_user()
        
        large_metadata = {
            "model": "gpt-4",
            "settings": {
                "temperature": 0.7,
                "max_tokens": 4000,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "stop": ["Human:", "Assistant:"],
                "custom_instructions": "This is a very long custom instruction " * 50
            },
            "usage_limits": {
                "daily_limit": 1000,
                "monthly_limit": 30000,
                "rate_limit": 60
            }
        }
        
        api_key_data = UserAPIKeyCreate(
            provider="large-metadata",
            api_key="sk-test-123",
            provider_metadata=large_metadata
        )
        
        stored = await user_repo.store_api_key(user.id, api_key_data)
        retrieved = await user_repo.get_api_key(user.id, "large-metadata")
        
        assert retrieved.provider_metadata == large_metadata
        assert len(retrieved.provider_metadata["settings"]["custom_instructions"]) > 1000


@pytest.mark.slow
class TestUserPerformance:
    """Performance tests for user operations."""
    
    async def test_multiple_api_keys_performance(self, user_repo):
        """Test performance with many API keys."""
        import time
        
        user = await cast(FileUserRepository, user_repo).get_current_user()
        
        # Store many API keys
        start_time = time.time()
        for i in range(50):
            api_key_data = UserAPIKeyCreate(
                provider=f"provider-{i:03d}",
                api_key=f"sk-key-{i:03d}-{'x' * 50}",
                provider_metadata={"model": f"model-{i}", "index": i}
            )
            await user_repo.store_api_key(user.id, api_key_data)
        
        store_time = time.time() - start_time
        
        # Retrieve all keys
        start_time = time.time()
        all_keys = await user_repo.get_all_api_keys(user.id)
        retrieve_time = time.time() - start_time
        
        assert len(all_keys) == 50
        assert store_time < 5.0  # Should store 50 keys in under 5 seconds
        assert retrieve_time < 1.0  # Should retrieve 50 keys in under 1 second
        
        print(f"Stored 50 keys in {store_time:.2f}s, retrieved in {retrieve_time:.2f}s") 