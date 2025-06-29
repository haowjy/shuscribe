# backend/src/agents/wikigen/arc_splitter_agent.py

"""
Arc Splitter Agent

Analyzes story structure to determine optimal narrative arc boundaries for wiki generation.
First agent in the workflow that establishes processing units with growth-aware planning.

Key Responsibilities:
- Analyzes narrative structure, pacing, and future potential
- Predicts likely story developments and growth patterns
- Identifies natural story breaks with consideration for future expansion
- Considers token count constraints while prioritizing fewer, larger arcs
- Handles edge cases (very short/long stories) with growth-adaptive approach
- Uses LLM to understand narrative flow, structure, and predict future developments

Key Features:
- Growth-aware arc sizing (assumes 2-5x expansion)
- Story prediction and development analysis
- Natural breakpoint identification with future-proofing
- Strong bias toward consolidation over splitting
- Fallback for short stories with single comprehensive arc
- Structured XML output format with prediction fields
"""

from typing import List, Optional, cast, AsyncIterator
from uuid import UUID

from src.services.llm.llm_service import LLMService
from src.schemas.llm.models import LLMMessage, LLMResponse
from src.schemas.wikigen.arc import ArcAnalysisResult, Arc, StoryStats, get_arc_analysis_schema
from src.prompts import prompt_manager
from src.agents.base_agent import BaseAgent


class ArcSplitterAgent(BaseAgent):
    """
    Analyzes story structure and determines optimal arc boundaries for wiki generation
    with strong emphasis on accommodating future story growth.
    
    Uses LLM analysis to identify natural narrative breaks, predict future developments,
    and ensure arcs are appropriately sized and flexible for effective wiki generation
    as stories continue to evolve and expand.
    """
    
    def __init__(
        self, 
        llm_service: LLMService,
        default_provider: str = "google",
        default_model: str = "gemini-2.0-flash-001"
    ):
        """
        Initializes agent with LLM service and default model.
        
        Args:
            llm_service: LLM service for making analysis calls
            default_provider: Default LLM provider for arc analysis
            default_model: Default model optimized for story structure analysis and prediction
        """
        super().__init__(
            llm_service=llm_service,
            default_provider=default_provider,
            default_model=default_model
        )
    
    async def analyze_story(
        self,
        story_title: str,
        story_content: str,
        total_chapters: int,
        user_id: UUID,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        genre: Optional[str] = None
    ) -> ArcAnalysisResult:
        """
        Main analysis method that splits story into arcs with growth-aware planning.
        
        Uses LLM to analyze narrative structure, predict future developments, and identify
        natural arc boundaries that can accommodate significant story expansion.
        For short stories (under 15k words), creates a single comprehensive arc.
        For longer stories, strongly prefers fewer, larger arcs with future-proofing.
        
        Process:
        1. Count words for prompt context
        2. Analyze narrative structure and predict future developments via LLM
        3. Apply growth-aware consolidation approach
        4. Return structured analysis with prediction and growth assessment
        
        Args:
            story_title: Title of the story
            story_content: Full story text content
            total_chapters: Number of chapters in story
            user_id: UUID of the user making the request
            api_key: Optional API key for direct usage
            provider: Optional LLM provider override (uses default if not provided)
            model: Optional LLM model override (uses default if not provided)
            genre: Optional story genre for context
            
        Returns:
            ArcAnalysisResult object with arc boundaries, story prediction, and growth metadata
        """
        # 1. Determine if this is a short story (bias toward single arc approach)
        word_count = len(story_content.split()) if story_content else 0
        is_short_story = word_count < 15000
        
        # 2. Load and render growth-aware prompts with short story flag
        messages = self._load_and_render_prompts(
            story_title=story_title,
            story_content=story_content,
            total_chapters=total_chapters,
            is_short_story=is_short_story,
            genre=genre
        )
        
        # 3. Make LLM call for arc analysis with structured output including predictions
        response = await self._make_llm_call(
            messages=messages,
            user_id=user_id,
            api_key=api_key,
            provider=provider,
            model=model,
            temperature=0.3,  # Low temperature for consistent analysis and predictions
            max_tokens=4000,
            stream=False,  # Non-streaming for structured output
            response_format=ArcAnalysisResult
        )
        
        # 4. Parse structured response (type cast safe since stream=False)
        llm_response = cast(LLMResponse, response)
        try:
            arc_analysis = ArcAnalysisResult.model_validate_json(llm_response.content)
        except Exception as e:
            raise ValueError(f"Failed to validate structured response: {e}")
        
        return arc_analysis
    
    async def analyze_story_streaming(
        self,
        story_title: str,
        story_content: str,
        total_chapters: int,
        user_id: UUID,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        genre: Optional[str] = None
    ) -> AsyncIterator[LLMResponse]:
        """
        Streaming version of story analysis for real-time feedback with growth planning.
        
        Streams the LLM analysis process with structured JSON output that includes
        story prediction, growth assessment, and consolidation reasoning.
        Handles both short stories (single arc) and longer stories (fewer arcs approach).
        
        Args:
            story_title: Title of the story
            story_content: Full story text content
            total_chapters: Number of chapters in story
            user_id: UUID of the user making the request
            api_key: Optional API key for direct usage
            provider: Optional LLM provider override (uses default if not provided)
            model: Optional LLM model override (uses default if not provided)
            genre: Optional story genre for context
            
        Yields:
            LLMResponse chunks as the analysis progresses (JSON format with predictions)
        """
        # 1. Determine if this is a short story (bias toward single arc approach)
        word_count = len(story_content.split()) if story_content else 0
        is_short_story = word_count < 15000
        
        # 2. Load and render growth-aware prompts with short story flag
        messages = self._load_and_render_prompts(
            story_title=story_title,
            story_content=story_content,
            total_chapters=total_chapters,
            is_short_story=is_short_story,
            genre=genre
        )
        
        # 3. Stream LLM analysis with structured output including predictions
        response = await self._make_llm_call(
            messages=messages,
            user_id=user_id,
            api_key=api_key,
            provider=provider,
            model=model,
            temperature=0.3,
            max_tokens=4000,
            stream=True,  # Enable streaming
            response_format=ArcAnalysisResult  # Include for parseable JSON output with predictions
        )
        
        # Type cast safe since stream=True
        response_stream = cast(AsyncIterator[LLMResponse], response)
        async for chunk in response_stream:
            yield chunk
    
    def _estimate_token_count(self, text: str) -> int:
        """
        Estimates token count for content using word-based approximation.
        
        Since tiktoken is not available, uses a reasonable approximation:
        - Split by whitespace to get words
        - Multiply by 1.3 to account for subword tokenization
        - Add extra for formatting and special tokens
        
        Args:
            text: Text content to analyze
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        # Basic word count
        words = len(text.split())
        
        # Approximate token count (words * 1.3 for subword tokenization)
        estimated_tokens = int(words * 1.3)
        
        # Add overhead for formatting, chapter headers, etc.
        overhead = min(estimated_tokens * 0.1, 1000)  # Max 1000 token overhead
        
        return int(estimated_tokens + overhead)
    
    def _validate_arc_boundaries(self, arcs: List, total_chapters: int) -> bool:
        """
        Validates that arc boundaries make sense.
        
        Checks:
        - No gaps or overlaps in chapter coverage
        - Minimum/maximum arc sizes are reasonable
        - All chapters are covered
        
        Args:
            arcs: List of Arc objects to validate
            total_chapters: Total number of chapters in story
            
        Returns:
            True if boundaries are valid, False otherwise
        """
        if not arcs:
            return False
        
        # Sort arcs by start chapter
        sorted_arcs = sorted(arcs, key=lambda a: a.start_chapter)
        
        # Check that first arc starts at chapter 1
        if sorted_arcs[0].start_chapter != 1:
            return False
        
        # Check that last arc ends at total_chapters
        if sorted_arcs[-1].end_chapter != total_chapters:
            return False
        
        # Check for gaps or overlaps
        for i in range(len(sorted_arcs) - 1):
            current_arc = sorted_arcs[i]
            next_arc = sorted_arcs[i + 1]
            
            # Check for overlaps (current end >= next start)
            if current_arc.end_chapter >= next_arc.start_chapter:
                return False
            
            # Check for gaps (current end + 1 != next start)
            if current_arc.end_chapter + 1 != next_arc.start_chapter:
                return False
        
        return True
    

    
    def _load_and_render_prompts(
        self, 
        story_title: str, 
        story_content: str, 
        total_chapters: int,
        is_short_story: bool,
        genre: Optional[str] = None
    ) -> List[LLMMessage]:
        """
        Loads and renders arc splitting prompts from TOML configuration.
        
        Uses the wikigen.arc_splitting prompt group with story context.
        
        Args:
            story_title: Title for prompt context
            story_content: Content for analysis
            total_chapters: Chapter count for context
            is_short_story: Whether this is a short story (< 15k words)
            genre: Optional genre for context
            
        Returns:
            List of rendered LLMMessage objects ready for API call
        """
        # Load prompt group
        splitting_prompts = prompt_manager.get_group("wikigen.arc_splitting")
        message_templates = splitting_prompts.get("messages")
        
        # Prepare render context
        render_kwargs = {
            "story_title": story_title,
            "story_content": story_content,
            "total_chapters": total_chapters,
            "is_short_story": is_short_story,
            "genre": genre or "Unknown"
        }
        
        # Render and build messages
        final_messages = []
        for template in message_templates:
            rendered_content = splitting_prompts.render(
                template['content'], 
                **render_kwargs
            )
            final_messages.append(LLMMessage(
                role=template['role'], 
                content=rendered_content
            ))
        
        return final_messages
    

    
    # Implementation of BaseAgent's abstract method
    async def execute(self, *args, **kwargs):
        """
        Execute the arc splitting analysis.
        
        This is a convenience method that calls analyze_story with the provided arguments.
        """
        return await self.analyze_story(*args, **kwargs) 