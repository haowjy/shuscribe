from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.schemas.db.writing import (
    AuthorNote, AuthorNoteCreate, AuthorNoteUpdate,
    WritingPrompt, WritingPromptCreate, WritingPromptUpdate,
    ResearchItem, ResearchItemCreate, ResearchItemUpdate,
    CharacterProfile, CharacterProfileCreate, CharacterProfileUpdate,
    PlotOutline, PlotOutlineCreate, PlotOutlineUpdate
)


class IWritingRepository(ABC):
    """Abstract interface for writing tools repository - pure CRUD + simple queries"""

    # Author Notes CRUD
    @abstractmethod
    async def create_author_note(self, note_data: AuthorNoteCreate) -> AuthorNote:
        """Create a new author note"""
        pass

    @abstractmethod
    async def get_author_note(self, note_id: UUID) -> Optional[AuthorNote]:
        """Get a specific author note by ID"""
        pass

    @abstractmethod
    async def update_author_note(
        self, note_id: UUID, note_data: AuthorNoteUpdate
    ) -> AuthorNote:
        """Update an existing author note"""
        pass

    @abstractmethod
    async def delete_author_note(self, note_id: UUID) -> bool:
        """Delete an author note"""
        pass

    # Simple Author Note Queries
    @abstractmethod
    async def get_author_notes_by_workspace(self, workspace_id: UUID) -> List[AuthorNote]:
        """Get author notes for a workspace"""
        pass

    @abstractmethod
    async def get_author_notes_by_tags(
        self, workspace_id: UUID, tags: List[str]
    ) -> List[AuthorNote]:
        """Get notes that have any of the specified tags"""
        pass

    @abstractmethod
    async def search_author_notes(
        self, workspace_id: UUID, query: str
    ) -> List[AuthorNote]:
        """Search author notes by content"""
        pass

    # Writing Prompts CRUD
    @abstractmethod
    async def create_writing_prompt(self, prompt_data: WritingPromptCreate) -> WritingPrompt:
        """Create a new writing prompt"""
        pass

    @abstractmethod
    async def get_writing_prompt(self, prompt_id: UUID) -> Optional[WritingPrompt]:
        """Get a specific writing prompt by ID"""
        pass

    @abstractmethod
    async def update_writing_prompt(
        self, prompt_id: UUID, prompt_data: WritingPromptUpdate
    ) -> WritingPrompt:
        """Update an existing writing prompt"""
        pass

    @abstractmethod
    async def delete_writing_prompt(self, prompt_id: UUID) -> bool:
        """Delete a writing prompt"""
        pass

    # Simple Writing Prompt Queries
    @abstractmethod
    async def get_writing_prompts_by_workspace(self, workspace_id: UUID) -> List[WritingPrompt]:
        """Get writing prompts for a workspace"""
        pass

    @abstractmethod
    async def get_writing_prompts_by_category(
        self, workspace_id: UUID, category: str
    ) -> List[WritingPrompt]:
        """Get writing prompts filtered by category"""
        pass

    # Research Items CRUD
    @abstractmethod
    async def create_research_item(self, research_data: ResearchItemCreate) -> ResearchItem:
        """Create a new research item"""
        pass

    @abstractmethod
    async def get_research_item(self, research_id: UUID) -> Optional[ResearchItem]:
        """Get a specific research item by ID"""
        pass

    @abstractmethod
    async def update_research_item(
        self, research_id: UUID, research_data: ResearchItemUpdate
    ) -> ResearchItem:
        """Update an existing research item"""
        pass

    @abstractmethod
    async def delete_research_item(self, research_id: UUID) -> bool:
        """Delete a research item"""
        pass

    # Simple Research Item Queries
    @abstractmethod
    async def get_research_items_by_workspace(self, workspace_id: UUID) -> List[ResearchItem]:
        """Get research items for a workspace"""
        pass

    @abstractmethod
    async def get_research_items_by_tags(
        self, workspace_id: UUID, tags: List[str]
    ) -> List[ResearchItem]:
        """Get research items that have any of the specified tags"""
        pass

    @abstractmethod
    async def search_research_items(
        self, workspace_id: UUID, query: str
    ) -> List[ResearchItem]:
        """Search research items by content"""
        pass

    # Character Profiles CRUD
    @abstractmethod
    async def create_character_profile(
        self, character_data: CharacterProfileCreate
    ) -> CharacterProfile:
        """Create a character development profile"""
        pass

    @abstractmethod
    async def get_character_profile(self, profile_id: UUID) -> Optional[CharacterProfile]:
        """Get a character profile by ID"""
        pass

    @abstractmethod
    async def update_character_profile(
        self, profile_id: UUID, character_data: CharacterProfileUpdate
    ) -> CharacterProfile:
        """Update a character development profile"""
        pass

    @abstractmethod
    async def delete_character_profile(self, profile_id: UUID) -> bool:
        """Delete a character profile"""
        pass

    # Simple Character Profile Queries
    @abstractmethod
    async def get_character_profiles_by_workspace(
        self, workspace_id: UUID
    ) -> List[CharacterProfile]:
        """Get all character profiles for a workspace"""
        pass

    @abstractmethod
    async def search_character_profiles(
        self, workspace_id: UUID, query: str
    ) -> List[CharacterProfile]:
        """Search character profiles by name and description"""
        pass

    # Plot Outlines CRUD
    @abstractmethod
    async def create_plot_outline(self, outline_data: PlotOutlineCreate) -> PlotOutline:
        """Create a plot outline"""
        pass

    @abstractmethod
    async def get_plot_outline(self, outline_id: UUID) -> Optional[PlotOutline]:
        """Get a plot outline by ID"""
        pass

    @abstractmethod
    async def update_plot_outline(
        self, outline_id: UUID, outline_data: PlotOutlineUpdate
    ) -> PlotOutline:
        """Update a plot outline"""
        pass

    @abstractmethod
    async def delete_plot_outline(self, outline_id: UUID) -> bool:
        """Delete a plot outline"""
        pass

    # Simple Plot Outline Queries
    @abstractmethod
    async def get_plot_outlines_by_workspace(
        self, workspace_id: UUID
    ) -> List[PlotOutline]:
        """Get all plot outlines for a workspace"""
        pass