# # shuscribe/services/llm/pipeline/steps/chapter.py

# from typing import List, Dict, Any, Optional, Sequence

# from shuscribe.services.llm.pipeline.base import PipelineContext
# from shuscribe.services.llm.pipeline.base_steps import EnhancedPipelineStep, StepResult
# from shuscribe.services.llm.pipeline.conditions import ContentMatchStoppingCondition, StoppingStatus
# from shuscribe.schemas.llm import Message, MessageRole, GenerationConfig
# from shuscribe.services.llm.session import LLMSession
# from shuscribe.schemas.pipeline import Chapter, ChapterSummary, ProcessingConfig


# class ChapterSummaryStep(EnhancedPipelineStep):
#     """Step to generate a summary of a chapter"""
    
#     def __init__(self, llm_session: LLMSession):
#         """Initialize chapter summary step"""
#         # Create a stopping condition that checks for key summary elements
#         stopping_condition = ContentMatchStoppingCondition(
#             patterns=[
#                 r"(?i)^.*summary.*:?",   # Look for a heading or intro that includes "summary"
#                 r"\b(in\s+this\s+chapter|the\s+chapter\s+begins|the\s+chapter\s+ends)\b",  # Common summary phrases
#             ],
#             require_all=False,  # Any of these patterns is good
#             min_length=200,     # Minimum reasonable summary length
#             max_retries=2       # Try up to 3 times
#         )
        
#         super().__init__(
#             name="chapter_summary",
#             stopping_condition=stopping_condition
#         )
#         self.llm_session = llm_session
    
#     async def execute(self, context: PipelineContext) -> Any:
#         """Execute chapter summary generation"""
#         # Get required data from context
#         config = context.data.get_typed(ProcessingConfig)
#         current_chapter = context.data.get_typed(Chapter)
        
#         if not config or not current_chapter:
#             return StepResult(
#                 value=None,
#                 status=StoppingStatus.ERROR,
#                 error=ValueError("Missing required configuration or chapter data")
#             )
        
#         # Get previous summaries if available
#         previous_summaries = []
#         if context.data.has("previous_chapter_summaries"):
#             previous_summaries = context.data.get("previous_chapter_summaries", [])
        
#         # Format the prompt
#         previous_context = ""
#         if previous_summaries:
#             # Format previous summaries for context
#             previous_context = "Previous chapter summaries:\n\n"
#             for i, summary in enumerate(previous_summaries):
#                 previous_context += f"Chapter {i+1}: {summary.summary}\n\n"
        
                
#         # Create the summary prompt
#         from shuscribe.services.llm.prompts.manager import PromptManager
#         prompt_manager = PromptManager()
#         messages = prompt_manager.chapter.summary(
#             current_chapter=current_chapter, 
#             # last_chapter=previous_summaries[-1].summary if previous_summaries else None,
#             # story_metadata=context.data.get_typed(StoryMetadata).to_string(),
#             # reader_context=context.data.get_typed(ReaderContext).to_string(),
#             # focus_genre=context.data.get_typed(StoryMetadata).genre
#         )
        
#         # Generate the summary
#         response = await self.llm_session.generate(
#             provider_name=config.provider_name,
#             model=config.model,
#             messages=messages,
#             config=GenerationConfig(temperature=0.3)  # Lower temperature for more focused summaries
#         )
        
#         # Create and return the chapter summary
#         return ChapterSummary(
#             chapter_id=current_chapter.id,
#             summary=response.text
#         )