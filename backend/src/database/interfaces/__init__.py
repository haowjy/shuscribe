# backend/src/database/interfaces/__init__.py
"""
Repository interface definitions for ShuScribe
"""

from src.database.interfaces.project_repository import ProjectRepository
from src.database.interfaces.document_repository import DocumentRepository  
from src.database.interfaces.file_tree_repository import FileTreeRepository

__all__ = [
    "ProjectRepository",
    "DocumentRepository", 
    "FileTreeRepository",
]