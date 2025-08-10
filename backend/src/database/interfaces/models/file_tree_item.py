# backend/src/database/interfaces/models/file_tree_item.py
"""
Domain model for FileTreeItem - database-agnostic
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Literal, List


@dataclass
class FileTreeItem:
    """
    Domain model for FileTreeItem - pure business logic representation
    """
    # Identity
    id: str
    project_id: str
    name: str
    type: Literal["file", "folder"]
    path: str
    
    # Hierarchy
    parent_id: Optional[str] = None
    
    # File Properties (for type="file")
    document_id: Optional[str] = None
    word_count: Optional[int] = None
    
    # Display
    icon: Optional[str] = None
    
    # Tags (as tag names/IDs for domain model simplicity)
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Ensure tags list is properly initialized"""
        if self.tags is None:
            self.tags = []