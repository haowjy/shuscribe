# shuscribe/auth/models.py

from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime
from shuscribe.auth.client import supabase_auth

# OAuth2 scheme for token extraction from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class UserBase(BaseModel):
    """Base User model with common fields"""
    email: EmailStr
    display_name: Optional[str] = None
    full_name: Optional[str] = None
    
class UserCreate(UserBase):
    """Model for user creation"""
    password: str
    
class UserUpdate(BaseModel):
    """Model for user updates"""
    display_name: Optional[str] = None
    full_name: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class User(UserBase):
    """Full User model with all fields"""
    id: uuid.UUID
    created_at: datetime
    last_sign_in_at: Optional[datetime] = None
    settings: Dict[str, Any] = Field(default_factory=dict)
        
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    """Data extracted from token"""
    sub: str
    exp: int
    email: Optional[str] = None
    role: Optional[str] = None
    