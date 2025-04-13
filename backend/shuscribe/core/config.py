# shuscribe/core/config.py

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import logging
import sys

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # CORS settings - initialize with empty list if not provided
    CORS_ORIGINS: List[str] = []
    
    # Supabase settings (with defaults to silence linter warnings)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""          # Anon key (public)
    SUPABASE_SERVICE_KEY: str = ""  # Service role key (private)
    
    # Auth settings
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache
def get_settings():
    return Settings()


def setup_logger(name, level=logging.INFO, format='%(levelname)s - %(message)s', stream=sys.stdout):
    """Set up a logger with just the warning level as a prefix."""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    
    # Create formatter with just level name as prefix
    format = logging.Formatter(format)
    handler.setFormatter(format)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger
