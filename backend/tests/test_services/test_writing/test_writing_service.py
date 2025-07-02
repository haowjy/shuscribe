"""
Comprehensive tests for WritingService with memory repositories
"""

import pytest
from uuid import uuid4
from typing import Dict, Any, List

from src.schemas.db.writing import (
    AuthorNote, AuthorNoteCreate, AuthorNoteUpdate,
    WritingPrompt, WritingPromptCreate, WritingPromptUpdate
)
from src.schemas.db.workspace import Workspace
from src.services.writing.writing_service import WritingService
from src.database.factory import RepositoryContainer


@pytest.fixture
async def writing_service(repository_container: RepositoryContainer) -> WritingService:
    """Provide WritingService with memory repositories."""
    return WritingService(
        writing_repository=repository_container.writing,
        workspace_repository=repository_container.workspace
    )


@pytest.fixture
async def sample_workspace(repository_container: RepositoryContainer) -> Workspace:
    """Create a sample workspace for writing tools."""
    from src.schemas.db.user import UserCreate
    from src.schemas.db.workspace import WorkspaceCreate
    
    user = await repository_container.user.create_user(UserCreate(
        email="writer@example.com",
        display_name="Writer User"
    ))
    
    return await repository_container.workspace.create_workspace(WorkspaceCreate(
        owner_id=user.id,
        name="Writing Workspace",
        description="Workspace for writing tools testing"
    ))


@pytest.fixture
async def sample_note(writing_service: WritingService, sample_workspace: Workspace) -> AuthorNote:
    """Create a sample author note for testing."""
    note_data = AuthorNoteCreate(
        workspace_id=sample_workspace.id,
        title="Character Development Note",
        content="Remember to develop the protagonist's backstory in chapter 5.",
        note_type="character",
        tags=["character", "development", "protagonist"]
    )
    return await writing_service.create_author_note(note_data)


@pytest.fixture
async def sample_prompt(writing_service: WritingService, sample_workspace: Workspace) -> WritingPrompt:
    """Create a sample writing prompt for testing."""
    prompt_data = WritingPromptCreate(
        workspace_id=sample_workspace.id,
        title="Battle Scene Prompt",
        prompt_text="Write a dramatic battle scene between the hero and the main antagonist.",
        category="scene",
        tags=["action", "climax", "battle"]
    )
    return await writing_service.create_writing_prompt(prompt_data)


class TestAuthorNotes:
    """Test author note management"""
    
    async def test_create_author_note_success(self, writing_service: WritingService, sample_workspace: Workspace):
        """Test creating a new author note"""
        note_data = AuthorNoteCreate(
            workspace_id=sample_workspace.id,
            title="Plot Point Note",
            content="Need to foreshadow the twist in chapter 3.",
            note_type="plot",
            tags=["plot", "foreshadowing", "twist"],
            metadata={"chapter_reference": 3, "priority": "high"}
        )
        
        note = await writing_service.create_author_note(note_data)
        
        assert note.id is not None
        assert note.workspace_id == sample_workspace.id
        assert note.title == "Plot Point Note"
        assert note.content == "Need to foreshadow the twist in chapter 3."
        assert note.note_type == "plot"
        assert note.tags == ["plot", "foreshadowing", "twist"]
        assert note.metadata["chapter_reference"] == 3
        assert note.created_at is not None
    
    async def test_create_author_note_workspace_not_found(self, writing_service: WritingService):
        """Test error when creating note for non-existent workspace"""
        fake_workspace_id = uuid4()
        note_data = AuthorNoteCreate(
            workspace_id=fake_workspace_id,
            title="Test Note",
            content="Test content"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await writing_service.create_author_note(note_data)
        
        assert f"Workspace {fake_workspace_id} not found" in str(exc_info.value)
    
    async def test_get_author_note_by_id(self, writing_service: WritingService, sample_note: AuthorNote):
        """Test retrieving author note by ID"""
        retrieved = await writing_service.get_author_note(sample_note.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_note.id
        assert retrieved.title == sample_note.title
        assert retrieved.content == sample_note.content
    
    async def test_get_author_note_not_found(self, writing_service: WritingService):
        """Test retrieving non-existent note returns None"""
        fake_id = uuid4()
        note = await writing_service.get_author_note(fake_id)
        assert note is None
    
    async def test_update_author_note_success(self, writing_service: WritingService, sample_note: AuthorNote):
        """Test updating author note content and metadata"""
        update_data = AuthorNoteUpdate(
            title="Updated Character Note",
            content="Updated: Develop protagonist's tragic backstory in chapters 5-7.",
            tags=["character", "development", "protagonist", "updated"],
            metadata={"chapters": [5, 6, 7], "importance": "critical"}
        )
        
        updated = await writing_service.update_author_note(sample_note.id, update_data)
        
        assert updated.title == "Updated Character Note"
        assert updated.content == "Updated: Develop protagonist's tragic backstory in chapters 5-7."
        assert updated.tags == ["character", "development", "protagonist", "updated"]
        assert updated.metadata["chapters"] == [5, 6, 7]
        assert updated.note_type == sample_note.note_type  # Unchanged
    
    async def test_update_author_note_not_found(self, writing_service: WritingService):
        """Test error when updating non-existent note"""
        fake_id = uuid4()
        update_data = AuthorNoteUpdate(title="New Title")
        
        with pytest.raises(ValueError) as exc_info:
            await writing_service.update_author_note(fake_id, update_data)
        
        assert f"Author note {fake_id} not found" in str(exc_info.value)
    
    async def test_delete_author_note_success(self, writing_service: WritingService, sample_note: AuthorNote):
        """Test deleting an author note"""
        result = await writing_service.delete_author_note(sample_note.id)
        assert result is True
        
        # Verify it's gone
        retrieved = await writing_service.get_author_note(sample_note.id)
        assert retrieved is None
    
    async def test_delete_author_note_not_found(self, writing_service: WritingService):
        """Test deleting non-existent note returns False"""
        fake_id = uuid4()
        result = await writing_service.delete_author_note(fake_id)
        assert result is False
    
    async def test_get_author_notes_by_workspace(self, writing_service: WritingService, sample_workspace: Workspace):
        """Test getting all author notes for a workspace"""
        # Create multiple notes
        note_types = ["character", "plot", "world"]
        created_notes = []
        
        for i, note_type in enumerate(note_types):
            note = await writing_service.create_author_note(AuthorNoteCreate(
                workspace_id=sample_workspace.id,
                title=f"Note {i+1}",
                content=f"Content for {note_type} note",
                note_type=note_type,
                tags=[note_type, "test"]
            ))
            created_notes.append(note)
        
        # Get all notes
        notes = await writing_service.get_author_notes_by_workspace(sample_workspace.id)
        
        assert len(notes) == 3
        note_titles = [n.title for n in notes]
        assert "Note 1" in note_titles
        assert "Note 2" in note_titles
        assert "Note 3" in note_titles
    
    async def test_get_author_notes_by_tag(self, writing_service: WritingService, sample_workspace: Workspace):
        """Test filtering author notes by tag"""
        # Create notes of different types
        await writing_service.create_author_note(AuthorNoteCreate(
            workspace_id=sample_workspace.id,
            title="Character Note 1",
            content="About character development",
            note_type="character",
            tags=["character", "development", "protagonist"]
        ))
        
        await writing_service.create_author_note(AuthorNoteCreate(
            workspace_id=sample_workspace.id,
            title="Plot Note 1",
            content="About plot structure",
            note_type="plot",
            tags=["plot", "structure", "themes"]
        ))
        
        await writing_service.create_author_note(AuthorNoteCreate(
            workspace_id=sample_workspace.id,
            title="Character Note 2",
            content="More character insights",
            note_type="character",
            tags=["character", "development", "protagonist"]
        ))
        
        # Get only character notes
        character_notes = await writing_service.get_author_notes_by_tags(
            sample_workspace.id, ["character"]
        )
        
        assert len(character_notes) == 2
        assert all(n.note_type == "character" for n in character_notes)
        titles = [n.title for n in character_notes]
        assert "Character Note 1" in titles
        assert "Character Note 2" in titles
    
    async def test_search_author_notes(self, writing_service: WritingService, sample_workspace: Workspace):
        """Test searching author notes by content"""
        # Create notes with specific content
        await writing_service.create_author_note(AuthorNoteCreate(
            workspace_id=sample_workspace.id,
            title="Magic System Note",
            content="The magic system is based on elemental powers and requires focus.",
            note_type="world"
        ))
        
        await writing_service.create_author_note(AuthorNoteCreate(
            workspace_id=sample_workspace.id,
            title="Character Magic",
            content="The protagonist discovers their magical abilities in chapter 4.",
            note_type="character"
        ))
        
        await writing_service.create_author_note(AuthorNoteCreate(
            workspace_id=sample_workspace.id,
            title="Combat System",
            content="Combat involves both physical and strategic elements.",
            note_type="world"
        ))
        
        # Search for "magic"
        magic_notes = await writing_service.search_author_notes(sample_workspace.id, "magic")
        
        assert len(magic_notes) == 2
        titles = [n.title for n in magic_notes]
        assert "Magic System Note" in titles
        assert "Character Magic" in titles
        assert "Combat System" not in titles


class TestWritingPrompts:
    """Test writing prompt management"""
    
    async def test_create_writing_prompt_success(self, writing_service: WritingService, sample_workspace: Workspace):
        """Test creating a new writing prompt"""
        prompt_data = WritingPromptCreate(
            workspace_id=sample_workspace.id,
            title="Dialogue Challenge",
            prompt_text="Write a tense conversation between two former friends who are now enemies.",
            category="dialogue",
            tags=["dialogue", "tension", "conflict"]
        )
        
        prompt = await writing_service.create_writing_prompt(prompt_data)
        
        assert prompt.id is not None
        assert prompt.workspace_id == sample_workspace.id
        assert prompt.title == "Dialogue Challenge"
        assert prompt.prompt_text == "Write a tense conversation between two former friends who are now enemies."
        assert prompt.category == "dialogue"
        assert prompt.tags == ["dialogue", "tension", "conflict"]
        assert prompt.created_at is not None
    
    async def test_create_writing_prompt_workspace_not_found(self, writing_service: WritingService):
        """Test error when creating prompt for non-existent workspace"""
        fake_workspace_id = uuid4()
        prompt_data = WritingPromptCreate(
            workspace_id=fake_workspace_id,
            title="Test Prompt",
            prompt_text="Test content"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await writing_service.create_writing_prompt(prompt_data)
        
        assert f"Workspace {fake_workspace_id} not found" in str(exc_info.value)
    
    async def test_get_writing_prompt_by_id(self, writing_service: WritingService, sample_prompt: WritingPrompt):
        """Test retrieving writing prompt by ID"""
        retrieved = await writing_service.get_writing_prompt(sample_prompt.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_prompt.id
        assert retrieved.title == sample_prompt.title
        assert retrieved.prompt_text == sample_prompt.prompt_text
    
    async def test_update_writing_prompt_success(self, writing_service: WritingService, sample_prompt: WritingPrompt):
        """Test updating writing prompt"""
        update_data = WritingPromptUpdate(
            title="Enhanced Battle Scene",
            prompt_text="Write an epic battle scene with magical elements and tactical combat.",
            tags=["action", "climax", "battle", "magic", "tactics"]
        )
        
        updated = await writing_service.update_writing_prompt(sample_prompt.id, update_data)
        
        assert updated.title == "Enhanced Battle Scene"
        assert updated.prompt_text == "Write an epic battle scene with magical elements and tactical combat."
        assert updated.tags == ["action", "climax", "battle", "magic", "tactics"]
    
    async def test_get_writing_prompts_by_workspace(self, writing_service: WritingService, sample_workspace: Workspace):
        """Test getting all writing prompts for a workspace"""
        # Create multiple prompts
        prompt_types = ["scene", "character", "dialogue"]
        
        for i, prompt_type in enumerate(prompt_types):
            await writing_service.create_writing_prompt(WritingPromptCreate(
                workspace_id=sample_workspace.id,
                title=f"Prompt {i+1}",
                prompt_text=f"Write a {prompt_type} exercise",
                category=prompt_type
            ))
        
        # Get all prompts
        prompts = await writing_service.get_writing_prompts_by_workspace(sample_workspace.id)
        
        assert len(prompts) == 3
        prompt_titles = [p.title for p in prompts]
        assert "Prompt 1" in prompt_titles
        assert "Prompt 2" in prompt_titles
        assert "Prompt 3" in prompt_titles
    
    async def test_get_writing_prompts_by_category(self, writing_service: WritingService, sample_workspace: Workspace):
        """Test filtering writing prompts by category"""
        # Create prompts of different types
        await writing_service.create_writing_prompt(WritingPromptCreate(
            workspace_id=sample_workspace.id,
            title="Scene Prompt 1",
            prompt_text="Describe a marketplace",
            category="scene"
        ))
        
        await writing_service.create_writing_prompt(WritingPromptCreate(
            workspace_id=sample_workspace.id,
            title="Character Prompt 1",
            prompt_text="Develop a villain's motivation",
            category="character"
        ))
        
        await writing_service.create_writing_prompt(WritingPromptCreate(
            workspace_id=sample_workspace.id,
            title="Scene Prompt 2",
            prompt_text="Write a chase sequence",
            category="scene"
        ))
        
        # Get only scene prompts
        scene_prompts = await writing_service.get_writing_prompts_by_category(
            sample_workspace.id, "scene"
        )
        
        assert len(scene_prompts) == 2
        assert all(p.category == "scene" for p in scene_prompts)


# TODO: Move conversation functionality to agent domain
# Commenting out conversation tests until conversation functionality is implemented
# class TestConversationHistory:
#     """Test conversation history management"""
#     
#     async def test_save_conversation_message(self, writing_service, sample_workspace):
#         pass
#     
#     async def test_get_conversation_history(self, writing_service, sample_workspace):
#         pass
#     
#     async def test_get_conversation_history_with_limit(self, writing_service, sample_workspace):
#         pass
#     
#     async def test_delete_conversation(self, writing_service, sample_workspace):
#         pass


class TestWritingStatistics:
    """Test writing tools statistics"""
    
    async def test_get_writing_statistics(self, writing_service: WritingService, sample_workspace: Workspace):
        """Test retrieving comprehensive writing statistics"""
        # Create various writing tools
        for i in range(3):
            await writing_service.create_author_note(AuthorNoteCreate(
                workspace_id=sample_workspace.id,
                title=f"Note {i}",
                content=f"Note content {i}",
                note_type="character" if i % 2 == 0 else "plot"
            ))
        
        for i in range(2):
            await writing_service.create_writing_prompt(WritingPromptCreate(
                workspace_id=sample_workspace.id,
                title=f"Prompt {i}",
                prompt_text=f"Prompt content {i}",
                category="scene"
            ))
        
        # TODO: Save some conversation messages (moved to agent domain)
        # for i in range(5):
        #     await writing_service.save_conversation_message(
        #         sample_workspace.id,
        #         "test_chat",
        #         {"role": "user" if i % 2 == 0 else "assistant", "content": f"Message {i}"}
        #     )
        
        # Get statistics
        stats = await writing_service.get_writing_statistics(sample_workspace.id)
        
        assert stats["total_notes"] == 3
        assert stats["total_prompts"] == 2
        # TODO: Re-enable when conversation functionality is implemented
        # assert stats["total_conversations"] == 1
        # assert stats["total_messages"] == 5
        assert stats["workspace_id"] == sample_workspace.id


class TestIntegration:
    """Integration tests for writing workflows"""
    
    async def test_full_writing_workflow(self, writing_service: WritingService, sample_workspace: Workspace):
        """Test complete writing tools workflow"""
        # 1. Create initial planning note
        planning_note = await writing_service.create_author_note(AuthorNoteCreate(
            workspace_id=sample_workspace.id,
            title="Story Planning",
            content="Initial ideas for the story structure and main themes.",
            note_type="plot",
            tags=["planning", "structure", "themes"]
        ))
        
        # 2. Create character development prompt
        char_prompt = await writing_service.create_writing_prompt(WritingPromptCreate(
            workspace_id=sample_workspace.id,
            title="Character Development Exercise",
            prompt_text="Write a scene showing your protagonist's biggest fear.",
            category="character",
            tags=["character", "fear", "development"]
        ))
        
        # TODO: 3. Start a conversation about character development (moved to agent domain)
        # await writing_service.save_conversation_message(
        #     sample_workspace.id,
        #     "character_dev_chat",
        #     {"role": "user", "content": "I'm struggling with my protagonist's motivation"}
        # )
        # 
        # await writing_service.save_conversation_message(
        #     sample_workspace.id,
        #     "character_dev_chat",
        #     {"role": "assistant", "content": "Let's explore their background and what drives them"}
        # )
        
        # 4. Update the planning note based on insights
        await writing_service.update_author_note(planning_note.id, AuthorNoteUpdate(
            content="Updated: Story centers on overcoming fear and finding inner strength.",
            tags=["planning", "structure", "themes", "fear", "strength"]
        ))
        
        # 5. Create more specific notes
        await writing_service.create_author_note(AuthorNoteCreate(
            workspace_id=sample_workspace.id,
            title="Chapter 3 Notes",
            content="This is where the protagonist faces their first real challenge.",
            note_type="chapter",
            tags=["chapter-3", "challenge", "growth"]
        ))
        
        # TODO: 6. Add more conversation history (moved to agent domain)
        # await writing_service.save_conversation_message(
        #     sample_workspace.id,
        #     "character_dev_chat",
        #     {"role": "user", "content": "How do I show character growth without being obvious?"}
        # )
        
        # 7. Verify final state
        stats = await writing_service.get_writing_statistics(sample_workspace.id)
        assert stats["total_notes"] == 2
        assert stats["total_prompts"] == 1
        # TODO: Re-enable when conversation functionality is implemented
        # assert stats["total_conversations"] == 1
        # assert stats["total_messages"] == 3
        
        # 8. Test search functionality
        fear_notes = await writing_service.search_author_notes(sample_workspace.id, "fear")
        assert len(fear_notes) == 1
        
        # TODO: 9. Get conversation history (moved to agent domain)
        # history = await writing_service.get_conversation_history(
        #     sample_workspace.id,
        #     "character_dev_chat"
        # )
        # assert len(history) == 3
        # assert any("motivation" in msg.content for msg in history)
        # assert any("growth" in msg.content for msg in history)