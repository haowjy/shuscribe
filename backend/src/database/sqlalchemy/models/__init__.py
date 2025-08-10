# backend/src/database/sqlalchemy/models/__init__.py
"""
SQLAlchemy models for ShuScribe - database-specific implementations
"""

from sqlalchemy import Table, Column, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

# Get table prefix once at module level
TABLE_PREFIX = settings.table_prefix


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass


# Association tables for many-to-many relationships
project_tags = Table(
    f"{TABLE_PREFIX}project_tags",
    Base.metadata,
    Column("project_id", String(36), ForeignKey(f"{TABLE_PREFIX}projects.id"), primary_key=True),
    Column("tag_id", String(36), ForeignKey(f"{TABLE_PREFIX}tags.id"), primary_key=True)
)

document_tags = Table(
    f"{TABLE_PREFIX}document_tags",
    Base.metadata,
    Column("document_id", String(36), ForeignKey(f"{TABLE_PREFIX}documents.id"), primary_key=True),
    Column("tag_id", String(36), ForeignKey(f"{TABLE_PREFIX}tags.id"), primary_key=True)
)

file_tree_item_tags = Table(
    f"{TABLE_PREFIX}file_tree_item_tags",
    Base.metadata,
    Column("file_tree_item_id", String(36), ForeignKey(f"{TABLE_PREFIX}file_tree_items.id"), primary_key=True),
    Column("tag_id", String(36), ForeignKey(f"{TABLE_PREFIX}tags.id"), primary_key=True)
)


# Import all models to make them available
from .project import Project
from .document import Document
from .file_tree_item import FileTreeItem
from .tag import Tag
from .user import User, UserAPIKey

__all__ = [
    "Base",
    "TABLE_PREFIX",
    "project_tags",
    "document_tags", 
    "file_tree_item_tags",
    "Project",
    "Document",
    "FileTreeItem", 
    "Tag",
    "User",
    "UserAPIKey",
]