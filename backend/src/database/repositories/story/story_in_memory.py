"""
In-Memory Story Repository Implementation
Handles stories, chapters, arcs, and enhanced chapters in memory for local/CLI usage
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from src.database.repositories.story.story_abc import AbstractStoryRepository
from src.schemas.story import (
    Story, StoryCreate, StoryUpdate, StoryStatus,
    Chapter, ChapterCreate, 
    StoryArc, StoryArcCreate, StoryArcUpdate, ArcStatus,
    EnhancedChapter, EnhancedChapterCreate,
    InputStory, StoryProcessingResult
)
# Wiki functionality moved to wikipage repository - no longer imported here

class InMemoryStoryRepository(AbstractStoryRepository):
    """In-memory implementation of story repository for local usage"""
    
    def __init__(self):
        # Primary data stores
        self._stories: Dict[UUID, Story] = {}
        self._chapters: Dict[UUID, Chapter] = {}
        self._story_arcs: Dict[UUID, StoryArc] = {}
        self._enhanced_chapters: Dict[UUID, EnhancedChapter] = {}
        
        # Index mappings for efficient lookups
        self._stories_by_owner: Dict[UUID, List[UUID]] = {}
        self._chapters_by_story: Dict[UUID, List[UUID]] = {}
        self._arcs_by_story: Dict[UUID, List[UUID]] = {}
        self._enhanced_by_story: Dict[UUID, List[UUID]] = {}
        self._enhanced_by_arc: Dict[UUID, List[UUID]] = {}
        self._enhanced_by_chapter: Dict[UUID, List[UUID]] = {}

    def _add_to_index(self, index_dict: Dict[UUID, List[UUID]], key: UUID, value: UUID):
        """Helper to add value to index list"""
        if key not in index_dict:
            index_dict[key] = []
        if value not in index_dict[key]:
            index_dict[key].append(value)

    def _remove_from_index(self, index_dict: Dict[UUID, List[UUID]], key: UUID, value: UUID):
        """Helper to remove value from index list"""
        if key in index_dict and value in index_dict[key]:
            index_dict[key].remove(value)

    # Story CRUD operations
    async def get_story(self, story_id: UUID) -> Story:
        """Get a story by ID - returns empty story if not found"""
        story = self._stories.get(story_id)
        if story is None:
            # Return empty story instead of None
            return Story.create_empty(owner_id=uuid4())  # We don't know the real owner
        return story

    async def get_stories_by_owner(self, owner_id: UUID) -> List[Story]:
        """Get all stories owned by a user"""
        story_ids = self._stories_by_owner.get(owner_id, [])
        return [self._stories[story_id] for story_id in story_ids if story_id in self._stories]

    async def create_story(self, story_create: StoryCreate) -> Story:
        """Create a new story"""
        story_id = uuid4()
        now = datetime.now(timezone.utc)
        
        story = Story(
            id=story_id,
            title=story_create.title,
            author=story_create.author,
            status=story_create.status,
            owner_id=story_create.owner_id,
            processing_plan=story_create.processing_plan,
            created_at=now,
            updated_at=now
        )
        
        self._stories[story_id] = story
        self._add_to_index(self._stories_by_owner, story_create.owner_id, story_id)
        
        return story

    async def update_story(self, story_id: UUID, story_update: StoryUpdate) -> Story:
        """Update an existing story - returns empty story if not found"""
        if story_id not in self._stories:
            return Story.create_empty(owner_id=uuid4())
            
        story = self._stories[story_id]
        update_data = story_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(story, field, value)
        
        story.updated_at = datetime.now(timezone.utc)
        return story

    async def delete_story(self, story_id: UUID) -> bool:
        """Delete a story and all related data"""
        if story_id not in self._stories:
            return False
        
        story = self._stories[story_id]
        
        # Remove from owner index
        self._remove_from_index(self._stories_by_owner, story.owner_id, story_id)
        
        # Delete all chapters
        chapter_ids = self._chapters_by_story.get(story_id, []).copy()
        for chapter_id in chapter_ids:
            if chapter_id in self._chapters:
                del self._chapters[chapter_id]
        self._chapters_by_story.pop(story_id, None)
        
        # Delete all arcs
        arc_ids = self._arcs_by_story.get(story_id, []).copy()
        for arc_id in arc_ids:
            if arc_id in self._story_arcs:
                del self._story_arcs[arc_id]
        self._arcs_by_story.pop(story_id, None)
        
        # Delete all enhanced chapters
        enhanced_ids = self._enhanced_by_story.get(story_id, []).copy()
        for enhanced_id in enhanced_ids:
            if enhanced_id in self._enhanced_chapters:
                del self._enhanced_chapters[enhanced_id]
        self._enhanced_by_story.pop(story_id, None)
        
        # Finally delete the story
        del self._stories[story_id]
        return True

    # Chapter operations
    async def get_chapters(self, story_id: UUID) -> List[Chapter]:
        """Get all chapters for a story"""
        chapter_ids = self._chapters_by_story.get(story_id, [])
        chapters = [self._chapters[chapter_id] for chapter_id in chapter_ids if chapter_id in self._chapters]
        return sorted(chapters, key=lambda c: c.chapter_number)

    async def get_chapter(self, chapter_id: UUID) -> Chapter:
        """Get a specific chapter - returns empty chapter if not found"""
        chapter = self._chapters.get(chapter_id)
        if chapter is None:
            return Chapter.create_empty()
        return chapter

    async def create_chapter(self, chapter_create: ChapterCreate) -> Chapter:
        """Create a new chapter"""
        chapter_id = uuid4()
        now = datetime.now(timezone.utc)
        
        chapter = Chapter(
            id=chapter_id,
            story_id=chapter_create.story_id,
            chapter_number=chapter_create.chapter_number,
            title=chapter_create.title,
            raw_content=chapter_create.raw_content,
            created_at=now
        )
        
        self._chapters[chapter_id] = chapter
        self._add_to_index(self._chapters_by_story, chapter_create.story_id, chapter_id)
        
        return chapter

    async def create_chapters_bulk(self, chapters_create: List[ChapterCreate]) -> List[Chapter]:
        """Create multiple chapters in bulk"""
        chapters = []
        for chapter_create in chapters_create:
            chapter = await self.create_chapter(chapter_create)
            chapters.append(chapter)
        return chapters

    # Story Arc operations
    async def get_story_arcs(self, story_id: UUID) -> List[StoryArc]:
        """Get all arcs for a story"""
        arc_ids = self._arcs_by_story.get(story_id, [])
        arcs = [self._story_arcs[arc_id] for arc_id in arc_ids if arc_id in self._story_arcs]
        return sorted(arcs, key=lambda a: a.arc_number)

    async def get_story_arc(self, arc_id: UUID) -> Optional[StoryArc]:
        """Get a specific story arc"""
        return self._story_arcs.get(arc_id)

    async def create_story_arc(self, arc_create: StoryArcCreate) -> StoryArc:
        """Create a new story arc"""
        arc_id = uuid4()
        now = datetime.now(timezone.utc)
        
        arc = StoryArc(
            id=arc_id,
            story_id=arc_create.story_id,
            arc_number=arc_create.arc_number,
            title=arc_create.title,
            start_chapter=arc_create.start_chapter,
            end_chapter=arc_create.end_chapter,
            summary=arc_create.summary,
            key_events=arc_create.key_events,
            token_count=arc_create.token_count,
            processing_status=arc_create.processing_status,
            created_at=now,
            updated_at=now
        )
        
        self._story_arcs[arc_id] = arc
        self._add_to_index(self._arcs_by_story, arc_create.story_id, arc_id)
        
        return arc

    async def update_story_arc(self, arc_id: UUID, arc_update: StoryArcUpdate) -> Optional[StoryArc]:
        """Update an existing story arc"""
        if arc_id not in self._story_arcs:
            return None
            
        arc = self._story_arcs[arc_id]
        update_data = arc_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(arc, field, value)
        
        arc.updated_at = datetime.now(timezone.utc)
        return arc

    # Enhanced Chapter operations
    async def get_enhanced_chapters(self, story_id: UUID, arc_id: Optional[UUID] = None) -> List[EnhancedChapter]:
        """Get enhanced chapters for a story/arc"""
        if arc_id:
            enhanced_ids = self._enhanced_by_arc.get(arc_id, [])
        else:
            enhanced_ids = self._enhanced_by_story.get(story_id, [])
        
        return [self._enhanced_chapters[enhanced_id] for enhanced_id in enhanced_ids if enhanced_id in self._enhanced_chapters]

    async def create_enhanced_chapter(self, enhanced_create: EnhancedChapterCreate) -> EnhancedChapter:
        """Create an enhanced chapter"""
        enhanced_id = uuid4()
        now = datetime.now(timezone.utc)
        
        # Get the original chapter to determine story_id for indexing
        chapter = await self.get_chapter(enhanced_create.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {enhanced_create.chapter_id} not found")
        
        enhanced = EnhancedChapter(
            id=enhanced_id,
            chapter_id=enhanced_create.chapter_id,
            arc_id=enhanced_create.arc_id,
            enhanced_content=enhanced_create.enhanced_content,
            link_metadata=enhanced_create.link_metadata,
            created_at=now,
            updated_at=now
        )
        
        self._enhanced_chapters[enhanced_id] = enhanced
        self._add_to_index(self._enhanced_by_story, chapter.story_id, enhanced_id)
        self._add_to_index(self._enhanced_by_arc, enhanced_create.arc_id, enhanced_id)
        self._add_to_index(self._enhanced_by_chapter, enhanced_create.chapter_id, enhanced_id)
        
        return enhanced

    async def create_enhanced_chapters_bulk(self, enhanced_creates: List[EnhancedChapterCreate]) -> List[EnhancedChapter]:
        """Create multiple enhanced chapters in bulk"""
        enhanced_chapters = []
        for enhanced_create in enhanced_creates:
            enhanced = await self.create_enhanced_chapter(enhanced_create)
            enhanced_chapters.append(enhanced)
        return enhanced_chapters

    # High-level operations
    async def store_input_story(self, input_story: InputStory, owner_id: UUID) -> Story:
        """Store an InputStory as a persistent Story with Chapters"""
        # Create the story
        story_create = StoryCreate(
            title=input_story.metadata.title,
            author=input_story.metadata.author,
            status=StoryStatus.PENDING,
            owner_id=owner_id
        )
        story = await self.create_story(story_create)
        
        # Create chapters
        chapters_create = [
            ChapterCreate(
                story_id=story.id,
                chapter_number=chapter.chapter_number,
                title=chapter.title,
                raw_content=chapter.content
            )
            for chapter in input_story.chapters
        ]
        await self.create_chapters_bulk(chapters_create)
        
        return story

    async def store_processing_result(self, processing_result: StoryProcessingResult) -> bool:
        """Store the complete result of story processing"""
        try:
            # Update story status
            await self.update_story(
                processing_result.story.id,
                StoryUpdate(status=StoryStatus.COMPLETED)
            )
            
            # Store arc processing results
            for arc_result in processing_result.arcs:
                # Update arc status
                await self.update_story_arc(
                    arc_result.arc.id,
                    StoryArcUpdate(processing_status=ArcStatus.COMPLETED)
                )
                
                # Store enhanced chapters
                if arc_result.enhanced_chapters:
                    await self.create_enhanced_chapters_bulk([
                        EnhancedChapterCreate(
                            chapter_id=enhanced.chapter_id,
                            arc_id=enhanced.arc_id,
                            enhanced_content=enhanced.enhanced_content,
                            link_metadata=enhanced.link_metadata
                        )
                        for enhanced in arc_result.enhanced_chapters
                    ])
            
            return True
            
        except Exception:
            return False 