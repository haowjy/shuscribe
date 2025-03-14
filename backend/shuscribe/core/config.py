from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ShuScribe"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str
    REDIS_URL: str
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]  # For NextJS frontend
    OPENAI_API_KEY: str
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()