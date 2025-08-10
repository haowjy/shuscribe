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
from src.database.sqlalchemy.mappers import DocumentMapper
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
                return DocumentMapper.to_domain(sqlalchemy_document)
            return None
    
    async def get_by_project_id(self, project_id: str) -> List[DomainDocument]:
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyDocument).where(SQLAlchemyDocument.project_id == project_id)
                .options(selectinload(SQLAlchemyDocument.tags))
            )
            sqlalchemy_documents = result.scalars().all()
            
            return [DocumentMapper.to_domain(document) for document in sqlalchemy_documents]
    
    async def create(self, document_data: Dict[str, Any]) -> DomainDocument:
        async with get_session_context() as session:
            # Create domain document first to validate data
            domain_document = DocumentMapper.from_dict({
                "id": document_data.get("id", str(uuid.uuid4())),
                "project_id": document_data["project_id"],
                "title": document_data["title"],
                "path": document_data["path"],
                "content": document_data.get("content", {"type": "doc", "content": []}),
                "word_count": document_data.get("word_count", 0),
                "version": document_data.get("version", "1.0.0"),
                "is_locked": document_data.get("is_locked", False),
                "locked_by": document_data.get("locked_by"),
                "file_tree_id": document_data.get("file_tree_id"),
                "created_by": document_data.get("created_by"),
                "updated_by": document_data.get("updated_by"),
                "tags": document_data.get("tags", []),
            })
            
            # Convert to SQLAlchemy model (without tags first)
            sqlalchemy_document = DocumentMapper.to_sqlalchemy(domain_document)
            
            # Handle tag relationships if provided
            if document_data.get("tags"):
                # Resolve tag names to SQLAlchemy Tag objects
                resolved_tags = await TagResolver.resolve_tags(
                    session,
                    document_data["tags"],
                    project_id=document_data["project_id"],
                    user_id=document_data.get("created_by")
                )
                # Assign the resolved tags to the document
                sqlalchemy_document.tags = resolved_tags
            
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
            return DocumentMapper.to_domain(refreshed_document)
    
    async def update(self, document_id: str, updates: Dict[str, Any]) -> Optional[DomainDocument]:
        async with get_session_context() as session:
            # Separate tag updates from column updates
            tag_updates = updates.pop("tags", None)
            
            # Add updated_at timestamp
            updates["updated_at"] = datetime.now(UTC).replace(tzinfo=None)
            
            # Update columns (excluding tags)
            if updates:
                result = await session.execute(
                    update(SQLAlchemyDocument).where(SQLAlchemyDocument.id == document_id).values(**updates)
                )
                
                if result.rowcount == 0:
                    return None
            
            # Handle tag updates separately if provided
            if tag_updates is not None:
                # Get the document to update its tags
                doc_result = await session.execute(
                    select(SQLAlchemyDocument)
                    .where(SQLAlchemyDocument.id == document_id)
                    .options(selectinload(SQLAlchemyDocument.tags))
                )
                document = doc_result.scalar_one_or_none()
                
                if not document:
                    return None
                
                # Resolve new tags
                resolved_tags = await TagResolver.resolve_tags(
                    session,
                    tag_updates,
                    project_id=document.project_id,
                    user_id=document.updated_by or document.created_by
                )
                
                # Update the tags relationship
                document.tags = resolved_tags
                await session.flush()
            
            return await self.get_by_id(document_id)
    
    async def delete(self, document_id: str) -> bool:
        async with get_session_context() as session:
            result = await session.execute(
                delete(SQLAlchemyDocument).where(SQLAlchemyDocument.id == document_id)
            )
            return result.rowcount > 0