# shuscribe/services/llm/prompts/templates/chapter/__init__.py

from typing import List, Optional
from shuscribe.schemas.wikigen.wiki import WikiPage
from shuscribe.schemas.wikigen.summary import ChapterSummary
from shuscribe.services.llm.prompts.base_template import PromptTemplate
from shuscribe.schemas.pipeline import Chapter, StoryMetadata
from shuscribe.services.llm.prompts.base_template import Message

class SummaryTemplate(PromptTemplate):
    """Wrapper around a PromptTemplate that allows for custom formatting logic"""
    
    def __init__(self, *args, **kwargs):
        # Store the template instance directly, not just its config
        super().__init__(
            "summary", 
            "shuscribe.services.llm.prompts.templates.chapter"
        )
        
    def format(
        self,
        current_chapter: Chapter,
        story_metadata: Optional[StoryMetadata] = None,
        summary_so_far: Optional[WikiPage] = None, # TODO: make the promptable class
        recent_summaries: Optional[List[ChapterSummary]] = None,
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
            summary_so_far (Optional[WikiPage], optional): The summary so far. Defaults to None.
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
        if recent_summaries:
            recent_summaries_prompt = "\n".join([summary.to_prompt() for summary in recent_summaries])
        else:
            recent_summaries_prompt = None
        
        # Call the underlying template's format method
        return super().format(
            current_chapter=current_chapter.to_prompt(),
            story_metadata=story_metadata.to_prompt() if story_metadata else None,
            summary_so_far=summary_so_far.to_prompt() if summary_so_far else None,
            recent_summaries=recent_summaries_prompt,
        )
        
summary = SummaryTemplate()