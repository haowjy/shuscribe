# backend/src/agents/wikigen/article_writer_agent.py

import asyncio
import logging
from textwrap import dedent
from typing import Dict, List, Any
from uuid import UUID, uuid4

from src.prompts import prompt_manager
from src.services.llm.llm_service import LLMService
from src.schemas.llm.models import LLMMessage
from src.core.logging import setup_application_logging, configure_console_logging

logger = logging.getLogger(__name__)

# We need to import ArticleTask, but we need to avoid circular imports
# since wikigen_orchestrator imports this module
from dataclasses import dataclass

@dataclass
class ArticleTask:
    """A structured task for writing a single wiki article."""
    title: str
    type: str
    file: str
    preview: str
    content_structure: str # The planned markdown structure from the <Content> tag

class ArticleWriterAgent:
    """
    A specialized agent that generates the full Markdown content for a single
    wiki article based on a structured plan from the Orchestrator.
    """
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def write_article(
        self,
        task: ArticleTask,
        story_content: str,
        overall_wiki_plan: str,
        user_id: UUID,
        provider: str,
        model: str,
    ) -> str:
        """
        Generates the full Markdown content for a wiki article.

        Args:
            task: The ArticleTask object containing the plan for this article.
            story_content: The full original story text for context.
            overall_wiki_plan: The raw XML of the entire wiki plan for link context.
            user_id: UUID of the user making the request
            provider: LLM provider ID (e.g., 'openai', 'anthropic')
            model: Exact hosted model name to use (e.g., 'gpt-4o')

        Returns:
            The generated Markdown content as a string.
        """
        logger.info(f"--- ArticleWriterAgent: Starting generation for '{task.title}' ---")

        # 1. Get a scoped "group" for the article generation prompts.
        writing_prompts = prompt_manager.get_group("wikigen.generate_article")

        # 2. Get raw data structures (messages)
        raw_message_templates: List[Dict[str, str]] = writing_prompts.get("messages")

        # 3. Prepare dynamic data for rendering.
        render_kwargs: Dict[str, Any] = {
            "article_title": task.title,
            "article_type": task.type,
            "article_file": task.file,
            "article_content_structure": task.content_structure,
            "story_content": story_content,
            "overall_wiki_plan": overall_wiki_plan,
        }

        # 4. Render each message's content and convert to LLMMessage objects.
        final_messages: List[LLMMessage] = []
        for msg_template in raw_message_templates:
            rendered_content = writing_prompts.render(
                msg_template['content'],
                **render_kwargs
            )
            final_messages.append(LLMMessage(role=msg_template['role'], content=rendered_content))
        
        # 5. Log the final prompt for debugging
        logger.debug("--- ArticleWriterAgent: Final LLM Messages (Start) ---")
        for msg in final_messages:
            logger.debug(f"\n{msg.content}\n")
        logger.debug("--- ArticleWriterAgent: Final LLM Messages (End) ---")

        # 6. Call the LLM Service
        llm_response = await self.llm_service.chat_completion(
            user_id=user_id,
            provider=provider,
            model=model,
            messages=final_messages
        )
        generated_content = llm_response.content
        
        logger.info(f"--- ArticleWriterAgent: Finished generation for '{task.title}' ---")
        return generated_content


# === Testing/Demo Code ===
async def main():
    """Asynchronous main function to run the agent test."""
    configure_console_logging(log_level="DEBUG", log_format='%(message)s')
    setup_application_logging(log_level="DEBUG")

    from src.schemas.llm.models import LLMResponse

    class MockLLMService:
        async def chat_completion(
            self,
            user_id: UUID,
            provider: str,
            model: str,
            messages: List[LLMMessage],
            **kwargs,
        ) -> LLMResponse:
            """A mock of the real LLMService.chat_completion method."""
            logger.info("\n=== Mock LLM Service Called (ArticleWriter) ===")
            logger.info(f"  UserID:   {user_id}")
            logger.info(f"  Provider: {provider}")
            logger.info(f"  Model:    {model}")
            
            # In a real scenario, the LLM would generate this based on the prompt.
            mock_content = dedent("""
            # Elara
            Elara is the main protagonist of *The Crystal of Aethermoor*. She is a gifted spellcaster hailing from the quiet village of Oakhaven.

            ## History
            Elara discovered the ancient prophecy foretelling the rise of the Shadow King. This discovery prompted her to begin her quest.

            ## Relationships
            - **[[Finn]]**: Her childhood friend and skilled tracker who joins her on her journey.
            """).strip()

            return LLMResponse(
                content=mock_content,
                model=model,
                usage={"prompt_tokens": 200, "completion_tokens": 100, "total_tokens": 300},
                metadata={"provider": provider, "user_id": str(user_id)}
            )

    # 1. Test Data
    writer_agent = ArticleWriterAgent(llm_service=MockLLMService()) # type: ignore

    test_story = dedent("""
    In the quiet village of Oakhaven, young Elara, a gifted but naive spellcaster,
    discovered an ancient prophecy detailing the rise of the Shadow King in the
    Forbidden Peaks. Alongside her childhood friend, Finn, a skilled tracker,
    she embarked on a perilous journey through the Whispering Woods,
    seeking the legendary Sunstone, the only artifact capable of defeating him.
    """)

    # This would be generated by the PlannerAgent in a real run
    mock_overall_plan = dedent("""
        <Article title="The Crystal of Aethermoor Wiki" type="main" file="The Crystal of Aethermoor Wiki.md">...</Article>
        <Article title="Elara" type="character" file="characters/Elara.md">...</Article>
        <Article title="Finn" type="character" file="characters/Finn.md">...</Article>
    """)

    # This is one of the tasks that the Orchestrator would create
    mock_article_task = ArticleTask(
        title="Elara",
        type="character",
        file="characters/Elara.md",
        preview="A gifted but naive spellcaster from the village of Oakhaven.",
        content_structure=dedent("""
            # Synopsis
            A brief summary of the character.
            # History
            Details about the character's background.
            # Relationships
            - [[Finn]]
        """).strip()
    )

    logger.info("=" * 60)
    logger.info("TESTING ARTICLE WRITER AGENT")
    logger.info("=" * 60)

    try:
        # 2. Run the agent
        generated_markdown = await writer_agent.write_article(
            task=mock_article_task,
            story_content=test_story,
            overall_wiki_plan=mock_overall_plan,
            user_id=uuid4(),
            provider="openai",
            model="gpt-4o"
        )
        logger.info("✅ SUCCESS: Article generated successfully.")
        logger.info("📊 Generated Markdown:")
        logger.info(generated_markdown)

    except Exception as e:
        logger.error(f"❌ ERROR in Test: {e}", exc_info=True)

    logger.info("\n" + "=" * 60)
    logger.info("TESTING COMPLETE")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 