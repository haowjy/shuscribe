# shuscribe/services/llm/prompts/groups.py

from typing import List, Optional, Union
from shuscribe.schemas.llm import Message
from shuscribe.services.llm.prompts.manager import PromptManager

class PromptGroup:
    """Base class for domain-specific prompt groups"""
    
    def __init__(self, manager: PromptManager):
        self.manager = manager
        self.domain = self.__class__.__name__.lower().replace('promptgroup', '')
        
    def _get_template(self, name: str):
        """Get template from the group's domain"""
        return self.manager.get(self.domain, name)


class EntityPromptGroup(PromptGroup):
    """Entity-related prompts"""
    
    def extraction(self, 
                  chapter_content: str, 
                  chapter_id: str, 
                  focus_genre: Optional[str] = None) -> List[Union[Message, str]]:
        """Generate entity extraction prompt"""
        return self._get_template("extraction").format(
            chapter_content=chapter_content,
            chapter_id=chapter_id,
            focus_genre=focus_genre
        )
    
    def update(self, 
              previous_entities: List[dict], 
              new_entities: List[dict], 
              chapter_id: str) -> List[Union[Message, str]]:
        """Generate entity update prompt"""
        return self._get_template("update").format(
            previous_entities=previous_entities,
            new_entities=new_entities,
            chapter_id=chapter_id
        )


class ChapterPromptGroup(PromptGroup):
    """Chapter-related prompts"""
    
    def summary(self, 
               chapter_content: str, 
               previous_summaries: Optional[List[dict]] = None) -> List[Union[Message, str]]:
        """Generate chapter summary prompt"""
        return self._get_template("summary").format(
            chapter_content=chapter_content,
            previous_summaries=previous_summaries or []
        )


# shuscribe/services/llm/prompts/groups.py

class WikiPromptGroup(PromptGroup):
    """Wiki-related prompts"""
    
    def main_article(self, 
                    chapter_summary: str, 
                    central_entities: List[dict],
                    major_entities: List[dict],
                    chapter_id: str,
                    previous_content: Optional[str] = None) -> List[Union[Message, str]]:
        """Generate main wiki article prompt"""
        return self._get_template("main_article").format(
            chapter_summary=chapter_summary,
            central_entities=central_entities,
            major_entities=major_entities,
            chapter_id=chapter_id,
            previous_content=previous_content or ""
        )
    
    def character_article(self, 
                         entity: dict, 
                         chapter_id: str, 
                         chapter_excerpt: str,
                         previous_content: Optional[str] = None) -> List[Union[Message, str]]:
        """Generate character wiki article prompt"""
        return self._get_template("character_article").format(
            entity=entity,
            chapter_id=chapter_id,
            chapter_excerpt=chapter_excerpt,
            previous_content=previous_content or ""
        )
    
    def generic_article(self,
                       entity: dict,
                       entity_type: str,
                       chapter_id: str,
                       chapter_excerpt: str,
                       previous_content: Optional[str] = None) -> List[Union[Message, str]]:
        """Generate a generic wiki article for any entity type"""
        return self._get_template("generic_article").format(
            entity=entity,
            entity_type=entity_type,
            chapter_id=chapter_id,
            chapter_excerpt=chapter_excerpt,
            previous_content=previous_content or ""
        )