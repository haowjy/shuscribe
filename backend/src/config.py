# backend/src/config.py
"""
Application configuration using Pydantic Settings
"""
import json
import logging # Added for potential logging in init
import os
from enum import Enum
from typing import List, Literal, Optional, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import dotenv_values

logger = logging.getLogger(__name__) # Added logger

class Environment(str, Enum):
    """Environment enumeration for type-safe environment configuration"""
    DEV = "dev"
    TEST = "test"
    STAGING = "staging"
    PROD = "prod"

# --- Determine environment early to configure Pydantic Settings ---
# Read the ENVIRONMENT variable directly from the .env file or system environment
# This allows us to configure `extra` mode conditionally.
_env_values = dotenv_values(".env") # Load .env file
CURRENT_ENVIRONMENT = os.getenv("ENVIRONMENT", _env_values.get("ENVIRONMENT", "dev"))
if CURRENT_ENVIRONMENT is not None:
    CURRENT_ENVIRONMENT = CURRENT_ENVIRONMENT.lower()

# Set the `extra` mode based on the environment
_extra_mode = "ignore" if CURRENT_ENVIRONMENT == "dev" else "forbid"
logger.info(f"Pydantic Settings 'extra' mode set to: '{_extra_mode}' for environment: '{CURRENT_ENVIRONMENT}'")

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    DEBUG: bool = False
    ENVIRONMENT: Environment = Environment.DEV
    SECRET_KEY: str = "change-me-in-production"
    
    # Database - Supabase Configuration
    SUPABASE_URL: str = "https://your-project.supabase.co"
    
    # New API Key System (2025+)
    SUPABASE_PUBLISHABLE_KEY: str = "your-anon-key-here"
    SUPABASE_SECRET_KEY: str = "your-service-key-here"
    
    # Legacy SQLAlchemy URL (kept for compatibility during migration)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/shuscribe"

    DATABASE_BACKEND: Literal["memory", "file", "database"] = "memory"
    
    # Table prefix for environment isolation
    TABLE_PREFIX: str = ""  # Empty for production, "test_" for development/testing
    
    # Database Seeding (Development Only)
    ENABLE_DATABASE_SEEDING: bool = False  # Enable/disable seeding on startup
    SEED_DATA_SIZE: str = "medium"        # "small", "medium", or "large"
    CLEAR_BEFORE_SEED: bool = False        # Clear existing test data before seeding
    
    # User Authorization
    ENABLE_USER_FILTERING: bool = False     # Enable user-based filtering for projects/data
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3001"]
    
    # Self-hosted Portkey Gateway Configuration
    PORTKEY_BASE_URL: str = "http://localhost:8787/v1"  # Default for local Docker setup
    PORTKEY_API_KEY: Optional[str] = None
    PORTKEY_VIRTUAL_KEY: Optional[str] = None
    
    # Security
    ENCRYPTION_KEY: str = "change-me-32-character-key-12345678" # Must be 32 bytes for Fernet
    
    # Database Connection Timeouts (in seconds)
    DATABASE_COMMAND_TIMEOUT: int = 60      # Timeout for database commands (CREATE TABLE, etc.)
    DATABASE_POOL_TIMEOUT: int = 30         # Timeout for getting connection from pool
    DATABASE_CONNECT_TIMEOUT: int = 30      # Timeout for initial connection establishment
    
    # Database Connection Pool Configuration
    DATABASE_POOL_SIZE: int = 20             # Base number of connections to maintain in pool
    DATABASE_MAX_OVERFLOW: int = 30          # Additional connections allowed beyond pool_size
                                             # Total max connections = pool_size + max_overflow = 50
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Thinking Configuration - Budget Token Percentages
    # These percentages are used to calculate budget_tokens for thinking models
    # based on the model's context window or a reasonable default
    THINKING_BUDGET_LOW_PERCENT: float = 15.0      # 15% of available tokens for low thinking
    THINKING_BUDGET_MEDIUM_PERCENT: float = 50.0   # 50% of available tokens for medium thinking  
    THINKING_BUDGET_HIGH_PERCENT: float = 100.0     # 100% of available tokens for high thinking
    THINKING_BUDGET_DEFAULT_TOKENS: int = 2048     # Default budget when context window unknown
    
    @field_validator('ENVIRONMENT', mode='before')
    @classmethod
    def parse_environment(cls, v: Union[str, Environment]) -> Environment:
        """Parse ENVIRONMENT from string to enum"""
        if isinstance(v, str):
            try:
                return Environment(v.lower())
            except ValueError:
                logger.warning(f"Invalid environment value: {v}. Using default: {Environment.DEV}")
                return Environment.DEV
        return v
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse ALLOWED_ORIGINS from JSON string or return as-is if already a list"""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                else:
                    logger.warning(f"ALLOWED_ORIGINS JSON is not a list: {parsed}")
                    return [str(parsed)]
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse ALLOWED_ORIGINS as JSON: {v}")
                return [v]
        return v
    
    @property
    def supabase_publishable_key(self) -> str:
        """Get the publishable key"""
        return self.SUPABASE_PUBLISHABLE_KEY
    
    @property
    def supabase_secret_key(self) -> str:
        """Get the secret key"""
        return self.SUPABASE_SECRET_KEY
    
    @property
    def table_prefix(self) -> str:
        """Get table prefix based on environment and configuration"""
        if self.ENVIRONMENT in [Environment.DEV, Environment.TEST, Environment.STAGING]:
            # Respect configured TABLE_PREFIX, but default to "test_" if empty
            return self.TABLE_PREFIX if self.TABLE_PREFIX else "test_"
        return ""
    
    @property
    def is_dev(self) -> bool:
        """Check if environment is development"""
        return self.ENVIRONMENT == Environment.DEV
    
    @property
    def is_test(self) -> bool:
        """Check if environment is testing"""
        return self.ENVIRONMENT == Environment.TEST
    
    @property
    def is_staging(self) -> bool:
        """Check if environment is staging"""
        return self.ENVIRONMENT == Environment.STAGING
    
    @property
    def is_prod(self) -> bool:
        """Check if environment is production"""
        return self.ENVIRONMENT == Environment.PROD
    
    @property
    def should_filter_by_user(self) -> bool:
        """Check if user filtering should be enabled based on environment and config"""
        # For production, always enable user filtering for security
        if self.is_prod:
            return True
        # For non-production environments, respect the config setting
        return self.ENABLE_USER_FILTERING
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra=_extra_mode  # <-- Dynamically set based on CURRENT_ENVIRONMENT
    )

# Global settings instance
settings = Settings()

# Add a check for encryption key length at startup for clarity
if len(settings.ENCRYPTION_KEY.encode('utf-8')) < 32:
    logger.warning("ENCRYPTION_KEY is less than 32 bytes. Fernet requires a 32-byte URL-safe base64-encoded key. This will cause encryption/decryption to fail.")