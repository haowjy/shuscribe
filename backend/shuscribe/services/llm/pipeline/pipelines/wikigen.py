# shuscribe/services/llm/pipeline/pipelines/wikigen.py

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import AsyncGenerator, List, Optional
import yaml
import json
import os
import logging

from shuscribe.schemas.llm import GenerationConfig, Message
from shuscribe.schemas.pipeline import Chapter, WikiGenPipelineConfig, PipelineStepInfo, StoryMetadata, StreamPipelineChunk, StreamStatus
from shuscribe.schemas.wikigen.entity import EntitySigLvl, TempEntityDB, TempEntityDBRepresentation, TempEntityRecord
from shuscribe.services.llm.pipeline.base_pipeline import Pipeline
from shuscribe.schemas.wikigen.entity import UpsertEntitiesOutSchema, ExtractEntitiesOutSchema
from shuscribe.schemas.wikigen.wiki import WikiPage
from shuscribe.schemas.wikigen.summary import ChapterSummary
from shuscribe.schemas.streaming import StreamChunk
from shuscribe.utils import merge_pydantic_models, simple_token_estimator

logger = logging.getLogger(__name__)

class WikiGenStep(str, Enum):
    LOAD_CHAPTER = "LOAD_CHAPTER"
    GENERATE_SUMMARY = "GENERATE_SUMMARY"
    EXTRACT_ENTITIES = "EXTRACT_ENTITIES"
    UPSERT_ENTITIES = "UPSERT_ENTITIES"
    GENERATE_WIKI = "GENERATE_WIKI"
    SAVE_RESULTS = "SAVE_RESULTS"

@dataclass
class CurrentState:
    summary_so_far: Optional[WikiPage] = None
    recent_chap_summaries: List[ChapterSummary] = field(default_factory=list)
    
    
    chapter_summary: Optional[ChapterSummary] = None
    entities: Optional[ExtractEntitiesOutSchema] = None
    upsert_entities: Optional[UpsertEntitiesOutSchema] = None
    
    
    
    prev_chapter_tokens: int = 0
    
    def add_new_chap_summary(self, new_chapter_summary: ChapterSummary) -> bool:
        popped = False
        old_summary = self.chapter_summary
        self.chapter_summary = new_chapter_summary
        
        if old_summary is None:
            return popped
        
        # limit by number of tokens
        new_tokens = simple_token_estimator(old_summary.to_prompt())
        self.prev_chapter_tokens += new_tokens
        
        while self.prev_chapter_tokens > 10000:
            self.prev_chapter_tokens -= simple_token_estimator(self.recent_chap_summaries[0].to_prompt())
            self.recent_chap_summaries.pop(0)
            popped = True
        self.recent_chap_summaries.append(old_summary)
        return popped
    
    def insert_old_chap_summary(self, chapter_summary: ChapterSummary) -> bool:
        """Insert a chapter summary into the back of the list
        
        Returns True if the chapter summary was inserted, False if it was not (because it exceeded the token limit)
        """
        failed = False
        # limit by number of tokens
        new_tokens = simple_token_estimator(chapter_summary.to_prompt())
        self.prev_chapter_tokens += new_tokens
        
        if self.prev_chapter_tokens > 10000:
            failed = True
            
        self.recent_chap_summaries.insert(0, chapter_summary)
        return failed
        
        
    def add_wiki(self, wiki: WikiPage):
        self.summary_so_far = wiki
        



class WikiGenerationPipeline(Pipeline):
    """Implementation of the wiki generation pipeline from the notebook"""
    
    def __init__(self, session_id: str, pipeline_id: str, config: WikiGenPipelineConfig):
        super().__init__(session_id, pipeline_id, config)
        self.chapters: List[Chapter] = []
        self.story_metadata: Optional[StoryMetadata] = None
        self.entity_db: TempEntityDB = TempEntityDB()
        self.current_state: CurrentState = CurrentState()
        self.end_chapter_idx: int = self.init_story(self.config.start_chapter_idx)
    
    @property
    def story_path(self) -> Path:
        return self.config.story_dir / self.config.story_name
        
    async def run(self) -> AsyncGenerator[StreamPipelineChunk, None]:
        """Run the pipeline and yield stream chunks"""
        try:
            self.is_running = True
            
            # Initialize pipeline
            yield await self.update_step(PipelineStepInfo.INITIALIZE(), message="Initializing pipeline")
            
            # Process chapters
            for chapter_index in range(self.current_chapter_idx, self.end_chapter_idx + 1):
                # Load chapter
                yield await self.update_step(PipelineStepInfo(id=WikiGenStep.LOAD_CHAPTER, name="Load Chapter", description="Loading chapter"), 
                                           chapter_idx=chapter_index,
                                           message=f"Loading chapter {chapter_index}")
                chapter: Chapter = self.load_chapter(chapter_index)
                
                # Generate chapter summary
                yield await self.update_step(PipelineStepInfo(id=WikiGenStep.GENERATE_SUMMARY, name="Generate Summary", description="Generating summary"), 
                                           chapter_idx=chapter_index,
                                           message=f"Generating summary for chapter {chapter_index}")
                
                # Stream the summary generation process
                async for chunk in self.generate_chapter_summary(chapter):
                    # Update with streaming text
                    yield StreamPipelineChunk(
                        text=chunk.text,
                        accumulated_text="",
                        status=StreamStatus.ACTIVE,
                        session_id=self.session_id,
                        pipeline_id=self.pipeline_id,
                        step=PipelineStepInfo(id=WikiGenStep.GENERATE_SUMMARY, name="Generate Summary", description="Generating summary"),
                        chapter=chapter_index,
                        step_message="Generating summary"
                    )
                
                # Extract entities
                yield await self.update_step(PipelineStepInfo(id=WikiGenStep.EXTRACT_ENTITIES, name="Extract Entities", description="Extracting entities"), 
                                           chapter_idx=chapter_index,
                                           message=f"Extracting entities for chapter {chapter_index}")
                
                # Stream the entity extraction process
                async for chunk in self.extract_entities(chapter):
                    yield StreamPipelineChunk(
                        text=chunk.text,
                        accumulated_text="",
                        status=StreamStatus.ACTIVE,
                        session_id=self.session_id,
                        pipeline_id=self.pipeline_id,
                        step=PipelineStepInfo(id=WikiGenStep.EXTRACT_ENTITIES, name="Extract Entities", description="Extracting entities"),
                        chapter=chapter_index,
                        step_message="Extracting entities"
                    )
                
                # Upsert entities
                yield await self.update_step(
                    PipelineStepInfo(
                        id=WikiGenStep.UPSERT_ENTITIES, 
                        name="Upsert Entities", 
                        description="Upserting entities"
                    ), 
                    chapter_idx=chapter_index,
                    message=f"Updating entity database for chapter {chapter_index}"
                )
                
                async for chunk in self.upsert_entities(chapter):
                    yield StreamPipelineChunk(
                        text=chunk.text,
                        accumulated_text="",
                        status=StreamStatus.ACTIVE,
                        session_id=self.session_id, 
                        pipeline_id=self.pipeline_id,
                        step=PipelineStepInfo(id=WikiGenStep.UPSERT_ENTITIES, name="Upsert Entities", description="Upserting entities"),
                        chapter=chapter_index,
                        step_message="Updating entity database"
                    )
                
                # Generate wiki
                yield await self.update_step(PipelineStepInfo(id=WikiGenStep.GENERATE_WIKI, name="Generate Wiki", description="Generating wiki"), 
                                           chapter_idx=chapter_index,
                                           message=f"Generating wiki for chapter {chapter_index}")
                
                async for chunk in self.generate_wiki(chapter):
                    yield StreamPipelineChunk(
                        text=chunk.text,
                        accumulated_text="",
                        status=StreamStatus.ACTIVE,
                        session_id=self.session_id,
                        pipeline_id=self.pipeline_id,
                        step=PipelineStepInfo(id=WikiGenStep.GENERATE_WIKI, name="Generate Wiki", description="Generating wiki"),
                        chapter=chapter_index,
                        step_message="Generating wiki"
                    )
                
                # Save results
                yield await self.update_step(PipelineStepInfo(id=WikiGenStep.SAVE_RESULTS, name="Save Results", description="Saving results"), 
                                           chapter_idx=chapter_index,
                                           message=f"Saving results for chapter {chapter_index}")
                await self.save_results(chapter_index)
            
            # Complete pipeline
            yield StreamPipelineChunk(
                text="Pipeline execution completed successfully",
                accumulated_text="",
                status=StreamStatus.COMPLETE,
                session_id=self.session_id,
                pipeline_id=self.pipeline_id,
                step=PipelineStepInfo.COMPLETE(),
                chapter=self.config.end_chapter_idx,
                step_message="Pipeline completed successfully",
                progress={"current": self.current_chapter_idx, 
                          "total": self.config.end_chapter_idx}
            )
            
        except Exception as e:
            # Handle error
            yield await self.handle_error(e)
    
    def init_story(self, start_chapter_idx: int) -> int:
        """Load story metadata from YAML file"""
        meta_path = self.story_path / "story" / "_meta.yaml"
        
        with open(meta_path, "r") as f:
            meta = yaml.safe_load(f)
            self.story_metadata = StoryMetadata(
                title=meta.get('story_title'),
                description=meta.get('story_description'),
                genres=meta.get('genres'),
                additional_tags=meta.get('additional_tags'),
                chapter_files=meta.get('chapters')
            )
            
        if self.config.end_chapter_idx is None:
            self.config.end_chapter_idx = len(self.story_metadata.chapter_files) if self.story_metadata.chapter_files else 0
        
        # Load chapters
        if self.story_metadata.chapter_files:
            for chapter_file in self.story_metadata.chapter_files:
                chapter_path = self.story_path / "story" / chapter_file
                with open(chapter_path, "r") as f:
                    chapter_content = yaml.safe_load(f)
                    self.chapters.append(Chapter(id=int(chapter_file.split('.')[0]), title=chapter_content.get('title'), content=chapter_content.get('content')))
        
        if start_chapter_idx > 1:
            self.load_prev_cached_results(start_chapter_idx - 1)
        
        return self.config.end_chapter_idx
    
    def load_prev_cached_results(self, prev_chapter_index: int):
        """Load cached results for the current chapter"""
        out_dir = self.story_path / f"{prev_chapter_index}out"
        
        # Load comprehensive wiki
        wiki_path = out_dir / "comprehensive_wiki.md"
        
        with open(wiki_path, "r") as f:
            wiki_str = f.read()
            self.current_state.summary_so_far = WikiPage.from_wiki_content(
                "Comprehensive Wiki Page", 
                wiki_str
            )
        
        # Load chapter summaries
        for i in range(prev_chapter_index, -1, -1):
            summary_path = self.story_path / f"{i}out" / "chapter_summary.md"
            with open(summary_path, "r") as f:
                summary_str = f.read()
                success = self.current_state.insert_old_chap_summary(ChapterSummary.from_chapter_summary(
                    i, 
                    summary_str
                ))
                if not success:
                    break
                
        # Load entity database
        entity_db_path = out_dir / "entity_db.json"
        if entity_db_path.exists():
            with open(entity_db_path, "r") as f:
                entities_db = TempEntityDBRepresentation.model_validate_json(f.read())
                self.entity_db.entities_db = entities_db
                
    
    def load_chapter(self, chapter_index: int) -> Chapter:
        """Load chapter content from YAML file"""
        
        # Find the requested chapter
        return self.chapters[chapter_index]
    
    async def generate_chapter_summary(self, chapter: Chapter) -> AsyncGenerator[StreamChunk, None]:
        """Generate summary for the current chapter"""
        from shuscribe.services.llm.prompts import templates
        from shuscribe.services.llm.session import LLMSession
        # Reload template to get latest version
        templates.chapter.summary.reload()
        
        # Prepare messages for summary generation
        summary_messages = templates.chapter.summary.format(
            current_chapter=chapter,
            story_metadata=self.story_metadata,
            summary_so_far=self.current_state.summary_so_far,
            recent_summaries=self.current_state.recent_chap_summaries,
        )
        
        # Create config from pipeline config
        if self.config.summary_config:
            config = self.config.summary_config.to_generation_config()
            config = merge_pydantic_models(templates.chapter.summary.default_config, config)
        else:
            config = templates.chapter.summary.default_config
        
        # Use session to generate
        async with LLMSession.session_scope() as session:
            async for chunk in session.generate_stream(
                messages=summary_messages,
                provider_name="",
                model="",
                config=config
            ):
                yield chunk
        
        if chunk:
            if chunk.status == StreamStatus.COMPLETE:
                self.current_state.add_new_chap_summary(ChapterSummary.from_chapter_summary(
                    chapter.id, 
                    chunk.accumulated_text
                ))
            elif chunk.status == StreamStatus.ERROR:
                raise Exception(chunk.error)
    
    async def extract_entities(self, chapter: Chapter) -> AsyncGenerator[StreamChunk, None]:
        """Extract entities from the current chapter"""
        from shuscribe.services.llm.prompts import templates
        from shuscribe.services.llm.session import LLMSession
        # Reload template to get latest version
        templates.entity.extract.reload()
        
        # Prepare messages for entity extraction
        entity_messages = templates.entity.extract.format(
            current_chapter=chapter,
            story_metadata=self.story_metadata,
            summary_so_far=self.current_state.summary_so_far,
            recent_summaries=self.current_state.recent_chap_summaries,
            chapter_summary=self.current_state.chapter_summary,
        )
        
        # Create config from pipeline config
        if self.config.entity_extraction_config:
            config = self.config.entity_extraction_config.to_generation_config()
            config = merge_pydantic_models(templates.entity.extract.default_config, config)
        else:
            config = templates.entity.extract.default_config
        
        # Use session to generate
        async with LLMSession.session_scope() as session:
            async for chunk in session.generate_stream(
                messages=entity_messages,
                provider_name="",
                model="",
                config=config
            ):
                yield chunk
            
        if chunk:
            if chunk.status == StreamStatus.COMPLETE:
                self.current_state.entities = ExtractEntitiesOutSchema.model_validate_json(
                    chunk.accumulated_text
                )
            elif chunk.status == StreamStatus.ERROR:
                raise Exception(chunk.error)
            
    async def upsert_entities(self, chapter: Chapter) -> AsyncGenerator[StreamChunk, None]:
        """Update existing entities or create new ones"""
        from shuscribe.services.llm.prompts import templates
        
        # Reload template to get latest version
        templates.entity.upsert.reload()
        
        # Parse extracted entities
        if not self.current_state.entities:
            raise ValueError("Entity extraction results not found")
            
        extracted_entities = self.current_state.entities
        
        # Filter entities by significance level
        ent_list = extracted_entities.filter_entities(EntitySigLvl.RELEVANT)

        existing_entities: set[TempEntityRecord] = set()

        for entity in ent_list:
            for result in self.entity_db.search(json.dumps(entity.to_upsert_dict(ent_list), indent=2)):
                existing_entities.add(result[0])
        
        self.current_state.upsert_entities = UpsertEntitiesOutSchema(entities=[])
        
        # Get batch for upsert (prepare entity data)
        for entity_batch in extracted_entities.batch_for_upsert(EntitySigLvl.RELEVANT):
            upsert_messages: list[Message] = templates.entity.upsert.format( 
                current_chapter=chapter,
                entity_batch=entity_batch,
                story_metadata=self.story_metadata,
                chapter_summary=self.current_state.chapter_summary,
                existing_entities=list(existing_entities) if existing_entities else None,
            )
            
            async for chunk in self.generate_stream(upsert_messages, "", "", templates.entity.upsert.default_config):
                yield chunk
            if chunk:
                if chunk.status == StreamStatus.COMPLETE:
                    self.current_state.upsert_entities.entities.extend(UpsertEntitiesOutSchema.model_validate_json(chunk.accumulated_text).entities)
                elif chunk.status == StreamStatus.ERROR:
                    raise Exception(chunk.error)
        
        # Update entity database
        self.entity_db.upsert(self.current_state.upsert_entities.entities)


 
    
    async def generate_wiki(self, chapter: Chapter) -> AsyncGenerator[StreamChunk, None]:
        """Generate comprehensive wiki document"""
        from shuscribe.services.llm.prompts import templates
        from shuscribe.services.llm.session import LLMSession
        
        # Reload template to get latest version
        templates.story.comprehensive_wiki.reload()
        
        if not self.current_state.chapter_summary:
            raise ValueError("Chapter summary not found")
        
        # Prepare messages for wiki generation
        wiki_messages = templates.story.comprehensive_wiki.format(
            current_chapter=chapter,
            story_metadata=self.story_metadata,
            summary_so_far=self.current_state.summary_so_far,
            recent_summaries=self.current_state.recent_chap_summaries,
            chapter_summary=self.current_state.chapter_summary,
        )
        
        # Create config from pipeline config
        if self.config.wiki_generation_config:
            config = self.config.wiki_generation_config.to_generation_config()
            config = merge_pydantic_models(templates.story.comprehensive_wiki.default_config, config)
        else:
            config = templates.story.comprehensive_wiki.default_config
        
        config = merge_pydantic_models(templates.story.comprehensive_wiki.default_config, config)
        
        # Use session to generate
        async with LLMSession.session_scope() as session:
            async for chunk in session.generate_stream(
                messages=wiki_messages,
                provider_name="",
                model="",
                config=config
            ):
                yield chunk
        
        if chunk:
            if chunk.status == StreamStatus.COMPLETE:
                self.current_state.summary_so_far = WikiPage.from_wiki_content(
                    "Comprehensive Wiki Page", 
                    chunk.accumulated_text
                )
            elif chunk.status == StreamStatus.ERROR:
                raise Exception(chunk.error)
    
    async def save_results(self, chapter_index: int):
        """Save all results for the current chapter"""
        out_dir = self.story_path / f"{chapter_index}out"
        os.makedirs(out_dir, exist_ok=True)
        
        # Save chapter summary
        if self.current_state.chapter_summary:
            with open(out_dir / "chapter_summary.md", "w") as f:
                f.write(self.current_state.chapter_summary.raw_summary)
                
        # Save entity extraction results
        if self.current_state.entities:
            with open(out_dir / "extract_entities.json", "w") as f:
                f.write(self.current_state.entities.model_dump_json(indent=2))
                
        # Save entity upsert results
        if self.current_state.upsert_entities:
            with open(out_dir / "upsert_entities.json", "w") as f:
                f.write(self.current_state.upsert_entities.model_dump_json(indent=2))
                
        # Save wiki generation results
        if self.current_state.summary_so_far:
            with open(out_dir / "comprehensive_wiki.md", "w") as f:
                f.write(self.current_state.summary_so_far.raw_content)
                
        # Save entity database - Fixed to use TempEntityDBRepresentation's model_dump_json
        with open(out_dir / "entity_db.json", "w") as f:
            f.write(self.entity_db.entities_db.model_dump_json(indent=2))
            
    async def generate_stream(self, messages: list[Message], provider_name: str, model: str, config: GenerationConfig):
        """Generate a stream of chunks from the LLM"""
        # Use session to generate
        from shuscribe.services.llm.session import LLMSession
        async with LLMSession.session_scope() as session:
            async for chunk in session.generate_stream(
                messages=messages,
                provider_name=provider_name,
                model=model,
                config=config
            ):
                yield chunk
        
            if chunk:
                if chunk.status == StreamStatus.ERROR:
                    raise Exception(chunk.error)