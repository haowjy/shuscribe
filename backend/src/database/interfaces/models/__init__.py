# backend/src/database/interfaces/models/__init__.py
"""
Domain models for ShuScribe - database-agnostic
"""

from .project import Project
from .document import Document
from .file_tree_item import FileTreeItem
from .tag import Tag
from .user import User, UserAPIKey

__all__ = [
    "Project",
    "Document", 
    "FileTreeItem",
    "Tag",
    "User",
    "UserAPIKey",
]