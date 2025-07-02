"""Memory-based writing repository implementation for testing and development."""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import UTC, datetime

from src.database.interfaces.writing_repository import IWritingRepository
from src.schemas.db.writing import (
    AuthorNote, AuthorNoteCreate, AuthorNoteUpdate,
    WritingPrompt, WritingPromptCreate, WritingPromptUpdate,
    ResearchItem, ResearchItemCreate, ResearchItemUpdate,
    CharacterProfile, CharacterProfileCreate, CharacterProfileUpdate,
    PlotOutline, PlotOutlineCreate, PlotOutlineUpdate
)


class MemoryWritingRepository(IWritingRepository):
    """In-memory implementation of writing repository for testing."""
    
    def __init__(self):
        self._author_notes: Dict[UUID, AuthorNote] = {}
        self._writing_prompts: Dict[UUID, WritingPrompt] = {}
        self._research_items: Dict[UUID, ResearchItem] = {}
        self._character_profiles: Dict[UUID, CharacterProfile] = {}
        self._plot_outlines: Dict[UUID, PlotOutline] = {}
    
    # Author Notes CRUD
    async def create_author_note(self, note_data: AuthorNoteCreate) -> AuthorNote:
        """Create a new author note"""
        note_id = uuid4()
        now = datetime.now(UTC)
        
        note = AuthorNote(
            id=note_id,
            workspace_id=note_data.workspace_id,
            title=note_data.title,
            content=note_data.content,
            note_type=note_data.note_type,
            tags=note_data.tags,
            metadata=note_data.metadata,
            is_private=note_data.is_private,
            created_at=now,
            updated_at=now
        )
        
        self._author_notes[note_id] = note
        return note
    
    async def get_author_note(self, note_id: UUID) -> Optional[AuthorNote]:
        """Get a specific author note by ID"""
        return self._author_notes.get(note_id)
    
    async def update_author_note(
        self, note_id: UUID, note_data: AuthorNoteUpdate
    ) -> AuthorNote:
        """Update an existing author note"""
        note = self._author_notes.get(note_id)
        if not note:
            raise ValueError(f"Author note {note_id} not found")
        
        update_dict = note_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        updated_note = note.model_copy(update=update_dict)
        self._author_notes[note_id] = updated_note
        return updated_note
    
    async def delete_author_note(self, note_id: UUID) -> bool:
        """Delete an author note"""
        if note_id in self._author_notes:
            del self._author_notes[note_id]
            return True
        return False
    
    # Simple Author Note Queries
    async def get_author_notes_by_workspace(self, workspace_id: UUID) -> List[AuthorNote]:
        """Get author notes for a workspace"""
        notes = []
        for note in self._author_notes.values():
            if note.workspace_id == workspace_id:
                notes.append(note)
        
        # Sort by creation date
        notes.sort(key=lambda n: n.created_at, reverse=True)
        return notes
    
    async def get_author_notes_by_tags(
        self, workspace_id: UUID, tags: List[str]
    ) -> List[AuthorNote]:
        """Get notes that have any of the specified tags"""
        matching_notes = []
        tag_set = set(tag.lower() for tag in tags)
        
        for note in self._author_notes.values():
            if note.workspace_id == workspace_id:
                note_tags = set(tag.lower() for tag in note.tags)
                if tag_set.intersection(note_tags):
                    matching_notes.append(note)
        
        matching_notes.sort(key=lambda n: n.created_at, reverse=True)
        return matching_notes
    
    async def search_author_notes(
        self, workspace_id: UUID, query: str
    ) -> List[AuthorNote]:
        """Search author notes by content"""
        query_lower = query.lower()
        matching_notes = []
        
        for note in self._author_notes.values():
            if note.workspace_id == workspace_id:
                if (query_lower in note.title.lower() or 
                    query_lower in note.content.lower()):
                    matching_notes.append(note)
        
        matching_notes.sort(key=lambda n: n.created_at, reverse=True)
        return matching_notes
    
    # Writing Prompts CRUD
    async def create_writing_prompt(self, prompt_data: WritingPromptCreate) -> WritingPrompt:
        """Create a new writing prompt"""
        prompt_id = uuid4()
        now = datetime.now(UTC)
        
        prompt = WritingPrompt(
            id=prompt_id,
            workspace_id=prompt_data.workspace_id,
            title=prompt_data.title,
            prompt_text=prompt_data.prompt_text,
            category=prompt_data.category,
            tags=prompt_data.tags,
            created_at=now,
            updated_at=now
        )
        
        self._writing_prompts[prompt_id] = prompt
        return prompt
    
    async def get_writing_prompt(self, prompt_id: UUID) -> Optional[WritingPrompt]:
        """Get a specific writing prompt by ID"""
        return self._writing_prompts.get(prompt_id)
    
    async def update_writing_prompt(
        self, prompt_id: UUID, prompt_data: WritingPromptUpdate
    ) -> WritingPrompt:
        """Update an existing writing prompt"""
        prompt = self._writing_prompts.get(prompt_id)
        if not prompt:
            raise ValueError(f"Writing prompt {prompt_id} not found")
        
        update_dict = prompt_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        updated_prompt = prompt.model_copy(update=update_dict)
        self._writing_prompts[prompt_id] = updated_prompt
        return updated_prompt
    
    async def delete_writing_prompt(self, prompt_id: UUID) -> bool:
        """Delete a writing prompt"""
        if prompt_id in self._writing_prompts:
            del self._writing_prompts[prompt_id]
            return True
        return False
    
    # Simple Writing Prompt Queries
    async def get_writing_prompts_by_workspace(self, workspace_id: UUID) -> List[WritingPrompt]:
        """Get writing prompts for a workspace"""
        prompts = []
        for prompt in self._writing_prompts.values():
            if prompt.workspace_id == workspace_id:
                prompts.append(prompt)
        
        # Sort by creation date
        prompts.sort(key=lambda p: p.created_at, reverse=True)
        return prompts
    
    async def get_writing_prompts_by_category(
        self, workspace_id: UUID, category: str
    ) -> List[WritingPrompt]:
        """Get writing prompts filtered by category"""
        prompts = []
        for prompt in self._writing_prompts.values():
            if prompt.workspace_id == workspace_id and prompt.category == category:
                prompts.append(prompt)
        
        prompts.sort(key=lambda p: p.created_at, reverse=True)
        return prompts
    
    # Research Items CRUD
    async def create_research_item(self, research_data: ResearchItemCreate) -> ResearchItem:
        """Create a new research item"""
        research_id = uuid4()
        now = datetime.now(UTC)
        
        research = ResearchItem(
            id=research_id,
            workspace_id=research_data.workspace_id,
            title=research_data.title,
            content=research_data.content,
            source_url=research_data.source_url,
            tags=research_data.tags,
            created_at=now,
            updated_at=now
        )
        
        self._research_items[research_id] = research
        return research
    
    async def get_research_item(self, research_id: UUID) -> Optional[ResearchItem]:
        """Get a specific research item by ID"""
        return self._research_items.get(research_id)
    
    async def update_research_item(
        self, research_id: UUID, research_data: ResearchItemUpdate
    ) -> ResearchItem:
        """Update an existing research item"""
        research = self._research_items.get(research_id)
        if not research:
            raise ValueError(f"Research item {research_id} not found")
        
        update_dict = research_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        updated_research = research.model_copy(update=update_dict)
        self._research_items[research_id] = updated_research
        return updated_research
    
    async def delete_research_item(self, research_id: UUID) -> bool:
        """Delete a research item"""
        if research_id in self._research_items:
            del self._research_items[research_id]
            return True
        return False
    
    # Simple Research Item Queries
    async def get_research_items_by_workspace(self, workspace_id: UUID) -> List[ResearchItem]:
        """Get research items for a workspace"""
        items = []
        for item in self._research_items.values():
            if item.workspace_id == workspace_id:
                items.append(item)
        
        # Sort by creation date
        items.sort(key=lambda i: i.created_at, reverse=True)
        return items
    
    async def get_research_items_by_tags(
        self, workspace_id: UUID, tags: List[str]
    ) -> List[ResearchItem]:
        """Get research items that have any of the specified tags"""
        matching_items = []
        tag_set = set(tag.lower() for tag in tags)
        
        for item in self._research_items.values():
            if item.workspace_id == workspace_id:
                item_tags = set(tag.lower() for tag in item.tags)
                if tag_set.intersection(item_tags):
                    matching_items.append(item)
        
        matching_items.sort(key=lambda i: i.created_at, reverse=True)
        return matching_items
    
    async def search_research_items(
        self, workspace_id: UUID, query: str
    ) -> List[ResearchItem]:
        """Search research items by content"""
        query_lower = query.lower()
        matching_items = []
        
        for item in self._research_items.values():
            if item.workspace_id == workspace_id:
                if (query_lower in item.title.lower() or 
                    query_lower in item.content.lower()):
                    matching_items.append(item)
        
        matching_items.sort(key=lambda i: i.created_at, reverse=True)
        return matching_items
    
    # Character Profiles CRUD
    async def create_character_profile(
        self, character_data: CharacterProfileCreate
    ) -> CharacterProfile:
        """Create a character development profile"""
        profile_id = uuid4()
        now = datetime.now(UTC)
        
        profile = CharacterProfile(
            id=profile_id,
            workspace_id=character_data.workspace_id,
            name=character_data.name,
            description=character_data.description,
            physical_description=character_data.physical_description,
            personality=character_data.personality,
            backstory=character_data.backstory,
            relationships=character_data.relationships,
            notes=character_data.notes,
            created_at=now,
            updated_at=now
        )
        
        self._character_profiles[profile_id] = profile
        return profile
    
    async def get_character_profile(self, profile_id: UUID) -> Optional[CharacterProfile]:
        """Get a character profile by ID"""
        return self._character_profiles.get(profile_id)
    
    async def update_character_profile(
        self, profile_id: UUID, character_data: CharacterProfileUpdate
    ) -> CharacterProfile:
        """Update a character development profile"""
        profile = self._character_profiles.get(profile_id)
        if not profile:
            raise ValueError(f"Character profile {profile_id} not found")
        
        update_dict = character_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        updated_profile = profile.model_copy(update=update_dict)
        self._character_profiles[profile_id] = updated_profile
        return updated_profile
    
    async def delete_character_profile(self, profile_id: UUID) -> bool:
        """Delete a character profile"""
        if profile_id in self._character_profiles:
            del self._character_profiles[profile_id]
            return True
        return False
    
    # Simple Character Profile Queries
    async def get_character_profiles_by_workspace(
        self, workspace_id: UUID
    ) -> List[CharacterProfile]:
        """Get all character profiles for a workspace"""
        profiles = []
        for profile in self._character_profiles.values():
            if profile.workspace_id == workspace_id:
                profiles.append(profile)
        
        # Sort by name
        profiles.sort(key=lambda p: p.name.lower())
        return profiles
    
    async def search_character_profiles(
        self, workspace_id: UUID, query: str
    ) -> List[CharacterProfile]:
        """Search character profiles by name and description"""
        query_lower = query.lower()
        matching_profiles = []
        
        for profile in self._character_profiles.values():
            if profile.workspace_id == workspace_id:
                if (query_lower in profile.name.lower() or 
                    query_lower in profile.description.lower()):
                    matching_profiles.append(profile)
        
        matching_profiles.sort(key=lambda p: p.name.lower())
        return matching_profiles
    
    # Plot Outlines CRUD
    async def create_plot_outline(self, outline_data: PlotOutlineCreate) -> PlotOutline:
        """Create a plot outline"""
        outline_id = uuid4()
        now = datetime.now(UTC)
        
        outline = PlotOutline(
            id=outline_id,
            workspace_id=outline_data.workspace_id,
            title=outline_data.title,
            description=outline_data.description,
            structure=outline_data.structure,
            notes=outline_data.notes,
            created_at=now,
            updated_at=now
        )
        
        self._plot_outlines[outline_id] = outline
        return outline
    
    async def get_plot_outline(self, outline_id: UUID) -> Optional[PlotOutline]:
        """Get a plot outline by ID"""
        return self._plot_outlines.get(outline_id)
    
    async def update_plot_outline(
        self, outline_id: UUID, outline_data: PlotOutlineUpdate
    ) -> PlotOutline:
        """Update a plot outline"""
        outline = self._plot_outlines.get(outline_id)
        if not outline:
            raise ValueError(f"Plot outline {outline_id} not found")
        
        update_dict = outline_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.now(UTC)
        
        updated_outline = outline.model_copy(update=update_dict)
        self._plot_outlines[outline_id] = updated_outline
        return updated_outline
    
    async def delete_plot_outline(self, outline_id: UUID) -> bool:
        """Delete a plot outline"""
        if outline_id in self._plot_outlines:
            del self._plot_outlines[outline_id]
            return True
        return False
    
    # Simple Plot Outline Queries
    async def get_plot_outlines_by_workspace(
        self, workspace_id: UUID
    ) -> List[PlotOutline]:
        """Get all plot outlines for a workspace"""
        outlines = []
        for outline in self._plot_outlines.values():
            if outline.workspace_id == workspace_id:
                outlines.append(outline)
        
        # Sort by creation date
        outlines.sort(key=lambda o: o.created_at, reverse=True)
        return outlines