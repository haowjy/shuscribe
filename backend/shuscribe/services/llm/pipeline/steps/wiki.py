# shuscribe/services/llm/pipeline/steps/wiki.py

from typing import Dict, List, Any, Optional, Union

from shuscribe.services.llm.pipeline.base import PipelineContext
from shuscribe.services.llm.pipeline.base_steps import EnhancedPipelineStep, StepResult
from shuscribe.services.llm.pipeline.conditions import ContentMatchStoppingCondition, StoppingStatus
from shuscribe.schemas.llm import Message, GenerationConfig
from shuscribe.services.llm.session import LLMSession
from shuscribe.services.llm.prompts import PromptManager
from shuscribe.schemas.pipeline import (
    Chapter, ChapterSummary, Entity, WikiArticle, ProcessingConfig, 
    EntitySignificanceLevel, WikiArticleType
)


class WikiArticleStep(EnhancedPipelineStep):
    """Generates wiki articles for entities or main story content"""
    
    def __init__(self, llm_session: LLMSession, article_type: WikiArticleType):
        """
        Initialize wiki article step
        
        Args:
            llm_session: Session for LLM API calls
            article_type: Type of wiki article to generate
        """
        # Define a stopping condition for all wiki articles
        stopping_condition = ContentMatchStoppingCondition(
            patterns=[
                r"#\s+.+",          # At least one heading
                r"\[\[.+?\]\]",      # At least one wiki link
                r".{300,}"           # At least 300 characters
            ],
            require_all=True,
            max_retries=2
        )
        
        name = f"{article_type.value}_wiki_article"
        
        super().__init__(
            name=name,
            stopping_condition=stopping_condition
        )
        
        self.llm_session: LLMSession = llm_session
        self.article_type: WikiArticleType = article_type
    
    async def execute(self, context: PipelineContext) -> Union[Dict[str, WikiArticle], WikiArticle, StepResult]:
        """
        Execute wiki article generation based on type
        
        Args:
            context: Pipeline context with required data
            
        Returns:
            For MAIN: Single WikiArticle
            For entity types: Dictionary of entity_id -> WikiArticle
            Or StepResult if an error occurs
        """
        # Get required data
        config: Optional[ProcessingConfig] = context.data.get_typed(ProcessingConfig)
        chapter: Optional[Chapter] = context.data.get_typed(Chapter)
        entities: List[Entity] = context.data.get("entity_update_result", [])
        chapter_summary: Optional[ChapterSummary] = context.data.get_typed(ChapterSummary)
        
        # Validation checks
        if not config or not chapter:
            return StepResult(
                value=None,
                status=StoppingStatus.ERROR,
                error=ValueError("Missing required configuration or chapter data")
            )
        
        if not entities:
            return StepResult(
                value=None,
                status=StoppingStatus.ERROR,
                error=ValueError("No updated entities found")
            )
        
        if not chapter_summary:
            return StepResult(
                value=None,
                status=StoppingStatus.ERROR,
                error=ValueError("No chapter summary found")
            )
        
        # Get existing wiki entries if available
        existing_wikis: Dict[str, Dict[str, Any]] = context.data.get("existing_wiki_entries", {})
        
        # Create prompt manager
        prompt_manager: PromptManager = PromptManager()
        
        # Process based on article type
        if self.article_type == WikiArticleType.MAIN:
            return await self._generate_main_article(
                config=config,
                chapter=chapter,
                entities=entities,
                chapter_summary=chapter_summary,
                existing_wikis=existing_wikis,
                prompt_manager=prompt_manager
            )
        else:
            return await self._generate_entity_articles(
                config=config,
                chapter=chapter,
                entities=entities,
                existing_wikis=existing_wikis,
                prompt_manager=prompt_manager
            )
    
    async def _generate_main_article(
        self, 
        config: ProcessingConfig,
        chapter: Chapter,
        entities: List[Entity],
        chapter_summary: ChapterSummary,
        existing_wikis: Dict[str, Dict[str, Any]],
        prompt_manager: PromptManager
    ) -> WikiArticle:
        """
        Generate the main wiki article
        
        Args:
            config: Processing configuration
            chapter: Current chapter
            entities: List of entities
            chapter_summary: Chapter summary
            existing_wikis: Existing wiki articles
            prompt_manager: Prompt template manager
            
        Returns:
            Generated WikiArticle
        """
        # Get previous content if available
        previous_content: str = existing_wikis.get("main", {}).get("content", "")
        
        # Filter entities by significance
        central_entities: List[Dict[str, Any]] = []
        major_entities: List[Dict[str, Any]] = []
        for entity in entities:
            if entity.significance == EntitySignificanceLevel.CENTRAL:
                central_entities.append(entity.dict())
            elif entity.significance == EntitySignificanceLevel.MAJOR:
                major_entities.append(entity.dict())
        
        # Create messages
        messages: List[Union[Message, str]] = prompt_manager.wiki.main_article(
            chapter_summary=chapter_summary.summary,
            central_entities=central_entities,
            major_entities=major_entities,
            chapter_id=chapter.id,
            previous_content=previous_content
        )
        
        # Generate the wiki article
        response = await self.llm_session.generate(
            provider_name=config.provider_name,
            model=config.model,
            messages=messages,
            config=GenerationConfig(temperature=0.7)
        )
        
        # Create article
        return WikiArticle(
            entity_id=None,  # Main article has no entity ID
            title="Main Story",
            content=response.text,
            related_entities=[e.id for e in entities if e.significance in 
                            (EntitySignificanceLevel.CENTRAL, EntitySignificanceLevel.MAJOR)],
            last_updated_chapter=chapter.id
        )
    
    async def _generate_entity_articles(
        self,
        config: ProcessingConfig,
        chapter: Chapter,
        entities: List[Entity],
        existing_wikis: Dict[str, Dict[str, Any]],
        prompt_manager: PromptManager
    ) -> Dict[str, WikiArticle]:
        """
        Generate wiki articles for entities of the specified type
        
        Args:
            config: Processing configuration
            chapter: Current chapter
            entities: List of entities
            existing_wikis: Existing wiki articles
            prompt_manager: Prompt template manager
            
        Returns:
            Dictionary mapping entity ID to wiki article
        """
        entity_type: str = self.article_type.value
        
        # Filter entities by type
        type_entities: List[Entity] = [e for e in entities if e.type == entity_type]
        
        # Filter by significance threshold
        threshold: EntitySignificanceLevel = getattr(
            EntitySignificanceLevel, 
            config.generate_entity_articles_threshold, 
            EntitySignificanceLevel.SUPPORTING
        )
        
        wiki_worthy_entities: List[Entity] = []
        for entity in type_entities:
            try:
                significance = EntitySignificanceLevel(entity.significance)
                if significance.to_int() >= EntitySignificanceLevel(threshold).to_int():
                    wiki_worthy_entities.append(entity)
            except ValueError:
                # Skip entities with invalid significance values
                continue
        
        # No entities to process
        if not wiki_worthy_entities:
            return {}
        
        # Process each entity
        wiki_entries: Dict[str, WikiArticle] = {}
        
        for entity in wiki_worthy_entities:
            # Get previous content if available
            previous_content: str = existing_wikis.get(entity.id, {}).get("content", "")
            
            # Get the appropriate template method for this entity type
            if entity_type == "character":
                messages: List[Union[Message, str]] = prompt_manager.wiki.character_article(
                    entity=entity.model_dump(),
                    chapter_id=chapter.id,
                    chapter_excerpt=chapter.content[:1000],
                    previous_content=previous_content
                )
            else:
                # Use generic article template for other types
                messages: List[Union[Message, str]] = prompt_manager.wiki.generic_article(
                    entity=entity.model_dump(),
                    entity_type=entity_type,
                    chapter_id=chapter.id,
                    chapter_excerpt=chapter.content[:1000],
                    previous_content=previous_content
                )
            
            # Generate the article
            response = await self.llm_session.generate(
                provider_name=config.provider_name,
                model=config.model,
                messages=messages,
                config=GenerationConfig(temperature=0.7)
            )
            
            # Create wiki entry
            wiki_entries[entity.id] = WikiArticle(
                entity_id=entity.id,
                title=entity.name,
                content=response.text,
                related_entities=[rel for rel in entity.relationships.keys()],
                last_updated_chapter=chapter.id
            )
        
        return wiki_entries