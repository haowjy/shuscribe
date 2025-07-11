# backend/src/database/interfaces/__init__.py
"""
Repository interface definitions for ShuScribe
"""

from .project_repository import ProjectRepository
from .document_repository import DocumentRepository  
from .file_tree_repository import FileTreeRepository

__all__ = [
    "ProjectRepository",
    "DocumentRepository", 
    "FileTreeRepository",
]