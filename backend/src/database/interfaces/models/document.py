# backend/src/database/interfaces/models/document.py
"""
Domain model for Document - database-agnostic
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class Document:
    """
    Domain model for Document - pure business logic representation
    """
    # Identity
    id: str
    project_id: str
    title: str
    path: str
    
    # Content (ProseMirror JSON)
    content: Dict[str, Any] = field(default_factory=dict)
    word_count: int = 0
    version: str = "1.0.0"
    
    # Edit Control
    is_locked: bool = False
    locked_by: Optional[str] = None
    
    # File Tree Integration
    file_tree_id: Optional[str] = None
    
    # User Tracking
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Tags (as tag names/IDs for domain model simplicity)
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Ensure content dict and tags list are properly initialized"""
        if self.content is None:
            self.content = {}
        if self.tags is None:
            self.tags = []