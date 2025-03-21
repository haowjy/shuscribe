# shuscribe/services/llm/prompts/groups.py

from typing import List, Optional, Sequence, Union

from shuscribe.schemas.llm import Message
from shuscribe.services.llm.prompts.manager import PromptManager
from shuscribe.schemas.pipeline import Chapter
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
                  focus_genre: Optional[str] = None) -> List[Message]:
        """Generate entity extraction prompt"""
        return self._get_template("extraction").format(
            chapter_content=chapter_content,
            chapter_id=chapter_id,
            focus_genre=focus_genre
        )
    
    def update(self, 
              previous_entities: List[dict], 
              new_entities: List[dict], 
              chapter_id: str) -> List[Message]:
        """Generate entity update prompt"""
        return self._get_template("update").format(
            previous_entities=previous_entities,
            new_entities=new_entities,
            chapter_id=chapter_id
        )


class ChapterPromptGroup(PromptGroup):
    """Chapter-related prompts"""
    
    def summary(self, 
               current_chapter: Chapter,
               last_chapter: Optional[Chapter] = None,
               story_metadata: Optional[str] = None,
               reader_context: Optional[str] = None,
               focus_genre: Optional[str] = None) -> list[Message]:
        """Generate chapter summary prompt
        
        Args:
            current_chapter: The current chapter of the story
            ```
            # Current Chapter
            {{ current_chapter }}
            ```
            last_chapter: The last chapter of the story (if available)
            ```
            # Last Chapter
            {{ last_chapter }}
            ```
            story_metadata: The metadata of the story (e.g. title, author, genre, etc.)
            ```
            # Story Context
            {{ story_metadata }}
            ```
            reader_context: The context of the reader (full story summary and summary of recent chapters)
            ```
            # Reader Context
            {{ reader_context }}
            ```
            focus_genre: The genre of the story
            ```
            # Genre Context
            This is a {{ focus_genre }} story. Pay special attention to genre-specific elements.
            ```
        """
        
        return self._get_template("summary").format(
            current_chapter=current_chapter.to_prompt(),
            last_chapter=last_chapter.to_prompt() if last_chapter else None,
            story_metadata=story_metadata,
            reader_context=reader_context,
            focus_genre=focus_genre
        ) 

class WikiPromptGroup(PromptGroup):
    """Wiki-related prompts"""
    
    def main_article(self, 
                    chapter_summary: str, 
                    central_entities: List[dict],
                    major_entities: List[dict],
                    chapter_id: str,
                    previous_content: Optional[str] = None) -> List[Message]:
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
                         previous_content: Optional[str] = None) -> List[Message]:
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
                       previous_content: Optional[str] = None) -> List[Message]:
        """Generate a generic wiki article for any entity type"""
        return self._get_template("generic_article").format(
            entity=entity,
            entity_type=entity_type,
            chapter_id=chapter_id,
            chapter_excerpt=chapter_excerpt,
            previous_content=previous_content or ""
        )
        