# ShuScribe Storage Architecture Implementation Plan

## Overview

This document outlines the implementation plan for the ShuScribe Storage Architecture v3.0, focusing on workspace-centric storage with chapter-based versioning, user management with BYOK (Bring Your Own Key) support, and dual storage backends (file-based + database).

## Architecture Principles

### 1. Separation of Concerns
- **Storage Interface**: Abstract interface defining core storage operations
- **Storage Backends**: Concrete implementations (FileStorage, DatabaseStorage)
- **Domain Models**: Pydantic models with validation and serialization
- **Managers**: Business logic orchestration layer
- **Services**: High-level application services
- **User Management**: Separate user/auth layer with BYOK API key management

### 2. Single Responsibility
- Each class has one clear purpose
- Methods are focused and simple
- Clear boundaries between data access and business logic
- User management separated from workspace/content management

### 3. Dependency Inversion
- Core logic depends on abstractions, not implementations
- Storage backends implement common interfaces
- Easy to swap between file-based and database storage
- User repositories follow same pattern as content repositories

## Implementation Structure

```
backend/src/database/
├── models/                     # Pydantic domain models
│   ├── __init__.py
│   ├── user.py                # User, UserAPIKey, SubscriptionTier
│   ├── workspace.py           # Workspace, Arc, ProcessingState
│   ├── story.py               # Chapter, Draft, StoryContent, StoryMetadata
│   ├── wiki.py                # WikiArticle, ChapterVersion, EditVersion, Connections
│   └── writing.py             # AuthorNotes, AIConversation, Research, WritingTools
├── interfaces/                 # Abstract repository interfaces
│   ├── __init__.py
│   ├── user.py                # IUserRepository
│   ├── workspace.py           # IWorkspaceRepository
│   ├── story.py               # IStoryRepository
│   ├── wiki.py                # IWikiRepository (includes connections)
│   └── writing.py             # IWritingRepository
├── memory/                     # In-memory implementations (testing/local)
│   ├── __init__.py            # Memory backend factory
│   ├── user.py                # InMemoryUserRepository
│   ├── workspace.py           # InMemoryWorkspaceRepository
│   ├── story.py               # InMemoryStoryRepository
│   ├── wiki.py                # InMemoryWikiRepository
│   └── writing.py             # InMemoryWritingRepository
├── file/                       # File-based implementations
│   ├── __init__.py            # File backend factory
│   ├── user.py                # FileUserRepository (with encryption)
│   ├── workspace.py           # FileWorkspaceRepository
│   ├── story.py               # FileStoryRepository
│   ├── wiki.py                # FileWikiRepository
│   ├── writing.py             # FileWritingRepository
│   ├── encryption.py          # File encryption utilities
│   └── utils.py               # File operation utilities
├── supabase/                   # Supabase implementations
│   ├── __init__.py            # Supabase backend factory
│   ├── user.py                # SupabaseUserRepository
│   ├── workspace.py           # SupabaseWorkspaceRepository
│   ├── story.py               # SupabaseStoryRepository
│   ├── wiki.py                # SupabaseWikiRepository
│   └── writing.py             # SupabaseWritingRepository
├── managers/                   # Business logic layer
│   ├── __init__.py
│   ├── user_manager.py        # UserManager - user operations with BYOK
│   ├── workspace_manager.py   # WorkspaceManager - workspace operations
│   ├── story_manager.py       # StoryManager - story and chapter operations
│   ├── wiki_manager.py        # WikiManager - wiki versioning and connections
│   └── writing_manager.py     # WritingManager - author tools and notes
├── services/                   # High-level services
│   ├── __init__.py
│   ├── storage_service.py     # StorageService - main application interface
│   └── correction_service.py  # CorrectionPropagationAgent
├── factory.py                  # Main backend factory (no circular imports!)
└── migrations/                 # Database migrations
    ├── __init__.py
    └── sql/                   # SQL migration files
```

## Repository Domains

The storage architecture is organized around five core domains:

1. **`user`** - User profiles, authentication, BYOK API keys
2. **`workspace`** - Workspace management, arcs, processing state  
3. **`story`** - All story content: published chapters, drafts, chapter versions, story metadata
4. **`wiki`** - AI-generated articles with versioning, connections, spoiler protection
5. **`writing`** - Author workspace tools: AI conversations, research notes, outlines, writing prompts, planning tools

### Domain Boundaries

- **`story`** handles the **narrative content itself**: published chapters, draft chapters, chapter revisions, story metadata, publication status
- **`wiki`** handles **reference material**: character profiles, location guides, chapter-based versioning for spoiler prevention, article connections and cross-references
- **`writing`** handles the **author's creative process**: AI conversation history, research notes, story planning, character development worksheets, writing tools and templates

## Core Models (Pydantic)

### User Models

- **`User`** - Core user profile with subscription tier, email, preferences
- **`UserAPIKey`** - BYOK API key storage with encryption, validation status, provider metadata
- **`SubscriptionTier`** - Enum for LOCAL, FREE_BYOK, PREMIUM, ENTERPRISE tiers

Key features:
- Email validation with Pydantic (optional for local usage)
- Optional API key encryption for file storage
- Composite key indexing for provider-specific keys
- Local tier for desktop-only usage with simplified user management

### Story Models

- **`Chapter`** - Individual chapters with publication status (DRAFT, PUBLISHED, ARCHIVED)
- **`StoryMetadata`** - Story-level info: title, author, synopsis, genres, chapter counts
- **`ChapterStatus`** - Enum for chapter states

Key features:
- Chapter versioning and draft management
- Publication tracking and metadata

### Wiki Models  

- **`ChapterVersion`** - Wiki content safe through specific chapter (spoiler prevention)
- **`CurrentVersion`** - Living version with user notes and AI generation guidance
- **`ArticleConnection`** - Links between wiki articles with metadata
- **`WikiArticleType`** - Enum for character profiles, locations, concepts, etc.

Key features:
- Chapter-based spoiler prevention
- User guidance for AI content evolution
- Rich article interconnections

### Writing Models

- **`AIConversation`** - Conversation history with AI (character dev, plotting, world building)
- **`AuthorNote`** - Research notes and planning with tagging
- **`WritingPrompt`** - Reusable writing templates with variables
- **`ConversationType`** - Enum for conversation categories

Key features:
- Structured AI conversation tracking
- Searchable author notes
- Template-based writing assistance

### Workspace Models

- **`Workspace`** - Story workspace with owner, status, processing state
- **`Arc`** - Story arc definition for batch processing (start/end chapters)
- **`WorkspaceStatus`** - Enum for ACTIVE, PROCESSING, ARCHIVED, ERROR states

Key features:
- User ownership tracking
- Arc-based content processing
- Processing state management

## Repository Interface Approach

### Domain-Specific Repository Strategy

Each domain gets its own repository interface and implementations:

- **`interfaces/user.py`** - User operations including BYOK API key management
- **`interfaces/workspace.py`** - Workspace creation, arcs, processing state
- **`interfaces/story.py`** - Story chapters, drafts, publication status
- **`interfaces/wiki.py`** - Wiki articles, chapter-based versioning, connections
- **`interfaces/writing.py`** - AI conversations, author notes, writing tools

### Implementation-First Organization

Instead of organizing by repository type first (which causes circular imports), organize by backend implementation:

- **`memory/`** - All in-memory implementations for testing
- **`file/`** - All file-based implementations with encryption
- **`supabase/`** - All database implementations

This eliminates circular import issues and makes backend switching cleaner.

## User Repository Interface (Enhanced)

```python
# interfaces/user_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..models.user import User, UserAPIKey, UserCreate, UserUpdate, UserAPIKeyCreate


class IUserRepository(ABC):
    """Abstract interface for user repository with BYOK support"""

    @abstractmethod
    async def get(self, id: UUID) -> Optional[User]:
        """Retrieve a single user by their ID"""
        pass

    @abstractmethod
    async def get_multi(self, *, offset: int = 0, limit: int = 100) -> List[User]:
        """Retrieve multiple users with pagination"""
        pass

    @abstractmethod
    async def create(self, user_data: UserCreate) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def update(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update an existing user"""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address"""
        pass

    # BYOK API Key Management
    @abstractmethod
    async def get_api_key(self, user_id: UUID, provider: str) -> Optional[UserAPIKey]:
        """Get user's API key for a specific provider"""
        pass

    @abstractmethod
    async def get_all_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get all API keys for a user"""
        pass

    @abstractmethod
    async def store_api_key(self, user_id: UUID, api_key_data: UserAPIKeyCreate) -> UserAPIKey:
        """Store or update user's API key for a provider"""
        pass

    @abstractmethod
    async def delete_api_key(self, user_id: UUID, provider: str) -> bool:
        """Delete user's API key for a provider"""
        pass

    @abstractmethod
    async def validate_api_key(self, user_id: UUID, provider: str) -> bool:
        """Validate user's API key for a provider"""
        pass
```

## File-Based Storage Security

### API Key Storage Strategy

```python
# security/encryption.py
import os
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class FileEncryption:
    """File-based encryption for API keys"""
    
    def __init__(self, encryption_enabled: bool = True, master_key: Optional[str] = None):
        self.encryption_enabled = encryption_enabled
        self._fernet = None
        
        if encryption_enabled:
            self._fernet = self._initialize_encryption(master_key)
    
    def _initialize_encryption(self, master_key: Optional[str] = None) -> Fernet:
        """Initialize encryption with master key or generate one"""
        if master_key:
            # Use provided master key
            key = base64.urlsafe_b64encode(master_key.encode()[:32].ljust(32, b'0'))
        else:
            # Generate or load key from environment/file
            key = self._get_or_create_encryption_key()
        
        return Fernet(key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get encryption key from environment or create new one"""
        # Try environment variable first
        env_key = os.getenv('SHUSCRIBE_ENCRYPTION_KEY')
        if env_key:
            return base64.urlsafe_b64encode(env_key.encode()[:32].ljust(32, b'0'))
        
        # Generate new key for local development
        return Fernet.generate_key()
    
    def encrypt(self, data: str) -> str:
        """Encrypt data string"""
        if not self.encryption_enabled or not self._fernet:
            return data  # Store as plaintext if encryption disabled
        
        return self._fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data string"""
        if not self.encryption_enabled or not self._fernet:
            return encrypted_data  # Return as-is if encryption disabled
        
        try:
            return self._fernet.decrypt(encrypted_data.encode()).decode()
        except Exception:
            # If decryption fails, assume it's plaintext (backward compatibility)
            return encrypted_data


# Configuration for file-based encryption
class FileStorageConfig:
    """Configuration for file-based storage security"""
    
    def __init__(self):
        # For local development, encryption can be optional
        self.encrypt_api_keys = os.getenv('SHUSCRIBE_ENCRYPT_API_KEYS', 'true').lower() == 'true'
        
        # For shared/production file storage, encryption should be required
        self.require_encryption = os.getenv('SHUSCRIBE_REQUIRE_ENCRYPTION', 'false').lower() == 'true'
        
        # Master key for encryption (optional for local dev)
        self.master_key = os.getenv('SHUSCRIBE_MASTER_KEY')
        
        # API key storage location
        self.secure_storage_path = os.getenv('SHUSCRIBE_SECURE_PATH', './.shuscribe_secure')
```

### File-Based User Repository (Desktop-Optimized)

```python
# repositories/user/user_file.py
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from ...models.user import User, UserAPIKey, UserCreate, UserUpdate, UserAPIKeyCreate
from ...interfaces.user_repository import IUserRepository
from ...security.encryption import FileEncryption, FileStorageConfig
from src.core.exceptions import ShuScribeException


class FileUserRepository(IUserRepository):
    """Desktop-optimized user repository with single config file"""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.shuscribe_dir = workspace_path / ".shuscribe"
        self.config_file = self.shuscribe_dir / "config.json"
        
        # Encryption setup
        self.config = FileStorageConfig()
        self.encryption = FileEncryption(
            encryption_enabled=self.config.encrypt_api_keys,
            master_key=self.config.master_key
        )
        
        # Ensure directories exist
        self.shuscribe_dir.mkdir(exist_ok=True)
        
        # For local usage, we typically have one "user" per workspace
        self._current_user_id = None
        self._load_or_create_config()
    
    def _load_or_create_config(self):
        """Load or create the local configuration"""
        if self.config_file.exists():
            try:
                config_data = json.loads(self.config_file.read_text())
                self._current_user_id = UUID(config_data.get("user_id"))
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration for new workspace"""
        self._current_user_id = uuid4()
        config_data = {
            "user_id": str(self._current_user_id),
            "workspace_name": self.workspace_path.name,
            "display_name": "Local Author",
            "email": "author@example.com",
            "subscription_tier": "local",
            "api_keys": {},
            "preferences": {
                "default_provider": "openai",
                "encrypt_keys": True
            },
            "created_at": datetime.now().isoformat()
        }
        self._save_config(config_data)
    
    def _save_config(self, config_data: dict):
        """Save configuration to file"""
        self.config_file.write_text(json.dumps(config_data, indent=2))
        # Set secure file permissions
        os.chmod(self.config_file, 0o600)  # Owner read/write only
    
    def _load_config(self) -> dict:
        """Load configuration from file"""
        if not self.config_file.exists():
            self._create_default_config()
        return json.loads(self.config_file.read_text())

    async def get_current_user(self) -> User:
        """Get the current local user"""
        config_data = self._load_config()
        return User(
            id=self._current_user_id,
            email=config_data.get("email", "author@example.com"),
            display_name=config_data.get("display_name", "Local Author"),
            subscription_tier=config_data.get("subscription_tier", "local"),
            preferences=config_data.get("preferences", {}),
            created_at=datetime.fromisoformat(config_data.get("created_at", datetime.now().isoformat())),
            updated_at=None
        )

    async def get(self, id: UUID) -> Optional[User]:
        """Get user by ID (local mode returns current user if ID matches)"""
        if id == self._current_user_id:
            return await self.get_current_user()
        return None

    async def get_multi(self, *, offset: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users (local mode returns single user)"""
        return [await self.get_current_user()]

    async def update(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update user (local mode updates current user)"""
        if user_id != self._current_user_id:
            raise ShuScribeException("User not found")
        
        config_data = self._load_config()
        
        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field not in ['id', 'created_at']:  # Don't update immutable fields
                config_data[field] = value
        
        config_data['updated_at'] = datetime.now().isoformat()
        self._save_config(config_data)
        
        return await self.get_current_user()

    # BYOK API Key Management
    async def store_api_key(self, user_id: UUID, api_key_data: UserAPIKeyCreate) -> UserAPIKey:
        """Store API key in local config"""
        if user_id != self._current_user_id:
            raise ShuScribeException("User not found")
        
        config_data = self._load_config()
        
        if "api_keys" not in config_data:
            config_data["api_keys"] = {}
        
        # Encrypt and store
        encrypted_key = self.encryption.encrypt(api_key_data.api_key)
        config_data["api_keys"][api_key_data.provider] = {
            "encrypted_key": encrypted_key,
            "provider_metadata": api_key_data.provider_metadata,
            "validation_status": "pending",
            "created_at": datetime.now().isoformat()
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
            created_at=datetime.fromisoformat(key_data["created_at"]),
            updated_at=None
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
                created_at=datetime.fromisoformat(key_data["created_at"]),
                updated_at=None
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
            self._save_config(config_data)
        
        return True
```

## User Manager Integration

```python
# managers/user_manager.py
from typing import Optional, List
from uuid import UUID

from ..interfaces.user_repository import IUserRepository
from ..models.user import User, UserAPIKey, UserCreate, UserUpdate, UserAPIKeyCreate
from ..security.key_validation import APIKeyValidator
from src.core.exceptions import ShuScribeException


class UserManager:
    """High-level user management with BYOK support"""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repo = user_repository
        self.key_validator = APIKeyValidator()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user"""
        return await self.user_repo.create(user_data)
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return await self.user_repo.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.user_repo.get_by_email(email)
    
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update user"""
        return await self.user_repo.update(user_id, user_data)
    
    # BYOK Management
    async def store_api_key(self, user_id: UUID, api_key_data: UserAPIKeyCreate) -> UserAPIKey:
        """Store and validate user's API key"""
        # Validate the API key before storing
        is_valid = await self.key_validator.validate_key(api_key_data.provider, api_key_data.api_key)
        
        # Store the key
        stored_key = await self.user_repo.store_api_key(user_id, api_key_data)
        
        # Update validation status
        if is_valid:
            stored_key.validation_status = "valid"
        else:
            stored_key.validation_status = "invalid"
            
        return stored_key
    
    async def get_user_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get all API keys for user"""
        return await self.user_repo.get_all_api_keys(user_id)
    
    async def get_validated_api_key(self, user_id: UUID, provider: str) -> Optional[str]:
        """Get decrypted, validated API key for use"""
        api_key = await self.user_repo.get_api_key(user_id, provider)
        
        if not api_key or api_key.validation_status != "valid":
            return None
            
        return api_key.encrypted_api_key  # This is actually decrypted in file storage
    
    async def delete_api_key(self, user_id: UUID, provider: str) -> bool:
        """Delete user's API key"""
        return await self.user_repo.delete_api_key(user_id, provider)
```

## Service Layer Architecture

### Storage Service Design

The main **`StorageService`** class provides the high-level application interface:

- **Factory-based initialization** - Creates appropriate repositories based on environment
- **Manager coordination** - Orchestrates user, workspace, story, wiki, and writing managers
- **Unified API** - Single entry point for all storage operations

### Manager Layer

Each domain gets its own manager for business logic:

- **`UserManager`** - User operations, BYOK validation, API key management
- **`WorkspaceManager`** - Workspace lifecycle, arc processing coordination
- **`StoryManager`** - Chapter management, publication workflow
- **`WikiManager`** - Article versioning, spoiler prevention, connections
- **`WritingManager`** - AI conversations, note organization, prompt management

## API Key Security Recommendations

### File-Based Storage Security:

1. **Local Development (Default)**:
   - API keys can be stored unencrypted for convenience
   - Files stored in `.shuscribe_secure/` directory (gitignored)
   - Optional encryption via `SHUSCRIBE_ENCRYPT_API_KEYS=true`

2. **Shared/Production File Storage**:
   - **Always encrypt** API keys using `SHUSCRIBE_REQUIRE_ENCRYPTION=true`
   - Use strong master key via `SHUSCRIBE_MASTER_KEY` environment variable
   - Set restrictive file permissions (600)
   - Store encrypted files separate from main content

3. **Hybrid Approach**:
   - Environment variable controls encryption: `SHUSCRIBE_ENCRYPT_API_KEYS`
   - Graceful fallback for unencrypted keys (development)
   - Clear warnings when encryption is disabled

### Database Storage Security:

- Always encrypt API keys at rest
- Use Supabase's built-in encryption capabilities
- Row-level security for user data isolation
- API key validation before storage

This approach gives you the flexibility of unencrypted keys for local development while ensuring security for shared or production deployments.

## Desktop-Optimized Implementation Benefits

### 1. **Simplified Local Development**
- **Single Config File**: All user data and API keys stored in one secure `.shuscribe/config.json` file
- **One User Per Workspace**: Eliminates multi-user complexity for desktop usage
- **Desktop-Friendly Structure**: Intuitive file organization that makes sense for local file browsing
- **Hidden System Files**: Implementation details kept in `.shuscribe/` directory

### 2. **Preserved Architecture Benefits**
- **Same Repository Interfaces**: All abstract interfaces remain unchanged
- **Business Logic Unchanged**: Managers and services work identically across implementations
- **Easy Backend Switching**: Factory pattern enables seamless transitions between file/database storage
- **Full Feature Preservation**: Chapter versioning, BYOK, spoiler prevention all maintained

### 3. **Performance Advantages**
- **Faster Development**: Simpler file structure means faster implementation and testing
- **No Database Dependencies**: Immediate local usage without requiring database setup
- **Direct File Access**: Users can browse and understand their project structure
- **Efficient Storage**: File-based approach scales well for individual projects

### 4. **Migration Path to Web Deployment**

The desktop-optimized approach provides a clear path to full web deployment:

```python
# Factory automatically selects implementation based on environment
class RepositoryFactory:
    @staticmethod
    def create_repositories(workspace_path: Path = None, supabase_client = None):
        if workspace_path:
            # Desktop/CLI mode: File-based implementations
            return {
                'user': FileUserRepository(workspace_path),
                'workspace': FileWorkspaceRepository(workspace_path), 
                'story': FileStoryRepository(workspace_path),
                'wiki': FileWikiRepository(workspace_path),
                'writing': FileWritingRepository(workspace_path)
            }
        else:
            # Web mode: Database implementations
            return {
                'user': SupabaseUserRepository(supabase_client),
                'workspace': SupabaseWorkspaceRepository(supabase_client),
                'story': SupabaseStoryRepository(supabase_client),
                'wiki': SupabaseWikiRepository(supabase_client),
                'writing': SupabaseWritingRepository(supabase_client)
            }
```

**Migration Steps:**
1. **Phase 1**: Implement file-based repositories for local MVP
2. **Phase 2**: Add Supabase repository implementations
3. **Phase 3**: Build web UI that consumes the same managers/services
4. **Phase 4**: Enable project import/export between local and web versions

### 5. **Local Subscription Tiers**

Desktop usage introduces a simplified subscription model:
- **`local`**: Full desktop functionality with BYOK
- **`premium`**: Future enhanced desktop features
- **`free_byok`**: Web-based free tier with BYOK
- **`enterprise`**: Web-based enterprise features

This approach delivers maximum development velocity for the local MVP while preserving all options for future scaling and web deployment.
