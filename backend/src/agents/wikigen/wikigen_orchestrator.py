# backend/src/agents/wikigen/wikigen_orchestrator.py

import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from textwrap import dedent
from typing import List
from uuid import UUID

from src.agents.wikigen.planner_agent import PlannerAgent
from src.agents.wikigen.article_writer_agent import ArticleWriterAgent, ArticleTask
from src.services.llm.llm_service import LLMService
from src.core.logging import setup_application_logging

logger = logging.getLogger(__name__)

class WikiGenOrchestrator:
    """
    Orchestrates the entire wiki generation process.
    This agent acts as the main thread, managing the overall workflow by calling
    specialized agents to perform specific tasks like planning and article writing.
    """
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.planner_agent = PlannerAgent(llm_service)
        self.article_writer_agent = ArticleWriterAgent(llm_service)

    async def generate_wiki(
        self, 
        story_title: str, 
        story_content: str, 
        output_dir: Path,
        user_id: UUID,
        provider: str,
        model: str
    ) -> None:
        """
        Executes the full pipeline to generate a wiki for a given story.
        """
        logger.info(f"Starting wiki generation for story: '{story_title}'")

        # Step 1: Format the input and call the PlannerAgent.
        logger.info("Calling PlannerAgent to generate the wiki structure plan...")
        story_xml = self._create_story_xml(story_title, story_content)
        wiki_plan_raw = await self.planner_agent.create_plan(
            story_title=story_title, 
            story_xml=story_xml,
            user_id=user_id,
            provider=provider,
            model=model
        )

        # Step 2: Parse the raw plan into a list of actionable tasks.
        logger.info("Parsing the wiki plan...")
        article_tasks = self._parse_plan(wiki_plan_raw)
        if not article_tasks:
            logger.warning("Parsing the plan yielded no article tasks. Aborting.")
            return

        logger.info(f"Plan parsed successfully. Found {len(article_tasks)} articles to generate.")
        for i, task in enumerate(article_tasks):
            logger.debug(f"  - Task {i+1}: {task.title} ({task.type}) -> {task.file}")


        # Step 3: Iterate through tasks and call the ArticleWriterAgent.
        logger.info("Beginning article generation...")
        for task in article_tasks:
            logger.info(f"Generating article: '{task.title}'")
            article_content = await self.article_writer_agent.write_article(
                task=task,
                story_content=story_content,
                overall_wiki_plan=wiki_plan_raw,
                user_id=user_id,
                provider=provider,
                model=model
            )
            # Step 4: Save the generated article content to a file.
            self._save_article(task, article_content, output_dir)

        logger.info(f"Wiki generation process complete. Output saved to '{output_dir.resolve()}'")

    def _create_story_xml(self, title: str, content: str) -> str:
        """Wraps the raw story content in a simple XML structure for the planner."""
        # This is a simple placeholder. In a real scenario, this might involve
        # fetching more metadata, genre, tags, etc.
        return dedent(f"""
        <Story>
            <Title>{title}</Title>
            <Content>
            {content}
            </Content>
        </Story>
        """).strip()

    def _parse_plan(self, raw_xml_plan: str) -> List[ArticleTask]:
        """
        Parses the XML output from the planner into a list of ArticleTask objects.
        """
        tasks = []
        try:
            # The LLM can sometimes return multiple root elements or text outside the root,
            # so we wrap the response in a single <root> tag to ensure it's well-formed.
            wrapped_xml = f"<root>{raw_xml_plan}</root>"
            root = ET.fromstring(wrapped_xml)
            for article_element in root.findall('Article'):
                task = ArticleTask(
                    title=article_element.attrib.get('title', 'No Title Provided'),
                    type=article_element.attrib.get('type', 'No Type Provided'),
                    file=article_element.attrib.get('file', 'No File Provided'),
                    preview=article_element.findtext('Preview', '').strip(),
                    content_structure=article_element.findtext('Content', '').strip()
                )
                tasks.append(task)
            return tasks
        except ET.ParseError as e:
            logger.error(f"Failed to parse planner XML response: {e}")
            logger.debug(f"--- Problematic XML --- \n{raw_xml_plan}")
            return []

    def _save_article(self, task: ArticleTask, content: str, output_dir: Path) -> None:
        """
        Saves the generated article content to its specified file path.
        """
        try:
            output_path = output_dir / task.file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
            logger.info(f"  -> Article saved: {output_path}")
        except IOError as e:
            logger.error(f"  -> Failed to save article '{task.title}' to {output_path}: {e}") 