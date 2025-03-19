# shuscribe/core/config.py

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

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