# backend/src/database/memory/repositories/document_repository.py
"""
Memory Document repository implementation
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC

from src.database.interfaces.document_repository import DocumentRepository
from src.database.interfaces.models import Document as DomainDocument


class MemoryDocumentRepository(DocumentRepository):
    """In-memory document repository for testing"""
    
    def __init__(self):
        self._documents: Dict[str, DomainDocument] = {}
    
    async def get_by_id(self, document_id: str) -> Optional[DomainDocument]:
        return self._documents.get(document_id)
    
    async def get_by_project_id(self, project_id: str) -> List[DomainDocument]:
        return [doc for doc in self._documents.values() if doc.project_id == project_id]
    
    async def create(self, document_data: Dict[str, Any]) -> DomainDocument:
        document_id = document_data.get("id", str(uuid.uuid4()))
        now = datetime.now(UTC).replace(tzinfo=None)
        
        document = DomainDocument(
            id=document_id,
            project_id=document_data["project_id"],
            title=document_data["title"],
            path=document_data["path"],
            created_by=document_data.get("created_by"),
            updated_by=document_data.get("updated_by"),
            content=document_data.get("content", ""),
            word_count=document_data.get("word_count", 0),
            index_markdown=document_data.get("index_markdown"),
            last_indexed_at=document_data.get("last_indexed_at"),
            version=document_data.get("version", "1.0.0"),
            is_locked=document_data.get("is_locked", False),
            locked_by=document_data.get("locked_by"),
            file_tree_id=document_data.get("file_tree_id"),
            tag_ids=document_data.get("tag_ids", []),
            created_at=now,
            updated_at=now,
        )
        self._documents[document_id] = document
        return document
    
    async def update(self, document_id: str, updates: Dict[str, Any]) -> Optional[DomainDocument]:
        document = self._documents.get(document_id)
        if not document:
            return None
        
        # Create updated document (dataclass is immutable)
        update_data = {
            "id": document.id,
            "project_id": document.project_id,
            "title": updates.get("title", document.title),
            "path": updates.get("path", document.path),
            "created_by": document.created_by,
            "updated_by": updates.get("updated_by", document.updated_by),
            "content": updates.get("content", document.content),
            "word_count": updates.get("word_count", document.word_count),
            "index_markdown": updates.get("index_markdown", document.index_markdown),
            "last_indexed_at": updates.get("last_indexed_at", document.last_indexed_at),
            "version": updates.get("version", document.version),
            "is_locked": updates.get("is_locked", document.is_locked),
            "locked_by": updates.get("locked_by", document.locked_by),
            "file_tree_id": updates.get("file_tree_id", document.file_tree_id),
            "tag_ids": updates.get("tag_ids", document.tag_ids),
            "created_at": document.created_at,
            "updated_at": datetime.now(UTC).replace(tzinfo=None),
        }
        
        updated_document = DomainDocument(**update_data)
        self._documents[document_id] = updated_document
        return updated_document
    
    async def delete(self, document_id: str) -> bool:
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False