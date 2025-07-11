# backend/src/database/interfaces/document_repository.py
"""
Document repository interface
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from src.database.models import Document


class DocumentRepository(ABC):
    """Abstract document repository interface"""
    
    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        pass
    
    @abstractmethod
    async def get_by_project_id(self, project_id: str) -> List[Document]:
        """Get all documents for a project"""
        pass
    
    @abstractmethod
    async def create(self, document_data: Dict[str, Any]) -> Document:
        """Create new document"""
        pass
    
    @abstractmethod
    async def update(self, document_id: str, updates: Dict[str, Any]) -> Optional[Document]:
        """Update document"""
        pass
    
    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """Delete document"""
        pass