# shuscribe/services/llm/prompts/templates/entity/__init__.py

import json
from typing import List, Optional, Type
from shuscribe.schemas.llm import GenerationConfig, ThinkingConfig
from shuscribe.schemas.provider import ProviderName
from shuscribe.schemas.wikigen.entity import EntitySigLvl, EntityType, ExtractEntitiesOutSchema, RelationshipType, UpsertEntitiesOutSchema
from shuscribe.schemas.wikigen.wiki import WikiPage
from shuscribe.schemas.wikigen.summary import ChapterSummary
from shuscribe.services.llm.prompts.base_template import PromptTemplate
from shuscribe.schemas.pipeline import Chapter, StoryMetadata
from shuscribe.services.llm.prompts.base_template import Message

class ExtractTemplate(PromptTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(
            "extract", 
            "shuscribe.services.llm.prompts.templates.entity"
        )
        self.default_config = GenerationConfig(
            # provider=ProviderName.GEMINI,
            # model="gemini-2.0-flash-thinking-exp", # TODO: move off of thinking-exp later
            # provider=ProviderName.ANTHROPIC,
            # model="claude-3-7-sonnet-20250219",
            provider=ProviderName.OPENAI,
            # model="o3-mini-2025-01-31",
            model="gpt-4o-mini",
            temperature=0.5,
            
            response_schema=ExtractEntitiesOutSchema,
            # thinking_config=ThinkingConfig(
            #     enabled=True,
            #     budget_tokens=1024,
            #     effort="low",
            # ),
        )
        
    def format(
        self,
        current_chapter: Chapter,
        story_metadata: Optional[StoryMetadata] = None,
        summary_so_far: Optional[WikiPage] = None, 
        recent_summaries: Optional[List[ChapterSummary]] = None,
        chapter_summary: Optional[ChapterSummary] = None,
    ) -> list[Message]:
        """Format the prompt template with the given context
        Args:
            current_chapter (Chapter): The current chapter to summarize
            ```
            ## Current Chapter
            
            {{ current_chapter }}
            ```
            story_metadata (Optional[StoryMetadata], optional): The story metadata. Defaults to None.
            ```
            # Story Metadata
            {{ story_metadata }}
            ```
            summary_so_far (Optional[str], optional): The summary so far. Defaults to None.
            ```
            # Story So Far
            {{ summary_so_far }}
            ```
            recent_summaries (Optional[List[ChapterSummary]], optional): The recent summaries. Defaults to None.
            ```
            ## Summary of Previous Chapters
            {{ recent_summaries }}
            ```
            chapter_summary (Optional[ChapterSummary], optional): The chapter summary. Defaults to None.
            ```
            ## Current Chapter Summary
            {{ chapter_summary }}
            ```
        Returns:
            list[Message]: The formatted prompt template
        """
        if recent_summaries:
            recent_summaries_prompt = "\n".join([summary.to_prompt() for summary in recent_summaries])
        else:
            recent_summaries_prompt = None
        
        entity_types_prompt = EntityType.to_prompt_reference()
        entity_significance_levels_prompt = EntitySigLvl.to_prompt_reference()
        # Call the underlying template's format method
        return super().format(
            current_chapter=current_chapter.to_prompt(),
            
            story_metadata=story_metadata.to_prompt() if story_metadata else None,
            summary_so_far=summary_so_far.to_prompt() if summary_so_far else None,
            recent_summaries=recent_summaries_prompt,
            chapter_summary=chapter_summary.to_prompt() if chapter_summary else None,
            
            entity_types=entity_types_prompt,
            entity_significance_levels=entity_significance_levels_prompt,
        )

extract = ExtractTemplate()





class UpsertTemplate(PromptTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(
            "upsert", 
            "shuscribe.services.llm.prompts.templates.entity"
        )
        self.default_config = GenerationConfig(
            provider=ProviderName.GEMINI,
            model="gemini-2.0-flash-001", 
            temperature=0.4,
            # max_output_tokens=8192,
            # provider=ProviderName.ANTHROPIC,
            # model="claude-3-5-sonnet-20240620",
            # thinking_config=ThinkingConfig(
            #     enabled=False,
            #     budget_tokens=1024,
            #     effort="low",
            # ),
            response_schema=UpsertEntitiesOutSchema,
        )

    def format(
        self,
        current_chapter: Chapter,
        entity_batch: List[str],
        story_metadata: Optional[StoryMetadata] = None,
        chapter_summary: Optional[ChapterSummary] = None,
        existing_entities: Optional[List[dict]] = None,
        summary_so_far: Optional[str] = None,
        recent_summaries: Optional[List[ChapterSummary]] = None,
    ) -> list[Message]:
        """Format the prompt template with the given context
        Args:
            current_chapter (Chapter): The current chapter to summarize
            ```
            ## Current Chapter
            
            {{ current_chapter }}
            ```
            
            entity_batch (List[str]): The extracted entity batch.
            ```
            # Entity Batch for Processing
            The following entities have been extracted from the current chapter:
            {{ entity_batch }}
            ```
            
            story_metadata (Optional[StoryMetadata], optional): The story metadata. Defaults to None.
            ```
            # Story Metadata
            {{ story_metadata }}
            ```
            
            chapter_summary (Optional[ChapterSummary], optional): The chapter summary. Defaults to None.
            ```
            ## Current Chapter Summary
            {{ chapter_summary }}
            ```
            
            existing_entities (Optional[List[dict]], optional): The existing entities in the database (json formatted). Defaults to None.
            ```
            ## Existing Entity Database
            These entities already exist in the database and may need to be updated:
            {{ existing_entities }}
            ```
            
            summary_so_far (Optional[str], optional): The summary so far. Defaults to None.
            ```
            # Story So Far
            {{ summary_so_far }}
            ```
            
            recent_summaries (Optional[List[ChapterSummary]], optional): The recent summaries. Defaults to None.
            ```
            ## Summary of Previous Chapters
            {{ recent_summaries }}
            ```
        Returns:
            list[Message]: The formatted prompt template
        """
        
        entity_batch_prompt = "\n---\n".join([f"{entity}" for entity in entity_batch])
        entity_batch_prompt = f"```yaml\n{entity_batch_prompt}\n```"
        
        if existing_entities:
            existing_entities_prompt = json.dumps(existing_entities, indent=2)
        else:
            existing_entities_prompt = None
            
        if recent_summaries:
            recent_summaries_prompt = "\n".join([summary.to_prompt() for summary in recent_summaries])
        else:
            recent_summaries_prompt = None

        entity_types_prompt = EntityType.to_prompt_reference()
        relationship_types_prompt = RelationshipType.to_prompt_reference()
        
        # Call the underlying template's format method
        return super().format(
            current_chapter=current_chapter.to_prompt(),
            entity_batch=entity_batch_prompt,
            
            story_metadata=story_metadata.to_prompt() if story_metadata else None,
            chapter_summary=chapter_summary.to_prompt() if chapter_summary else None,
            existing_entities=existing_entities_prompt,
            summary_so_far=summary_so_far,
            recent_summaries=recent_summaries_prompt,
            
            entity_types=entity_types_prompt,
            relationship_types=relationship_types_prompt,
        )

upsert = UpsertTemplate()
