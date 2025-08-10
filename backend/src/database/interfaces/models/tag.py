# backend/src/database/interfaces/models/tag.py
"""
Domain model for Tag - database-agnostic
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Tag:
    """
    Domain model for Tag - pure business logic representation
    """
    # Identity
    id: str
    name: str
    
    # Visual & Categorization
    icon: Optional[str] = None
    color: Optional[str] = None  # hex color code
    description: Optional[str] = None
    category: Optional[str] = None
    
    # Scope
    project_id: Optional[str] = None
    
    # Legacy global support (for future use)
    is_global: bool = False
    user_id: Optional[str] = None
    
    # Metadata
    is_system: bool = False
    is_archived: bool = False
    usage_count: int = 0
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None