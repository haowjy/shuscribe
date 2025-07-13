# backend/src/database/models.py
"""
Minimal SQLAlchemy models for ShuScribe frontend-first approach
"""
from datetime import datetime, UTC
from typing import Optional, Any, Dict, List
import uuid

from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.config import settings


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class Project(Base):
    """Project model matching frontend ProjectDetails interface"""
    __tablename__ = f"{settings.table_prefix}projects"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic project info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    
    # Metrics
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    document_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # JSON fields for flexibility
    tag_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    collaborators: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    settings: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))
    
    # Relationships
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    file_tree_items: Mapped[List["FileTreeItem"]] = relationship("FileTreeItem", back_populates="project", cascade="all, delete-orphan")


class Document(Base):
    """Document model matching frontend Document interface"""
    __tablename__ = f"{settings.table_prefix}documents"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to project
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey(f"{settings.table_prefix}projects.id"), nullable=False)
    
    # Document info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # ProseMirror content as JSON
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Metadata
    tag_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    
    # Locking mechanism
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    locked_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # File tree reference (optional)
    file_tree_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey(f"{settings.table_prefix}file_tree_items.id"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="documents")
    file_tree_item: Mapped[Optional["FileTreeItem"]] = relationship("FileTreeItem", back_populates="document")


class FileTreeItem(Base):
    """File tree item model matching frontend FileTreeItem interface"""
    __tablename__ = f"{settings.table_prefix}file_tree_items"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to project
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey(f"{settings.table_prefix}projects.id"), nullable=False)
    
    # Tree structure
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'file' or 'folder'
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    parent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey(f"{settings.table_prefix}file_tree_items.id"), nullable=True)
    
    # Document reference (for files only)
    document_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Display info
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tag_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))
    
    # Constraints for type-document_id consistency
    __table_args__ = (
        CheckConstraint(
            "(type = 'file' AND document_id IS NOT NULL) OR (type = 'folder' AND document_id IS NULL)",
            name=f"ck_{settings.table_prefix}file_tree_items_type_document_consistency"
        ),
        CheckConstraint(
            "type IN ('file', 'folder')",
            name=f"ck_{settings.table_prefix}file_tree_items_valid_type"
        ),
        # Indexes for performance
        Index(f"ix_{settings.table_prefix}file_tree_items_project_type", "project_id", "type"),
        Index(f"ix_{settings.table_prefix}file_tree_items_parent", "parent_id"),
        Index(f"ix_{settings.table_prefix}file_tree_items_document", "document_id"),
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="file_tree_items")
    parent: Mapped[Optional["FileTreeItem"]] = relationship("FileTreeItem", remote_side=[id], back_populates="children")
    children: Mapped[List["FileTreeItem"]] = relationship("FileTreeItem", back_populates="parent")
    document: Mapped[Optional["Document"]] = relationship("Document", back_populates="file_tree_item")


class Tag(Base):
    """Tag model for multi-level tags with global/private scoping"""
    __tablename__ = f"{settings.table_prefix}tags"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Tag properties
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # hex color code
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Scope and ownership
    is_global: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # null for global tags
    
    # Metadata
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))
    
    # Constraints
    __table_args__ = (
        # Performance indexes for global/private tag lookups
        Index(f"ix_{settings.table_prefix}tags_global", "is_global"),
        Index(f"ix_{settings.table_prefix}tags_user", "user_id"),
        Index(f"ix_{settings.table_prefix}tags_global_name", "is_global", "name"),
        Index(f"ix_{settings.table_prefix}tags_user_name", "user_id", "name"),
        Index(f"ix_{settings.table_prefix}tags_category", "category"),
        Index(f"ix_{settings.table_prefix}tags_system", "is_system"),
        Index(f"ix_{settings.table_prefix}tags_archived", "is_archived"),
    )