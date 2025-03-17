# shuscribe/config/settings.py

from typing import List
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # CORS settings
    CORS_ORIGINS: List[str] = []
    
    # Supabase settings
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str
    
    # Auth settings
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# # Create a global settings instance
settings = Settings(
    SUPABASE_URL=os.getenv("SUPABASE_URL", ""),
    SUPABASE_KEY=os.getenv("SUPABASE_KEY", ""),
    SUPABASE_JWT_SECRET=os.getenv("SUPABASE_JWT_SECRET", ""),
    CORS_ORIGINS=os.getenv("CORS_ORIGINS", "").split(",")
)