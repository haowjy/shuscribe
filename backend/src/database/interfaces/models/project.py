# backend/src/database/interfaces/models/project.py
"""
Domain model for Project - database-agnostic
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class Project:
    """
    Domain model for Project - pure business logic representation
    """
    # Identity
    id: str
    title: str
    description: str = ""
    
    # Ownership & Collaboration
    owner_id: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    collaborators: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metrics (auto-calculated)
    word_count: int = 0
    document_count: int = 0
    
    # Configuration
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # Tags (as tag names/IDs for domain model simplicity)
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Ensure lists and dicts are properly initialized"""
        if self.collaborators is None:
            self.collaborators = []
        if self.settings is None:
            self.settings = {}
        if self.tags is None:
            self.tags = []