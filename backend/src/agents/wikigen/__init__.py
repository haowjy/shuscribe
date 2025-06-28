"""
WikiGen Workflow: Agent-based story processing and wiki generation.

This package contains all agents and orchestration logic for the WikiGen workflow,
which transforms unstructured narrative text into comprehensive, interconnected 
wiki systems through arc-based processing with spoiler prevention.

Key Features:
- Arc-based processing for stories of any length
- Spoiler-prevention through progressive wiki archives
- Specialized agents for different aspects of wiki generation
- Web search integration for cultural references
- Bidirectional chapter-wiki linking
"""

from .orchestrator import WikiGenOrchestrator
from .arc_splitter import ArcSplitterAgent
from .planner_agent import WikiPlannerAgent
from .article_writer import ArticleWriterAgent

from .general_summarizer import GeneralSummarizerAgent
from .chapter_backlinker import ChapterBacklinkerAgent

__all__ = [
    "WikiGenOrchestrator",
    "ArcSplitterAgent", 
    "WikiPlannerAgent",
    "ArticleWriterAgent",
    "GeneralSummarizerAgent",
    "ChapterBacklinkerAgent",
]
