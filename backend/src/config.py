# backend/src/config.py
"""
Application configuration using Pydantic Settings
"""
import logging # Added for potential logging in init
import os
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import dotenv_values

logger = logging.getLogger(__name__) # Added logger

# --- Determine environment early to configure Pydantic Settings ---
# Read the ENVIRONMENT variable directly from the .env file or system environment
# This allows us to configure `extra` mode conditionally.
_env_values = dotenv_values(".env") # Load .env file
CURRENT_ENVIRONMENT = os.getenv("ENVIRONMENT", _env_values.get("ENVIRONMENT", "development"))
if CURRENT_ENVIRONMENT is not None:
    CURRENT_ENVIRONMENT = CURRENT_ENVIRONMENT.lower()

# Set the `extra` mode based on the environment
_extra_mode = "ignore" if CURRENT_ENVIRONMENT == "development" else "forbid"
logger.info(f"Pydantic Settings 'extra' mode set to: '{_extra_mode}' for environment: '{CURRENT_ENVIRONMENT}'")

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    
    # Database - Supabase Configuration
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_KEY: str = "your-anon-key-here"
    SUPABASE_SERVICE_KEY: Optional[str] = None  # For admin operations
    SKIP_DATABASE: bool = False # <-- Set to True to skip database connection and use in-memory repositories
    
    # Legacy SQLAlchemy URL (kept for compatibility during migration)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/shuscribe"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Self-hosted Portkey Gateway Configuration
    PORTKEY_BASE_URL: str = "http://localhost:8787/v1"  # Default for local Docker setup
    PORTKEY_API_KEY: Optional[str] = None
    PORTKEY_VIRTUAL_KEY: Optional[str] = None
    
    # Security
    ENCRYPTION_KEY: str = "change-me-32-character-key-12345678" # Must be 32 bytes for Fernet
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = _extra_mode # <-- Dynamically set based on CURRENT_ENVIRONMENT

# Global settings instance
settings = Settings()

# Add a check for encryption key length at startup for clarity
if len(settings.ENCRYPTION_KEY.encode('utf-8')) < 32:
    logger.warning("ENCRYPTION_KEY is less than 32 bytes. Fernet requires a 32-byte URL-safe base64-encoded key. This will cause encryption/decryption to fail.")