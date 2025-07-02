"""
Writing Service - Business logic for author tools, notes, and research management.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from src.database.interfaces.writing_repository import IWritingRepository
from src.database.interfaces.workspace_repository import IWorkspaceRepository
from src.schemas.db.writing import (
    AuthorNote, AuthorNoteCreate, AuthorNoteUpdate,
    WritingPrompt, WritingPromptCreate, WritingPromptUpdate,
    ResearchItem, ResearchItemCreate, ResearchItemUpdate,
    CharacterProfile, CharacterProfileCreate, CharacterProfileUpdate,
    PlotOutline, PlotOutlineCreate, PlotOutlineUpdate
)
from src.schemas.responses.writing import SearchAllResult, TaggedContentResult


class WritingService:
    """Service layer for writing tools and author resources."""
    
    def __init__(
        self, 
        writing_repository: IWritingRepository,
        workspace_repository: IWorkspaceRepository
    ):
        self.writing_repository = writing_repository
        self.workspace_repository = workspace_repository
    
    # Author Notes Management
    async def create_author_note(self, note_data: AuthorNoteCreate) -> AuthorNote:
        """Create a new author note with validation."""
        # Verify workspace exists
        workspace = await self.workspace_repository.get_workspace(note_data.workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {note_data.workspace_id} not found")
        
        return await self.writing_repository.create_author_note(note_data)
    
    async def get_author_note(self, note_id: UUID) -> Optional[AuthorNote]:
        """Get author note by ID."""
        return await self.writing_repository.get_author_note(note_id)
    
    async def update_author_note(self, note_id: UUID, note_data: AuthorNoteUpdate) -> AuthorNote:
        """Update author note."""
        # Verify note exists
        existing_note = await self.writing_repository.get_author_note(note_id)
        if not existing_note:
            raise ValueError(f"Author note {note_id} not found")
        
        return await self.writing_repository.update_author_note(note_id, note_data)
    
    async def delete_author_note(self, note_id: UUID) -> bool:
        """Delete author note."""
        return await self.writing_repository.delete_author_note(note_id)
    
    async def get_author_notes_by_workspace(self, workspace_id: UUID) -> List[AuthorNote]:
        """Get all notes for a workspace."""
        return await self.writing_repository.get_author_notes_by_workspace(workspace_id)
    
    async def search_author_notes(self, workspace_id: UUID, query: str) -> List[AuthorNote]:
        """Search notes by title and content."""
        return await self.writing_repository.search_author_notes(workspace_id, query)
    
    async def get_author_notes_by_tags(self, workspace_id: UUID, tags: List[str]) -> List[AuthorNote]:
        """Get author notes filtered by tags."""
        return await self.writing_repository.get_author_notes_by_tags(workspace_id, tags)
    
    # Writing Prompts Management
    async def create_writing_prompt(self, prompt_data: WritingPromptCreate) -> WritingPrompt:
        """Create a new writing prompt."""
        # Verify workspace exists
        workspace = await self.workspace_repository.get_workspace(prompt_data.workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {prompt_data.workspace_id} not found")
        
        return await self.writing_repository.create_writing_prompt(prompt_data)
    
    async def get_writing_prompt(self, prompt_id: UUID) -> Optional[WritingPrompt]:
        """Get writing prompt by ID."""
        return await self.writing_repository.get_writing_prompt(prompt_id)
    
    async def update_writing_prompt(self, prompt_id: UUID, prompt_data: WritingPromptUpdate) -> WritingPrompt:
        """Update writing prompt."""
        # Verify prompt exists
        existing_prompt = await self.writing_repository.get_writing_prompt(prompt_id)
        if not existing_prompt:
            raise ValueError(f"Writing prompt {prompt_id} not found")
        
        return await self.writing_repository.update_writing_prompt(prompt_id, prompt_data)
    
    async def delete_prompt(self, prompt_id: UUID) -> bool:
        """Delete writing prompt."""
        return await self.writing_repository.delete_writing_prompt(prompt_id)
    
    async def get_writing_prompts_by_workspace(self, workspace_id: UUID) -> List[WritingPrompt]:
        """Get all prompts for a workspace."""
        return await self.writing_repository.get_writing_prompts_by_workspace(workspace_id)
    
    async def get_writing_prompts_by_category(self, workspace_id: UUID, category: str) -> List[WritingPrompt]:
        """Get prompts filtered by category."""
        return await self.writing_repository.get_writing_prompts_by_category(workspace_id, category)
    
    async def get_prompts_by_category(self, workspace_id: UUID, category: str) -> List[WritingPrompt]:
        """Get prompts filtered by category."""
        return await self.writing_repository.get_writing_prompts_by_category(workspace_id, category)
    
    # Research Items Management
    async def create_research_item(self, research_data: ResearchItemCreate) -> ResearchItem:
        """Create a new research item."""
        # Verify workspace exists
        workspace = await self.workspace_repository.get_workspace(research_data.workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {research_data.workspace_id} not found")
        
        return await self.writing_repository.create_research_item(research_data)
    
    async def get_research_item(self, research_id: UUID) -> Optional[ResearchItem]:
        """Get research item by ID."""
        return await self.writing_repository.get_research_item(research_id)
    
    async def update_research_item(
        self, research_id: UUID, research_data: ResearchItemUpdate
    ) -> ResearchItem:
        """Update research item."""
        # Verify research item exists
        existing_research = await self.writing_repository.get_research_item(research_id)
        if not existing_research:
            raise ValueError(f"Research item {research_id} not found")
        
        return await self.writing_repository.update_research_item(research_id, research_data)
    
    async def delete_research_item(self, research_id: UUID) -> bool:
        """Delete research item."""
        return await self.writing_repository.delete_research_item(research_id)
    
    async def get_research_by_workspace(self, workspace_id: UUID) -> List[ResearchItem]:
        """Get all research items for a workspace."""
        return await self.writing_repository.get_research_items_by_workspace(workspace_id)
    
    async def search_research(self, workspace_id: UUID, query: str) -> List[ResearchItem]:
        """Search research items by title and content."""
        return await self.writing_repository.search_research_items(workspace_id, query)
    
    async def get_research_by_tags(self, workspace_id: UUID, tags: List[str]) -> List[ResearchItem]:
        """Get research items filtered by tags."""
        return await self.writing_repository.get_research_items_by_tags(workspace_id, tags)
    
    # Character Profiles Management
    async def create_character_profile(self, profile_data: CharacterProfileCreate) -> CharacterProfile:
        """Create a new character profile."""
        # Verify workspace exists
        workspace = await self.workspace_repository.get_workspace(profile_data.workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {profile_data.workspace_id} not found")
        
        # Check for duplicate character names
        existing_profiles = await self.writing_repository.get_character_profiles_by_workspace(
            profile_data.workspace_id
        )
        if any(p.name.lower() == profile_data.name.lower() for p in existing_profiles):
            raise ValueError(f"Character '{profile_data.name}' already exists in workspace")
        
        return await self.writing_repository.create_character_profile(profile_data)
    
    async def get_character_profile(self, profile_id: UUID) -> Optional[CharacterProfile]:
        """Get character profile by ID."""
        return await self.writing_repository.get_character_profile(profile_id)
    
    async def update_character_profile(
        self, profile_id: UUID, profile_data: CharacterProfileUpdate
    ) -> CharacterProfile:
        """Update character profile."""
        # Verify profile exists
        existing_profile = await self.writing_repository.get_character_profile(profile_id)
        if not existing_profile:
            raise ValueError(f"Character profile {profile_id} not found")
        
        # Check for name conflicts if name is being changed
        if profile_data.name and profile_data.name != existing_profile.name:
            workspace_profiles = await self.writing_repository.get_character_profiles_by_workspace(
                existing_profile.workspace_id
            )
            if any(p.name.lower() == profile_data.name.lower() and p.id != profile_id 
                   for p in workspace_profiles):
                raise ValueError(f"Character '{profile_data.name}' already exists in workspace")
        
        return await self.writing_repository.update_character_profile(profile_id, profile_data)
    
    async def delete_character_profile(self, profile_id: UUID) -> bool:
        """Delete character profile."""
        return await self.writing_repository.delete_character_profile(profile_id)
    
    async def get_character_profiles_by_workspace(self, workspace_id: UUID) -> List[CharacterProfile]:
        """Get all character profiles for a workspace."""
        return await self.writing_repository.get_character_profiles_by_workspace(workspace_id)
    
    async def search_character_profiles(self, workspace_id: UUID, query: str) -> List[CharacterProfile]:
        """Search character profiles by name and description."""
        return await self.writing_repository.search_character_profiles(workspace_id, query)
    
    # Plot Outlines Management
    async def create_plot_outline(self, outline_data: PlotOutlineCreate) -> PlotOutline:
        """Create a new plot outline."""
        # Verify workspace exists
        workspace = await self.workspace_repository.get_workspace(outline_data.workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {outline_data.workspace_id} not found")
        
        return await self.writing_repository.create_plot_outline(outline_data)
    
    async def get_plot_outline(self, outline_id: UUID) -> Optional[PlotOutline]:
        """Get plot outline by ID."""
        return await self.writing_repository.get_plot_outline(outline_id)
    
    async def update_plot_outline(
        self, outline_id: UUID, outline_data: PlotOutlineUpdate
    ) -> PlotOutline:
        """Update plot outline."""
        # Verify outline exists
        existing_outline = await self.writing_repository.get_plot_outline(outline_id)
        if not existing_outline:
            raise ValueError(f"Plot outline {outline_id} not found")
        
        return await self.writing_repository.update_plot_outline(outline_id, outline_data)
    
    async def delete_plot_outline(self, outline_id: UUID) -> bool:
        """Delete plot outline."""
        return await self.writing_repository.delete_plot_outline(outline_id)
    
    async def get_plot_outlines_by_workspace(self, workspace_id: UUID) -> List[PlotOutline]:
        """Get all plot outlines for a workspace."""
        return await self.writing_repository.get_plot_outlines_by_workspace(workspace_id)
    
    # Cross-Content Search and Analytics
    async def search_all_content(self, workspace_id: UUID, query: str) -> SearchAllResult:
        """Search across all writing content types."""
        notes = await self.writing_repository.search_author_notes(workspace_id, query)
        research = await self.writing_repository.search_research_items(workspace_id, query)
        characters = await self.writing_repository.search_character_profiles(workspace_id, query)
        
        return SearchAllResult(
            notes=notes,
            research=research,
            characters=characters,
        )
    
    async def get_writing_statistics(self, workspace_id: UUID) -> Dict[str, Any]:
        """Get comprehensive writing statistics for a workspace."""
        notes = await self.writing_repository.get_author_notes_by_workspace(workspace_id)
        prompts = await self.writing_repository.get_writing_prompts_by_workspace(workspace_id)
        research = await self.writing_repository.get_research_items_by_workspace(workspace_id)
        characters = await self.writing_repository.get_character_profiles_by_workspace(workspace_id)
        outlines = await self.writing_repository.get_plot_outlines_by_workspace(workspace_id)
        
        # Calculate content lengths
        total_note_length = sum(len(n.content) for n in notes)
        total_research_length = sum(len(r.content) for r in research)
        
        # Collect all tags
        all_tags = set()
        for item in notes + research:
            all_tags.update(item.tags)
        
        return {
            "workspace_id": workspace_id,
            "total_notes": len(notes),
            "total_prompts": len(prompts),
            "total_research_items": len(research),
            "total_characters": len(characters),
            "total_plot_outlines": len(outlines),
            "total_content_length": total_note_length + total_research_length,
            "unique_tags": list(all_tags),
            "tag_count": len(all_tags)
        }
    
    async def get_content_by_tags(self, workspace_id: UUID, tags: List[str]) -> TaggedContentResult:
        """Get all content items that match any of the given tags."""
        notes = await self.writing_repository.get_author_notes_by_tags(workspace_id, tags)
        research = await self.writing_repository.get_research_items_by_tags(workspace_id, tags)
        
        return TaggedContentResult(
            notes=notes,
            research=research,
        )
    
    async def get_recent_activity(self, workspace_id: UUID, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently created or updated writing content."""
        notes = await self.writing_repository.get_author_notes_by_workspace(workspace_id)
        research = await self.writing_repository.get_research_items_by_workspace(workspace_id)
        characters = await self.writing_repository.get_character_profiles_by_workspace(workspace_id)
        outlines = await self.writing_repository.get_plot_outlines_by_workspace(workspace_id)
        
        # Combine and sort by updated_at or created_at
        all_items = []
        
        for note in notes:
            all_items.append({
                "type": "note",
                "id": note.id,
                "title": note.title,
                "updated_at": note.updated_at or note.created_at,
                "item": note
            })
        
        for item in research:
            all_items.append({
                "type": "research",
                "id": item.id,
                "title": item.title,
                "updated_at": item.updated_at or item.created_at,
                "item": item
            })
        
        for character in characters:
            all_items.append({
                "type": "character",
                "id": character.id,
                "title": character.name,
                "updated_at": character.updated_at or character.created_at,
                "item": character
            })
        
        for outline in outlines:
            all_items.append({
                "type": "plot_outline",
                "id": outline.id,
                "title": outline.title,
                "updated_at": outline.updated_at or outline.created_at,
                "item": outline
            })
        
        # Sort by most recent first
        all_items.sort(key=lambda x: x["updated_at"], reverse=True)
        
        return all_items[:limit]