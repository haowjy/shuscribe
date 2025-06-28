"""
Abstract Base Class for Writing Repositories (STUB)
For future author tools: drafts, worldbuilding documents, character sheets, etc.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID


class AbstractWritingRepository(ABC):
    """Abstract interface for writing repository operations - STUB FOR FUTURE IMPLEMENTATION"""

    @abstractmethod
    async def placeholder_method(self) -> bool:
        """Placeholder method for future writing functionality"""
        ... 