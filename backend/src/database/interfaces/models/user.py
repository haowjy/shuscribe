# backend/src/database/interfaces/models/user.py
"""
Domain models for User and UserAPIKey - database-agnostic
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class User:
    """
    Domain model for User - pure business logic representation
    Note: User management is primarily handled by Supabase on frontend,
    this is mainly for backend user context and API key storage
    """
    # Identity
    id: str
    email: str
    
    # Profile
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Ensure metadata dict is properly initialized"""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class UserAPIKey:
    """
    Domain model for UserAPIKey - pure business logic representation
    """
    # Identity
    user_id: str
    provider: str  # PROVIDER_ID from constants
    encrypted_api_key: str
    
    # Validation
    validation_status: str = "unknown"
    last_validated_at: Optional[datetime] = None
    
    # Provider metadata
    provider_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Ensure provider_metadata dict is properly initialized"""
        if self.provider_metadata is None:
            self.provider_metadata = {}