# shuscribe/services/llm/prompts/templates/entity/__init__.py

from typing import List, Optional
from shuscribe.schemas.wikigen.entity import EntityType
from shuscribe.schemas.wikigen.summary import ChapterSummary
from shuscribe.services.llm.prompts.base_template import PromptTemplate
from shuscribe.schemas.pipeline import Chapter, StoryMetadata
from shuscribe.services.llm.prompts.base_template import Message

class ExtractTemplate(PromptTemplate):
    def __init__(self):
        super().__init__(
            "extract", 
            "shuscribe.services.llm.prompts.templates.entity"
        )

    def format(
        self,
        current_chapter: Chapter,
        story_metadata: Optional[StoryMetadata] = None,
        summary_so_far: Optional[str] = None, # TODO: make the promptable class
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
        
        entity_types_prompt = ""
        for i, entity in enumerate(EntityType):
            entity_types_prompt += (
                f"\t{i+1}. {entity.value}s: {entity.description}\n"
            )
        
        # Call the underlying template's format method
        return super().format(
            current_chapter=current_chapter.to_prompt(),
            story_metadata=story_metadata.to_prompt() if story_metadata else None,
            summary_so_far=summary_so_far,
            recent_summaries=recent_summaries_prompt,
            chapter_summary=chapter_summary.to_prompt() if chapter_summary else None,
            entity_types=entity_types_prompt,
        )

extract = ExtractTemplate()
