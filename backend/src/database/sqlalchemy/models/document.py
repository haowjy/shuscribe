# backend/src/database/sqlalchemy/models/document.py
"""
SQLAlchemy model for Document
"""
from datetime import datetime, UTC
from typing import Optional, Any, Dict, List, TYPE_CHECKING
import uuid

from sqlalchemy import String, Integer, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.sqlalchemy.models import Base, TABLE_PREFIX, document_tags

if TYPE_CHECKING:
    from src.database.sqlalchemy.models.project import Project
    from src.database.sqlalchemy.models.file_tree_item import FileTreeItem
    from src.database.sqlalchemy.models.tag import Tag


class Document(Base):
    """SQLAlchemy Document model matching frontend Document interface"""
    __tablename__ = f"{TABLE_PREFIX}documents"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to project
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey(f"{TABLE_PREFIX}projects.id"), nullable=False)
    
    # Document info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # User tracking
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # Document creator
    updated_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # Last modifier
    
    # ProseMirror content as JSON
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Metadata
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    
    # Locking mechanism
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    locked_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # File tree reference (optional)
    file_tree_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey(f"{TABLE_PREFIX}file_tree_items.id"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))
    
    # Indexes for performance
    __table_args__ = (
        Index(f"ix_{TABLE_PREFIX}documents_created_by", "created_by"),
        Index(f"ix_{TABLE_PREFIX}documents_updated_by", "updated_by"),
        Index(f"ix_{TABLE_PREFIX}documents_project_created_by", "project_id", "created_by"),
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="documents")
    file_tree_item: Mapped[Optional["FileTreeItem"]] = relationship("FileTreeItem", back_populates="document")
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=document_tags, back_populates="documents")