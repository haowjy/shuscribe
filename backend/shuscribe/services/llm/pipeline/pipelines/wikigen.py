# shuscribe/services/llm/pipeline/pipelines/wikigen.py

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import AsyncGenerator, List, Optional
import yaml
import json
import os
import logging

from shuscribe.schemas.pipeline import Chapter, WikiGenPipelineConfig, PipelineStepInfo, StoryMetadata, StreamPipelineChunk, StreamStatus
from shuscribe.schemas.wikigen.entity import EntitySigLvl, TempEntityDB, TempEntityDBRepresentation
from shuscribe.services.llm.pipeline.base_pipeline import Pipeline
from shuscribe.services.llm.session import LLMSession
from shuscribe.schemas.wikigen.entity import UpsertEntitiesOutSchema, ExtractEntitiesOutSchema
from shuscribe.schemas.wikigen.wiki import WikiPage
from shuscribe.schemas.wikigen.summary import ChapterSummary
from shuscribe.schemas.llm import GenerationConfig
from shuscribe.schemas.streaming import StreamChunk
from shuscribe.utils import simple_token_estimator

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
    chapter_summary: Optional[ChapterSummary] = None
    recent_chap_summaries: List[ChapterSummary] = []
    
    entities: Optional[ExtractEntitiesOutSchema] = None
    upsert_entities: Optional[UpsertEntitiesOutSchema] = None
    
    summary_so_far: Optional[WikiPage] = None
    
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
        self.chapters = []
        self.story_metadata = None
        self.entity_db = TempEntityDB()
        self.current_state: CurrentState = CurrentState()
    
    @property
    def story_path(self) -> Path:
        return self.config.story_dir / self.config.story_name
        
    async def run(self) -> AsyncGenerator[StreamPipelineChunk, None]:
        """Run the pipeline and yield stream chunks"""
        try:
            self.is_running = True
            
            # Initialize pipeline
            yield await self.update_step(PipelineStepInfo.INITIALIZE(), message="Initializing pipeline")
            await self.init_story(self.config.start_chapter_idx)
            
            # Process chapters
            for chapter_index in range(self.current_chapter_idx, self.config.end_chapter_idx + 1):
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
                yield await self.update_step(PipelineStepInfo(id=WikiGenStep.UPSERT_ENTITIES, name="Upsert Entities", description="Upserting entities"), 
                                           chapter_idx=chapter_index,
                                           message=f"Updating entity database for chapter {chapter_index}")
                
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
                progress={"current": self.config.end_chapter_idx - self.config.start_chapter_idx + 1, 
                          "total": self.config.end_chapter_idx - self.config.start_chapter_idx + 1}
            )
            
        except Exception as e:
            # Handle error
            yield await self.handle_error(e)
    
    
    async def init_story(self, start_chapter_idx: int):
        """Load story metadata from YAML file"""
        meta_path = self.story_path / "_meta.yaml"
        
        with open(meta_path, "r") as f:
            meta = yaml.safe_load(f)
            self.story_metadata = StoryMetadata(
                title=meta.get('story_title'),
                description=meta.get('story_description'),
                genres=meta.get('genres'),
                additional_tags=meta.get('additional_tags')
            )
            
        if start_chapter_idx > 1:
            await self.load_prev_cached_results(start_chapter_idx - 1)
    
    def load_chapter(self, chapter_index: int) -> Chapter:
        """Load chapter content from YAML file"""

        # Load chapter list from metadata if not already loaded
        if not self.chapters:
            meta_path = self.story_path / "story" / "_meta.yaml"
            with open(meta_path, "r") as f:
                meta = yaml.safe_load(f)
                
                # Load all chapters
                for chapter_file in meta.get('chapters', []):
                    chapter_path = self.story_path / "story" / chapter_file
                    try:
                        with open(chapter_path, "r") as cf:
                            chapter_id = int(chapter_file.split('.')[0])
                            chapter_content = yaml.safe_load(cf)
                            self.chapters.append(Chapter(
                                id=chapter_id, 
                                title=chapter_content.get('title'), 
                                content=chapter_content.get('content')
                            ))
                    except Exception as e:
                        logger.warning(f"Error loading chapter {chapter_file}: {str(e)}")
                        continue
        
        # Find the requested chapter
        for chapter in self.chapters:
            if chapter.id == chapter_index:
                return chapter
                
        raise ValueError(f"Chapter {chapter_index} not found")
    
    async def load_prev_cached_results(self, prev_chapter_index: int):
        """Load cached results for the current chapter"""
        out_dir = self.story_path / f"{prev_chapter_index}out"
        
        # Load comprehensive wiki
        wiki_path = out_dir / "comprehensive_wiki.json"
        if wiki_path.exists():
            with open(wiki_path, "r") as f:
                wiki_data = json.loads(f.read())
                self.current_state.summary_so_far = WikiPage.from_wiki_content(
                    "Comprehensive Wiki Page", 
                    wiki_data["accumulated_text"]
                )
        
        # Load chapter summaries
        for i in range(prev_chapter_index, -1, -1):
            summary_path = out_dir / f"chapter_{i}.json"
            if summary_path.exists():
                with open(summary_path, "r") as f:
                    summary_data = json.loads(f.read())
                    success = self.current_state.insert_old_chap_summary(ChapterSummary.from_chapter_summary(
                        i, 
                        StreamChunk.model_validate(summary_data).accumulated_text
                    ))
                    if not success:
                        break
                
        # Load entity database
        entity_db_path = out_dir / "entity_db.json"
        if entity_db_path.exists():
            with open(entity_db_path, "r") as f:
                entities_db = TempEntityDBRepresentation.model_validate_json(f.read())
                self.entity_db.entities_db = entities_db
    
    async def generate_chapter_summary(self, chapter: Chapter) -> AsyncGenerator[StreamChunk, None]:
        """Generate summary for the current chapter"""
        from shuscribe.services.llm.prompts import templates
        
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
        config = GenerationConfig(
            temperature=self.config.summary_config.temperature,
            model=self.config.summary_config.model,
            provider=self.config.summary_config.provider_name,
            thinking_config=self.config.summary_config.thinking_config,
            max_output_tokens=self.config.summary_config.max_output_tokens
        )
        
        # Use session to generate
        async with LLMSession.session_scope() as session:
            async for chunk in session.generate_stream(
                messages=summary_messages,
                provider_name=self.config.summary_config.provider_name,
                model=self.config.summary_config.model,
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
        config = GenerationConfig(
            temperature=self.config.entity_extraction_config.temperature,
            model=self.config.entity_extraction_config.model,
            provider=self.config.entity_extraction_config.provider_name,
            thinking_config=self.config.entity_extraction_config.thinking_config,
            max_output_tokens=self.config.entity_extraction_config.max_output_tokens,
            response_schema=ExtractEntitiesOutSchema
        )
        
        # Use session to generate
        async with LLMSession.session_scope() as session:
            async for chunk in session.generate_stream(
                messages=entity_messages,
                provider_name=self.config.entity_extraction_config.provider_name,
                model=self.config.entity_extraction_config.model,
                config=config
            ):
                yield chunk
    
    async def upsert_entities(self, chapter: Chapter) -> AsyncGenerator[StreamChunk, None]:
        """Update existing entities or create new ones"""
        from shuscribe.services.llm.prompts import templates
        
        # Reload template to get latest version
        templates.entity.upsert.reload()
        
        # Parse extracted entities
        if not self.current_state.entities:
            raise ValueError("Entity extraction results not found")
            
        entities_schema = self.current_state.entities
        
        # Filter entities by significance level
        filtered_entities = entities_schema.filter_entities(EntitySigLvl.RELEVANT)
        
        # Get batch for upsert (prepare entity data)
        entity_batch = next(entities_schema.batch_for_upsert(EntitySigLvl.RELEVANT))
        
        # Find existing entities for this batch
        existing_entities = []
        for entity in filtered_entities:
            # Check if entity already exists in database
            matching_entities = []
            entity_id = entity.identifier
            
            # Check by identifier
            if entity_id in self.entity_db.entities_db.entities:
                matching_entities.append(self.entity_db.entities_db.entities[entity_id])
            
            # Check by aliases
            for db_entity in self.entity_db.entities_db.entities.values():
                if entity_id in db_entity.aliases:
                    matching_entities.append(db_entity)
            
            # If matching entities found, add to existing entities
            if matching_entities:
                for match in matching_entities:
                    existing_entities.append(match)
        
        # Prepare messages for entity upsert
        upsert_messages = templates.entity.upsert.format(
            current_chapter=chapter,
            story_metadata=self.story_metadata,
            summary_so_far=self.current_state.summary_so_far,
            recent_summaries=self.current_state.recent_chap_summaries,
            chapter_summary=self.current_state.chapter_summary,
            entity_batch=entity_batch,
            existing_entities=existing_entities if existing_entities else None,
        )
        
        # Create config from pipeline config
        config = GenerationConfig(
            temperature=self.config.entity_upsert_config.temperature,
            model=self.config.entity_upsert_config.model,
            provider=self.config.entity_upsert_config.provider_name,
            thinking_config=self.config.entity_upsert_config.thinking_config,
            max_output_tokens=self.config.entity_upsert_config.max_output_tokens,
            response_schema=UpsertEntitiesOutSchema
        )
        
        # Use session to generate
        async with LLMSession.session_scope() as session:
            async for chunk in session.generate_stream(
                messages=upsert_messages,
                provider_name=self.config.entity_upsert_config.provider_name,
                model=self.config.entity_upsert_config.model,
                config=config
            ):
                yield chunk
        
        if chunk:
            if chunk.status == StreamStatus.COMPLETE:
                self.current_state.upsert_entities = UpsertEntitiesOutSchema.model_validate_json(
                    chunk.accumulated_text
                )
                self.entity_db.upsert(self.current_state.upsert_entities.entities)
            elif chunk.status == StreamStatus.ERROR:
                raise Exception(chunk.error)
 
    
    async def generate_wiki(self, chapter: Chapter) -> AsyncGenerator[StreamChunk, None]:
        """Generate comprehensive wiki document"""
        from shuscribe.services.llm.prompts import templates
        
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
        config = GenerationConfig(
            temperature=self.config.wiki_generation_config.temperature,
            model=self.config.wiki_generation_config.model,
            provider=self.config.wiki_generation_config.provider_name,
            thinking_config=self.config.wiki_generation_config.thinking_config,
            max_output_tokens=self.config.wiki_generation_config.max_output_tokens
        )
        
        # Use session to generate
        async with LLMSession.session_scope() as session:
            async for chunk in session.generate_stream(
                messages=wiki_messages,
                provider_name=self.config.wiki_generation_config.provider_name,
                model=self.config.wiki_generation_config.model,
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
            with open(out_dir / "chapter_summary.json", "w") as f:
                f.write(self.current_state.chapter_summary.model_dump_json(indent=2))
                
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
            with open(out_dir / "comprehensive_wiki.json", "w") as f:
                f.write(self.current_state.summary_so_far.model_dump_json(indent=2))
                
        # Save entity database
        with open(out_dir / "entity_db.json", "w") as f:
            f.write(self.entity_db.entities_db.model_dump_json(indent=2))