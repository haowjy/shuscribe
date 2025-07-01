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
from uuid import UUID, uuid4

from src.services.llm.llm_service import LLMService
from src.schemas.llm.models import LLMMessage, LLMResponse, ThinkingEffort
from src.schemas.wikigen.arc import ArcAnalysisResult, Arc
from src.database.models.story import FullStoryBase as Story
from src.prompts import prompt_manager
from src.agents.base_agent import BaseAgent, WindowProcessingResult
from src.utils import clean_json_from_llm_response

import logging
logger = logging.getLogger(__name__)


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
        default_model: str = "gemini-2.5-flash-lite-preview-06-17",
        temperature: float = 0.7,
        max_tokens: int = 16000,
        thinking: Optional[ThinkingEffort] = None
    ):
        """
        Initializes agent with LLM service and default model.
        
        Args:
            llm_service: LLM service for making analysis calls
            default_provider: Default LLM provider for arc analysis
            default_model: Default model optimized for story structure analysis and prediction
            temperature: Temperature for LLM calls (low for consistent analysis)
            max_tokens: Maximum tokens for LLM responses
            thinking: Thinking level for story analysis (default: MEDIUM for balanced reasoning)
        """
        super().__init__(
            llm_service=llm_service,
            default_provider=default_provider,
            default_model=default_model,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking=thinking
        )
        
        # State management for window processing
        self._window_results: List[WindowProcessingResult] = []
        self._current_analysis_id: Optional[str] = None
    
    def _reset_analysis_state(self) -> None:
        """Reset internal state for a new analysis."""
        self._window_results.clear()
        self._current_analysis_id = str(uuid4())
        logger.info(f"🔄 Starting new analysis: {self._current_analysis_id}")
    
    def get_window_results(self) -> List[WindowProcessingResult]:
        """Get all window processing results from the current analysis."""
        return self._window_results.copy()
    
    def get_final_result(self) -> ArcAnalysisResult:
        """
        Merge all chunk processing results into a final ArcAnalysisResult.
        
        Returns:
            Aggregated ArcAnalysisResult with all arcs from all chunks
            
        Raises:
            ValueError: If no chunks were processed or parsing failed
        """
        if not self._window_results:
            raise ValueError("No windows have been processed. Run analyze_story_streaming() first.")
        
        # Check for any processing errors
        errors = [r for r in self._window_results if r.error]
        if errors:
            error_details = "; ".join(f"Window {r.window_number}: {r.error}" for r in errors)
            raise ValueError(f"Window processing errors: {error_details}")
        
        # Collect all successfully parsed results
        parsed_results = [cast(ArcAnalysisResult, r.parsed_result) for r in self._window_results if r.parsed_result]
        if not parsed_results:
            raise ValueError("No chunks were successfully parsed.")
        
        # Merge arcs from all chunks
        all_arcs: List[Arc] = []
        for i, chunk_result in enumerate(parsed_results):
            chunk_arcs = chunk_result.arcs
            
            if i == 0:
                # First chunk: add all arcs
                all_arcs.extend(chunk_arcs)
                logger.info(f"   ➕ Chunk 1: Added {len(chunk_arcs)} arcs")
            else:
                # Subsequent chunks: handle incomplete arc merging
                prev_chunk_arcs = all_arcs
                if prev_chunk_arcs and chunk_arcs:
                    last_arc = prev_chunk_arcs[-1]
                    first_new_arc = chunk_arcs[0]
                    
                    # Check if the first new arc continues the last incomplete arc
                    if not last_arc.is_finalized and last_arc.id == first_new_arc.id:
                        # Replace the incomplete arc with the updated version
                        all_arcs[-1] = first_new_arc
                        all_arcs.extend(chunk_arcs[1:])  # Add remaining new arcs
                        logger.info(f"   🔗 Chunk {i+1}: Merged continuing arc + {len(chunk_arcs)-1} new arcs")
                    else:
                        # All arcs are new
                        all_arcs.extend(chunk_arcs)
                        logger.info(f"   ➕ Chunk {i+1}: Added {len(chunk_arcs)} new arcs")
                else:
                    # Handle edge case where one side is empty
                    all_arcs.extend(chunk_arcs)
                    logger.info(f"   ➕ Chunk {i+1}: Added {len(chunk_arcs)} arcs (edge case)")
        
        # Use metadata from the last chunk (most complete)
        last_result = parsed_results[-1]
        final_metadata = last_result.model_dump(exclude={'arcs'})
        
        final_result = ArcAnalysisResult(
            arcs=all_arcs,
            **final_metadata
        )
        
        logger.info(f"🎯 Final result: {len(final_result.arcs)} total arcs merged from {len(parsed_results)} chunks")
        return final_result
    
    async def analyze_story(
        self,
        story: Story,
        user_id: UUID,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> ArcAnalysisResult:
        """
        Main analysis method that splits story into arcs with growth-aware planning.
        
        This method processes the story by streaming through chunks to accumulate
        state, then merges all results into a final ArcAnalysisResult.
        
        Args:
            story: Story object containing all story data
            user_id: UUID of the user making the request
            api_key: Optional API key for direct usage
            provider: Optional LLM provider override
            model: Optional LLM model override
            
        Returns:
            A single ArcAnalysisResult object containing all arcs for the entire story.
        """
        # Stream through all chunks to accumulate state (don't yield to caller)
        async for _ in self.analyze_story_streaming(
            story=story,
            user_id=user_id,
            api_key=api_key,
            provider=provider,
            model=model
        ):
            pass  # Just consume the stream to accumulate internal state
        
        # Return the final merged result
        return self.get_final_result()

    async def analyze_story_streaming(
        self,
        story: Story,
        user_id: UUID,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> AsyncIterator[LLMResponse]:
        """
        Streaming version of story analysis that yields raw LLM responses while managing internal state.
        
        This method processes the story in token-aware chunks and yields all LLM responses
        as they arrive. Internal state is accumulated for later retrieval via get_final_result().
        
        Args:
            story: Story object containing all story data
            user_id: UUID of the user making the request
            api_key: Optional API key for direct usage
            provider: Optional LLM provider override
            model: Optional LLM model override
            
        Yields:
            Raw LLLResponse chunks as they arrive from the LLM, with proper chunk type labels.
            Internal state is accumulated for later merging.
        """
        # Reset state for new analysis
        self._reset_analysis_state()
        
        # Setup and Configuration
        story_title = story.metadata.title
        total_chapters = story.total_chapters
        genre = ", ".join(story.metadata.genres) if story.metadata.genres else None
        
        # Calculate chunk token limit based on model's input context window
        chunk_token_limit = self._calculate_chunk_token_limit(provider, model)

        is_short_story = story.is_short_story
        
        logger.info(f"🔍 ArcSplitter Analysis Starting:")
        logger.info(f"   📖 Story: {story_title}")
        logger.info(f"   📊 Chapters: {total_chapters}, Words: {story.word_count}")
        logger.info(f"   🧮 Total tokens: {story.total_tokens}, Chunk limit: {chunk_token_limit}")
        logger.info(f"   📏 Short story: {is_short_story}")

        # Process chunks using story's efficient chunking
        previous_arcs_json: Optional[str] = None
        last_processed_chapter = 0

        for chunk_chapters, story_content_chunk, actual_chunk_tokens in story.get_content_chunks(chunk_token_limit):
            # Create window processing result
            window_number = len(self._window_results) + 1
            chunk_start_chapter = chunk_chapters[0].chapter_number
            chunk_end_chapter = chunk_chapters[-1].chapter_number
            is_final_chunk = (chunk_end_chapter == total_chapters)
            
            window_result = WindowProcessingResult(
                window_number=window_number,
                start_chapter=chunk_start_chapter,
                end_chapter=chunk_end_chapter,
                is_final_window=is_final_chunk
            )
            self._window_results.append(window_result)
            
            logger.info(f"🔄 Processing window {window_number}: chapters {chunk_start_chapter}-{chunk_end_chapter}")
            logger.info(f"   🧮 Chunk tokens: {actual_chunk_tokens}, Final: {is_final_chunk}")

            # Render prompts for the current chunk
            messages = self._load_and_render_prompts_for_chunk(
                story_title=story_title,
                story_content_chunk=story_content_chunk,
                total_chapters=total_chapters,
                is_short_story=is_short_story,
                genre=genre,
                chunk_start_chapter=chunk_start_chapter,
                chunk_end_chapter=chunk_end_chapter,
                is_final_chunk=is_final_chunk,
                previous_arcs_json=previous_arcs_json,
                last_processed_chapter=last_processed_chapter
            )

            # Make the LLM call for the window
            logger.info(f"   🤖 Making LLM call for window {window_number}...")
            try:
                response_stream = await self._make_llm_call(
                    messages=messages,
                    user_id=user_id,
                    api_key=api_key,
                    provider=provider,
                    model=model,
                    stream=True,
                    response_format=ArcAnalysisResult
                )
                
                # Process the streaming response
                stream = cast(AsyncIterator[LLMResponse], response_stream)
                chunk_stream_count = 0
                
                async for llm_chunk in stream:
                    chunk_stream_count += 1
                    
                    # Add metadata to help with debugging
                    llm_chunk.metadata = llm_chunk.metadata or {}
                    llm_chunk.metadata.update({
                        "analysis_id": self._current_analysis_id,
                        "window_number": window_number,
                        "chapters": f"{chunk_start_chapter}-{chunk_end_chapter}",
                        "is_final_chunk": is_final_chunk
                    })
                    
                    # Accumulate content in window result
                    window_result.raw_content.add_chunk(llm_chunk)
                    
                    # Yield the raw LLM response
                    yield llm_chunk
                
                logger.info(f"   📡 Window {window_number}: {chunk_stream_count} streaming responses")
                
                # Parse the accumulated content for this window
                content_to_parse = window_result.raw_content.content + window_result.raw_content.unknown
                if content_to_parse.strip():
                    try:
                        # Clean the JSON from potential markdown formatting
                        cleaned_json = clean_json_from_llm_response(content_to_parse)
                        parsed_result = ArcAnalysisResult.model_validate_json(cleaned_json)
                        window_result.parsed_result = parsed_result
                        logger.info(f"   ✅ Window {window_number}: Parsed {len(parsed_result.arcs)} arcs")
                        
                        # Update context for next iteration
                        previous_arcs_json = parsed_result.model_dump_json()
                        if parsed_result.arcs:
                            last_processed_chapter = parsed_result.arcs[-1].end_chapter
                            
                    except Exception as e:
                        error_msg = f"Failed to parse window {window_number}: {e}"
                        window_result.error = error_msg
                        logger.error(f"   ❌ {error_msg}")
                else:
                    error_msg = f"Window {window_number} produced no parseable content"
                    window_result.error = error_msg
                    logger.error(f"   ❌ {error_msg}")
                    
            except Exception as e:
                error_msg = f"LLM call failed for window {window_number}: {e}"
                window_result.error = error_msg
                logger.error(f"   ❌ {error_msg}")
        
        logger.info(f"✅ Streaming completed: {len(self._window_results)} windows processed")
    
    def _load_and_render_prompts_for_chunk(
        self,
        story_title: str,
        story_content_chunk: str,
        total_chapters: int,
        is_short_story: bool,
        genre: Optional[str],
        chunk_start_chapter: int,
        chunk_end_chapter: int,
        is_final_chunk: bool,
        previous_arcs_json: Optional[str],
        last_processed_chapter: int
    ) -> List[LLMMessage]:
        """Loads and renders arc splitting prompts using chunk-specific context."""
        splitting_prompts = prompt_manager.get_group("wikigen.arc_splitting")
        message_templates = splitting_prompts.get("messages")
        
        render_kwargs = {
            "story_title": story_title,
            "story_content_chunk": story_content_chunk,
            "total_chapters": total_chapters,
            "is_short_story": is_short_story,
            "genre": genre or "Unknown",
            "chunk_start_chapter": chunk_start_chapter,
            "chunk_end_chapter": chunk_end_chapter,
            "is_final_chunk": is_final_chunk,
            "previous_arcs_json": previous_arcs_json,
            "last_processed_chapter": last_processed_chapter
        }
        
        final_messages = []
        for template in message_templates:
            rendered_content = splitting_prompts.render(template['content'], **render_kwargs)
            final_messages.append(LLMMessage(role=template['role'], content=rendered_content))
        
        return final_messages

    def _calculate_chunk_token_limit(
        self, 
        provider: Optional[str] = None, 
        model: Optional[str] = None,
        prompt_overhead_tokens: int = 5000
    ) -> int:
        """
        Calculate the maximum token limit for story chunks based on the model's input context window.
        
        Args:
            provider: LLM provider override (uses default if None)
            model: LLM model override (uses default if None)  
            prompt_overhead_tokens: Tokens to reserve for prompt overhead
            
        Returns:
            Maximum tokens available for story content in each chunk
            
        Raises:
            ValueError: If the model is not found in the catalog
        """
        final_provider, final_model = self._get_model_params(provider, model)
        
        # Get the model's actual input context window (not output tokens!)
        from src.core.llm.catalog import get_hosted_model_instance
        model_instance = get_hosted_model_instance(final_provider, final_model)
        if not model_instance:
            raise ValueError(f"Unknown model: {final_provider}/{final_model}")
        
        # Get the input token limit, with fallback to reasonable default
        input_token_limit = model_instance.input_token_limit or 128000  # Default to 128k if not specified
        
        # Reserve space for prompt overhead, use remaining for story content
        chunk_token_limit = input_token_limit - prompt_overhead_tokens
        
        # Sanity check: ensure we have reasonable chunk size
        if chunk_token_limit < 10000:
            logger.warning(f"⚠️  Very small chunk limit: {chunk_token_limit:,} tokens. This might cause issues.")
            chunk_token_limit = max(chunk_token_limit, 5000)  # Minimum viable chunk size
        
        logger.info(f"📐 Model Context Window: {input_token_limit:,} tokens")
        logger.info(f"📐 Chunk Limit: {chunk_token_limit:,} tokens (after {prompt_overhead_tokens:,} overhead)")
        
        return chunk_token_limit
    
    # Implementation of BaseAgent's abstract method
    async def execute(self, *args, **kwargs):
        """
        Execute the arc splitting analysis.
        
        This is a convenience method that calls analyze_story with the provided arguments.
        """
        return await self.analyze_story(*args, **kwargs) 