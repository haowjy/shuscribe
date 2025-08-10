# backend/src/database/sqlalchemy/models/project.py
"""
SQLAlchemy model for Project
"""
from datetime import datetime, UTC
from typing import Optional, Any, Dict, List, TYPE_CHECKING
import uuid

from sqlalchemy import String, Text, Integer, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.sqlalchemy.models import Base, TABLE_PREFIX, project_tags

if TYPE_CHECKING:
    from src.database.sqlalchemy.models.document import Document
    from src.database.sqlalchemy.models.file_tree_item import FileTreeItem
    from src.database.sqlalchemy.models.tag import Tag


class Project(Base):
    """SQLAlchemy Project model matching frontend ProjectDetails interface"""
    __tablename__ = f"{TABLE_PREFIX}projects"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic project info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    
    # User ownership
    owner_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # Project owner
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # Creator tracking
    updated_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # Last modifier tracking
    
    # Metrics
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    document_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # JSON fields for flexibility
    collaborators: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    settings: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))
    
    # Indexes for performance
    __table_args__ = (
        Index(f"ix_{TABLE_PREFIX}projects_owner_id", "owner_id"),
        Index(f"ix_{TABLE_PREFIX}projects_created_by", "created_by"),
        Index(f"ix_{TABLE_PREFIX}projects_updated_by", "updated_by"),
        Index(f"ix_{TABLE_PREFIX}projects_owner_updated", "owner_id", "updated_at"),
    )
    
    # Relationships
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    file_tree_items: Mapped[List["FileTreeItem"]] = relationship("FileTreeItem", back_populates="project", cascade="all, delete-orphan")
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=project_tags, back_populates="projects")