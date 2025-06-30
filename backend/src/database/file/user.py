"""
File-Based User Repository Implementation

Desktop-optimized user repository with single config file per workspace.
Stores user data and encrypted API keys in .shuscribe/config.json.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from src.database.interfaces.user import IUserRepository
from src.database.models.user import User, UserAPIKey, UserCreate, UserUpdate, UserAPIKeyCreate, SubscriptionTier
from src.database.file.utils import FileManager
from src.database.file.encryption import FileEncryption, FileStorageConfig


class FileUserRepository(IUserRepository):
    """Desktop-optimized user repository with single config file"""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.file_manager = FileManager(workspace_path)
        
        # Desktop-specific file paths
        structure = self.file_manager.get_workspace_structure()
        self.config_file = structure['system'] / "config.json"
        
        # Encryption setup
        self.config = FileStorageConfig()
        self.encryption = FileEncryption(
            encryption_enabled=self.config.encrypt_api_keys,
            master_key=self.config.master_key
        )
        
        # For local usage, we typically have one "user" per workspace
        self._current_user_id: Optional[UUID] = None
        self._load_or_create_config()
    
    def _load_or_create_config(self) -> None:
        """Load or create the local configuration"""
        config_data = self.file_manager.read_json_file(self.config_file)
        
        if config_data and "user_id" in config_data:
            try:
                self._current_user_id = UUID(config_data["user_id"])
            except ValueError:
                # Invalid UUID, create new config
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default configuration for new workspace"""
        self._current_user_id = uuid4()
        config_data = {
            "user_id": str(self._current_user_id),
            "workspace_name": self.workspace_path.name,
            "display_name": "Local Author",
            "email": "author@example.com",
            "subscription_tier": SubscriptionTier.LOCAL.value,
            "api_keys": {},
            "preferences": {
                "default_provider": "openai",
                "encrypt_keys": self.config.encrypt_api_keys
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        }
        self._save_config(config_data)
    
    def _save_config(self, config_data: dict) -> None:
        """Save configuration to file with secure permissions"""
        self.file_manager.write_json_file(self.config_file, config_data, secure=True)
    
    def _load_config(self) -> dict:
        """Load configuration from file"""
        config_data = self.file_manager.read_json_file(self.config_file)
        if not config_data:
            self._create_default_config()
            config_data = self.file_manager.read_json_file(self.config_file)
        return config_data

    async def get_current_user(self) -> User:
        """Get the current local user"""
        if self._current_user_id is None:
            self._load_or_create_config()
        
        config_data = self._load_config()
        return User(
            id=self._current_user_id,  # type: ignore - guaranteed to be set by _load_or_create_config
            email=config_data.get("email", "author@example.com"),
            display_name=config_data.get("display_name", "Local Author"),
            subscription_tier=SubscriptionTier(config_data.get("subscription_tier", SubscriptionTier.LOCAL.value)),
            preferences=config_data.get("preferences", {}),
            created_at=datetime.fromisoformat(config_data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(config_data["updated_at"]) if config_data.get("updated_at") else None
        )

    async def get(self, id: UUID) -> Optional[User]:
        """Get user by ID (local mode returns current user if ID matches)"""
        if id == self._current_user_id:
            return await self.get_current_user()
        return None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email (local mode returns current user if email matches)"""
        user = await self.get_current_user()
        if user.email.lower() == email.lower():
            return user
        return None

    async def get_multi(self, *, offset: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users (local mode returns single user)"""
        if offset == 0:
            return [await self.get_current_user()]
        return []

    async def create(self, user_data: UserCreate) -> User:
        """Create user (local mode updates current user)"""
        config_data = self._load_config()
        
        # Update with new user data
        config_data.update({
            "email": user_data.email,
            "display_name": user_data.display_name,
            "subscription_tier": user_data.subscription_tier.value,
            "preferences": user_data.preferences,
            "updated_at": datetime.now().isoformat()
        })
        
        self._save_config(config_data)
        return await self.get_current_user()

    async def update(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update user (local mode updates current user)"""
        if user_id != self._current_user_id:
            raise ValueError("User not found")
        
        config_data = self._load_config()
        
        # Update fields
        update_dict = user_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if field not in ['id', 'created_at']:  # Don't update immutable fields
                if field == 'subscription_tier' and hasattr(value, 'value'):
                    config_data[field] = value.value
                else:
                    config_data[field] = value
        
        config_data['updated_at'] = datetime.now().isoformat()
        self._save_config(config_data)
        
        return await self.get_current_user()

    async def delete(self, user_id: UUID) -> bool:
        """Delete user (local mode resets to default)"""
        if user_id != self._current_user_id:
            return False
        
        # Reset to default configuration
        self._create_default_config()
        return True

    # BYOK API Key Management
    async def store_api_key(self, user_id: UUID, api_key_data: UserAPIKeyCreate) -> UserAPIKey:
        """Store API key in local config"""
        if user_id != self._current_user_id:
            raise ValueError("User not found")
        
        config_data = self._load_config()
        
        if "api_keys" not in config_data:
            config_data["api_keys"] = {}
        
        # Encrypt and store
        encrypted_key = self.encryption.encrypt(api_key_data.api_key)
        config_data["api_keys"][api_key_data.provider] = {
            "encrypted_key": encrypted_key,
            "provider_metadata": api_key_data.provider_metadata,
            "validation_status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        }
        
        self._save_config(config_data)
        
        return UserAPIKey(
            user_id=user_id,
            provider=api_key_data.provider,
            encrypted_api_key=api_key_data.api_key,  # Return decrypted for use
            provider_metadata=api_key_data.provider_metadata,
            validation_status="pending",
            created_at=datetime.now(),
            updated_at=None
        )

    async def get_api_key(self, user_id: UUID, provider: str) -> Optional[UserAPIKey]:
        """Get user's API key for a specific provider"""
        if user_id != self._current_user_id:
            return None
        
        config_data = self._load_config()
        api_keys = config_data.get("api_keys", {})
        
        if provider not in api_keys:
            return None
        
        key_data = api_keys[provider]
        decrypted_key = self.encryption.decrypt(key_data["encrypted_key"])
        
        return UserAPIKey(
            user_id=user_id,
            provider=provider,
            encrypted_api_key=decrypted_key,  # Return decrypted for use
            provider_metadata=key_data.get("provider_metadata", {}),
            validation_status=key_data.get("validation_status", "pending"),
            last_validated_at=datetime.fromisoformat(key_data["last_validated_at"]) if key_data.get("last_validated_at") else None,
            created_at=datetime.fromisoformat(key_data["created_at"]),
            updated_at=datetime.fromisoformat(key_data["updated_at"]) if key_data.get("updated_at") else None
        )

    async def get_all_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get all API keys for user"""
        if user_id != self._current_user_id:
            return []
        
        config_data = self._load_config()
        api_keys = config_data.get("api_keys", {})
        
        result = []
        for provider, key_data in api_keys.items():
            decrypted_key = self.encryption.decrypt(key_data["encrypted_key"])
            result.append(UserAPIKey(
                user_id=user_id,
                provider=provider,
                encrypted_api_key=decrypted_key,
                provider_metadata=key_data.get("provider_metadata", {}),
                validation_status=key_data.get("validation_status", "pending"),
                last_validated_at=datetime.fromisoformat(key_data["last_validated_at"]) if key_data.get("last_validated_at") else None,
                created_at=datetime.fromisoformat(key_data["created_at"]),
                updated_at=datetime.fromisoformat(key_data["updated_at"]) if key_data.get("updated_at") else None
            ))
        
        return result

    async def delete_api_key(self, user_id: UUID, provider: str) -> bool:
        """Delete user's API key"""
        if user_id != self._current_user_id:
            return False
        
        config_data = self._load_config()
        api_keys = config_data.get("api_keys", {})
        
        if provider in api_keys:
            del api_keys[provider]
            config_data["updated_at"] = datetime.now().isoformat()
            self._save_config(config_data)
            return True
        
        return False

    async def validate_api_key(self, user_id: UUID, provider: str) -> bool:
        """Validate API key (implementation depends on provider)"""
        api_key = await self.get_api_key(user_id, provider)
        if not api_key:
            return False
        
        # Update validation status in config
        config_data = self._load_config()
        if provider in config_data.get("api_keys", {}):
            config_data["api_keys"][provider]["validation_status"] = "valid"
            config_data["api_keys"][provider]["last_validated_at"] = datetime.now().isoformat()
            config_data["api_keys"][provider]["updated_at"] = datetime.now().isoformat()
            self._save_config(config_data)
        
        return True 