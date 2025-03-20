# shuscribe/services/llm/prompts/__init__.py

from shuscribe.services.llm.prompts.template import PromptTemplate, PromptTemplateConfig
from shuscribe.services.llm.prompts.manager import PromptManager
from shuscribe.services.llm.prompts.groups import EntityPromptGroup, ChapterPromptGroup, WikiPromptGroup

__all__ = [
    'PromptTemplate',
    'PromptTemplateConfig',
    'PromptManager',
    'EntityPromptGroup',
    'ChapterPromptGroup',
    'WikiPromptGroup',
]