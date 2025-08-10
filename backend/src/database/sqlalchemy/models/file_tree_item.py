# backend/src/database/sqlalchemy/models/file_tree_item.py
"""
SQLAlchemy model for FileTreeItem
"""
from datetime import datetime, UTC
from typing import Optional, List, TYPE_CHECKING
import uuid

from sqlalchemy import String, Integer, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.sqlalchemy.models import Base, TABLE_PREFIX, file_tree_item_tags

if TYPE_CHECKING:
    from src.database.sqlalchemy.models.project import Project
    from src.database.sqlalchemy.models.document import Document
    from src.database.sqlalchemy.models.tag import Tag


class FileTreeItem(Base):
    """SQLAlchemy FileTreeItem model matching frontend FileTreeItem interface"""
    __tablename__ = f"{TABLE_PREFIX}file_tree_items"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to project
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey(f"{TABLE_PREFIX}projects.id"), nullable=False)
    
    # Tree structure
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'file' or 'folder'
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    parent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey(f"{TABLE_PREFIX}file_tree_items.id"), nullable=True)
    
    # Document reference (for files only)
    document_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Display info
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))
    
    # Constraints for type-document_id consistency
    __table_args__ = (
        CheckConstraint(
            "(type = 'file' AND document_id IS NOT NULL) OR (type = 'folder' AND document_id IS NULL)",
            name=f"ck_{TABLE_PREFIX}file_tree_items_type_document_consistency"
        ),
        CheckConstraint(
            "type IN ('file', 'folder')",
            name=f"ck_{TABLE_PREFIX}file_tree_items_valid_type"
        ),
        # Indexes for performance
        Index(f"ix_{TABLE_PREFIX}file_tree_items_project_type", "project_id", "type"),
        Index(f"ix_{TABLE_PREFIX}file_tree_items_parent", "parent_id"),
        Index(f"ix_{TABLE_PREFIX}file_tree_items_document", "document_id"),
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="file_tree_items")
    parent: Mapped[Optional["FileTreeItem"]] = relationship("FileTreeItem", remote_side=[id], back_populates="children")
    children: Mapped[List["FileTreeItem"]] = relationship("FileTreeItem", back_populates="parent")
    document: Mapped[Optional["Document"]] = relationship("Document", back_populates="file_tree_item")
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=file_tree_item_tags, back_populates="file_tree_items")