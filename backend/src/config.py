# backend/src/config.py
"""
Application configuration using Pydantic Settings
"""
import logging # Added for potential logging in init
from typing import List, Optional

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__) # Added logger


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/shuscribe"
    SKIP_DATABASE: bool = False # <-- NEW: Set to True to skip database connection
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Self-hosted Portkey Gateway Configuration
    PORTKEY_BASE_URL: str = "http://localhost:8787/v1"  # Default for local Docker setup
    
    # Security
    ENCRYPTION_KEY: str = "change-me-32-character-key-12345678" # Must be 32 bytes for Fernet
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Add a check for encryption key length at startup for clarity
if len(settings.ENCRYPTION_KEY.encode('utf-8')) < 32:
    logger.warning("ENCRYPTION_KEY is less than 32 bytes. Fernet requires a 32-byte URL-safe base64-encoded key. This will cause encryption/decryption to fail.")