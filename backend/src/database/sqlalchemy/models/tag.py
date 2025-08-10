# backend/src/database/sqlalchemy/models/tag.py
"""
SQLAlchemy model for Tag
"""
from datetime import datetime, UTC
from typing import Optional, List, TYPE_CHECKING
import uuid

from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.sqlalchemy.models import Base, TABLE_PREFIX, project_tags, document_tags, file_tree_item_tags

if TYPE_CHECKING:
    from src.database.sqlalchemy.models.project import Project
    from src.database.sqlalchemy.models.document import Document
    from src.database.sqlalchemy.models.file_tree_item import FileTreeItem


class Tag(Base):
    """SQLAlchemy Tag model for multi-level tags with global/private scoping"""
    __tablename__ = f"{TABLE_PREFIX}tags"
    
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
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey(f"{TABLE_PREFIX}projects.id"), nullable=True)  # null for global tags
    
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
        Index(f"ix_{TABLE_PREFIX}tags_global", "is_global"),
        Index(f"ix_{TABLE_PREFIX}tags_user", "user_id"),
        Index(f"ix_{TABLE_PREFIX}tags_global_name", "is_global", "name"),
        Index(f"ix_{TABLE_PREFIX}tags_user_name", "user_id", "name"),
        Index(f"ix_{TABLE_PREFIX}tags_category", "category"),
        Index(f"ix_{TABLE_PREFIX}tags_system", "is_system"),
        Index(f"ix_{TABLE_PREFIX}tags_archived", "is_archived"),
        Index(f"ix_{TABLE_PREFIX}tags_project", "project_id"),
    )
    
    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project")
    projects: Mapped[List["Project"]] = relationship("Project", secondary=project_tags, back_populates="tags")
    documents: Mapped[List["Document"]] = relationship("Document", secondary=document_tags, back_populates="tags")
    file_tree_items: Mapped[List["FileTreeItem"]] = relationship("FileTreeItem", secondary=file_tree_item_tags, back_populates="tags")