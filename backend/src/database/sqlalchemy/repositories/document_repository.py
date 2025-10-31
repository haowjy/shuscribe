# backend/src/database/sqlalchemy/repositories/document_repository.py
"""
SQLAlchemy Document repository implementation
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from src.database.interfaces import DocumentRepository
from src.database.interfaces.models import Document as DomainDocument
from src.database.connection import get_session_context
from src.database.sqlalchemy.models import Document as SQLAlchemyDocument
from src.database.utils import TagResolver

logger = logging.getLogger(__name__)


class DatabaseDocumentRepository(DocumentRepository):
    """Database-backed document repository using SQLAlchemy"""
    
    async def get_by_id(self, document_id: str) -> Optional[DomainDocument]:
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyDocument).where(SQLAlchemyDocument.id == document_id)
                .options(selectinload(SQLAlchemyDocument.tags))
            )
            sqlalchemy_document = result.scalar_one_or_none()
            
            if sqlalchemy_document:
                domain = DomainDocument.model_validate(sqlalchemy_document, from_attributes=True)
                # Ensure tag_ids reflect ORM relationship
                tag_ids = [t.id for t in getattr(sqlalchemy_document, "tags", [])] if sqlalchemy_document.tags else []
                return domain.model_copy(update={"tag_ids": tag_ids})
            return None
    
    async def get_by_project_id(self, project_id: str) -> List[DomainDocument]:
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyDocument).where(SQLAlchemyDocument.project_id == project_id)
                .options(selectinload(SQLAlchemyDocument.tags))
            )
            sqlalchemy_documents = result.scalars().all()
            
            documents: List[DomainDocument] = []
            for doc in sqlalchemy_documents:
                domain = DomainDocument.model_validate(doc, from_attributes=True)
                tag_ids = [t.id for t in getattr(doc, "tags", [])] if doc.tags else []
                documents.append(domain.model_copy(update={"tag_ids": tag_ids}))
            return documents
    
    async def create(self, document_data: Dict[str, Any]) -> DomainDocument:
        async with get_session_context() as session:
            # Create domain document first to validate data
            domain_document = DomainDocument(**{
                "id": document_data.get("id", str(uuid.uuid4())),
                "project_id": document_data["project_id"],
                "title": document_data["title"],
                "path": document_data["path"],
                "content": document_data.get("content", ""),
                "word_count": document_data.get("word_count", 0),
                "index_markdown": document_data.get("index_markdown"),
                "last_indexed_at": document_data.get("last_indexed_at"),
                "version": document_data.get("version", "1.0.0"),
                "is_locked": document_data.get("is_locked", False),
                "locked_by": document_data.get("locked_by"),
                "file_tree_id": document_data.get("file_tree_id"),
                "created_by": document_data.get("created_by"),
                "updated_by": document_data.get("updated_by"),
                # tag_ids will be set after ORM relationship is resolved
                "tag_ids": [],
            })
            
            # Convert to SQLAlchemy model (without tags first)
            sqlalchemy_document = SQLAlchemyDocument(
                id=domain_document.id,
                project_id=domain_document.project_id,
                title=domain_document.title,
                path=domain_document.path,
                content=domain_document.content or "",
                word_count=domain_document.word_count,
                index_markdown=domain_document.index_markdown,
                last_indexed_at=domain_document.last_indexed_at,
                version=domain_document.version,
                is_locked=domain_document.is_locked,
                locked_by=domain_document.locked_by,
                file_tree_id=domain_document.file_tree_id,
                created_by=domain_document.created_by,
                updated_by=domain_document.updated_by,
                created_at=domain_document.created_at,
                updated_at=domain_document.updated_at,
            )
            
            # Handle tag relationships if provided (IDs only)
            if document_data.get("tag_ids"):
                from src.database.sqlalchemy.models import Tag as SQLAlchemyTag
                tag_result = await session.execute(
                    select(SQLAlchemyTag).where(SQLAlchemyTag.id.in_(document_data["tag_ids"]))
                )
                sqlalchemy_document.tags = list(tag_result.scalars().all())
            
            # Add to session and flush to get the document saved
            session.add(sqlalchemy_document)
            await session.flush()
            
            # Re-fetch with tags eagerly loaded to avoid lazy loading issues
            result = await session.execute(
                select(SQLAlchemyDocument)
                .where(SQLAlchemyDocument.id == sqlalchemy_document.id)
                .options(selectinload(SQLAlchemyDocument.tags))
            )
            refreshed_document = result.scalar_one()
            
            # Return domain document with proper tag relationships
            domain = DomainDocument.model_validate(refreshed_document, from_attributes=True)
            tag_ids = [t.id for t in getattr(refreshed_document, "tags", [])] if refreshed_document.tags else []
            return domain.model_copy(update={"tag_ids": tag_ids})
    
    async def update(self, document_id: str, updates: Dict[str, Any]) -> Optional[DomainDocument]:
        async with get_session_context() as session:
            # Separate tag updates from column updates (IDs only)
            tag_ids_update = updates.pop("tag_ids", None)
            
            # Add updated_at timestamp
            updates["updated_at"] = datetime.now(UTC).replace(tzinfo=None)
            
            # No legacy MDX translation; format is Markdown-only

            # Update columns (excluding tags)
            if updates:
                result = await session.execute(
                    update(SQLAlchemyDocument).where(SQLAlchemyDocument.id == document_id).values(**updates)
                )
                
                if result.rowcount == 0:
                    return None
            
            # Handle tag updates separately if provided
            if tag_ids_update is not None:
                # Get the document to update its tags
                doc_result = await session.execute(
                    select(SQLAlchemyDocument)
                    .where(SQLAlchemyDocument.id == document_id)
                    .options(selectinload(SQLAlchemyDocument.tags))
                )
                document = doc_result.scalar_one_or_none()
                
                if not document:
                    return None
                
                # Load tags by IDs and update the relationship
                from src.database.sqlalchemy.models import Tag as SQLAlchemyTag
                tag_result = await session.execute(
                    select(SQLAlchemyTag).where(SQLAlchemyTag.id.in_(tag_ids_update))
                )
                document.tags = list(tag_result.scalars().all())
                await session.flush()
            
            return await self.get_by_id(document_id)
    
    async def delete(self, document_id: str) -> bool:
        async with get_session_context() as session:
            result = await session.execute(
                delete(SQLAlchemyDocument).where(SQLAlchemyDocument.id == document_id)
            )
            return result.rowcount > 0