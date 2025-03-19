# shuscribe/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

class User(BaseModel):
    """User model"""
    id: uuid.UUID
    email: EmailStr
    created_at: datetime
    last_sign_in_at: Optional[datetime] = None
    display_name: Optional[str] = None
    full_name: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    display_name: Optional[str] = None
    full_name: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None