# shuscribe/services/llm/prompts/templates/story/__init__.py

from typing import List, Optional
from shuscribe.schemas.wikigen.entity import UpsertEntitiesOutSchema
from shuscribe.schemas.wikigen.summary import ChapterSummary
from shuscribe.services.llm.prompts.base_template import PromptTemplate
from shuscribe.schemas.pipeline import Chapter, StoryMetadata
from shuscribe.services.llm.prompts.base_template import Message

class ComprehensiveSummaryTemplate(PromptTemplate):
    """Wrapper around a PromptTemplate that allows for custom formatting logic"""
    
    def __init__(self):
        # Store the template instance directly, not just its config
        super().__init__(
            "comprehensive", 
            "shuscribe.services.llm.prompts.templates.story"
        )
        
    def format(
        self,
        current_chapter: Chapter,
        chapter_summary: ChapterSummary,
        key_entities: UpsertEntitiesOutSchema, # TODO: temporarily use the UpsertEntitiesOutSchema schema - update to a the database Entity schema later
        
        story_metadata: Optional[StoryMetadata] = None,
        summary_so_far: Optional[str] = None, # TODO: make the promptable class
        recent_summaries: Optional[List[ChapterSummary]] = None,
    ) -> list[Message]:
        """Format the prompt template with the given context
        Args:
            current_chapter (Chapter): The current chapter to summarize
            ```
            ## Latest Chapter
            {{ current_chapter }}
            ```
            
            chapter_summary (ChapterSummary): The summary of the current chapter
            ```
            ## Latest Chapter Summary
            {{ chapter_summary }}
            ```
            
            key_entities (List[UpsertEntitiesOutSchema]): The key entities in the latest chapter
            ```
            # Key Entities in Latest Chapter
            {{ key_entities }}
            ```
            
            story_metadata (Optional[StoryMetadata], optional): The story metadata. Defaults to None.
            ```
            # Story Metadata
            {{ story_metadata }}
            ```
            
            summary_so_far (Optional[str], optional): The summary so far. Defaults to None.
            ```
            # Previous Comprehensive Summary
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
        if recent_summaries:
            recent_summaries_prompt = "\n".join([summary.to_prompt() for summary in recent_summaries])
        else:
            recent_summaries_prompt = None
                    
        # Call the underlying template's format method
        return super().format(
            current_chapter=current_chapter.to_prompt(),
            chapter_summary=chapter_summary.to_prompt(),
            key_entities=key_entities.model_dump_json(indent=2),
            
            story_metadata=story_metadata.to_prompt() if story_metadata else None,
            summary_so_far=summary_so_far,
            recent_summaries=recent_summaries_prompt,
        )
        
comprehensive_summary = ComprehensiveSummaryTemplate()