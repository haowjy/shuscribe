# shuscribe/services/llm/pipeline/steps/entity.py

import json
import re
import uuid
from typing import List, Union

from pydantic import ValidationError

from shuscribe.services.llm.pipeline.base import PipelineContext
from shuscribe.services.llm.pipeline.base_steps import EnhancedPipelineStep, StepResult
from shuscribe.services.llm.pipeline.conditions import PydanticStoppingCondition, StoppingStatus
from shuscribe.schemas.llm import GenerationConfig
from shuscribe.services.llm.session import LLMSession
from shuscribe.schemas.pipeline import Chapter, ChapterSummary, Entity, ProcessingConfig, EntityList


class EntityExtractionStep(EnhancedPipelineStep):
    """Extracts entities from a chapter"""
    
    def __init__(self, llm_session: LLMSession):
        """Initialize entity extraction step"""
        # Use Pydantic model validation as stopping condition
        stopping_condition = PydanticStoppingCondition(
            model_class=EntityList,
            max_retries=3
        )
        
        super().__init__(
            name="entity_extraction",
            stopping_condition=stopping_condition,
            max_iterations=5
        )
        self.llm_session = llm_session
    
    async def execute(self, context: PipelineContext) -> Union[List[Entity], StepResult]:
        """Execute entity extraction"""
        config = context.data.get_typed(ProcessingConfig)
        chapter = context.data.get_typed(Chapter)
        
        if not config or not chapter:
            return StepResult(
                value=None,
                status=StoppingStatus.ERROR,
                error=ValueError("Missing required configuration or chapter data")
            )
        
        # Create entity extraction prompt
        from shuscribe.services.llm.prompts.manager import PromptManager
        prompt_manager = PromptManager()

        # Get the chapter summary if available
        chapter_summary = context.data.get_typed(ChapterSummary)
        summary_text = chapter_summary.summary if chapter_summary else ""
        
        messages = prompt_manager.entity.extraction(
            chapter_content=chapter.content,
            chapter_id=chapter.id,
            focus_genre=config.focus_genre
        )
        
        # Set response format for structured output
        gen_config = GenerationConfig(
            temperature=0.7,
            response_schema=EntityList
        )
        
        # Generate the entities
        response = await self.llm_session.generate(
            provider_name=config.provider_name,
            model=config.model,
            messages=messages,
            config=gen_config
        )
        
        # Parse response
        try:
            # Look for JSON in the response
            json_pattern = r'(\[.*\])'
            match = re.search(json_pattern, response.text, re.DOTALL)
            if match:
                entities_json = match.group(0)
            else:
                entities_json = response.text
            
            # Parse JSON
            entities_data = json.loads(entities_json)
            
            # Ensure IDs are set
            for entity_data in entities_data:
                if not entity_data.get("id") or entity_data.get("id") == "unique-id":
                    entity_data["id"] = str(uuid.uuid4())
            
            # Convert to Entity objects
            entities = [Entity.parse_obj(entity_data) for entity_data in entities_data]
            return entities
            
        except (json.JSONDecodeError, ValidationError) as e:
            # Return a StepResult with retry status
            return StepResult(
                value=response.text,
                status=StoppingStatus.RETRY,
                error=e
            )


class EntityUpdateStep(EnhancedPipelineStep):
    """Updates previously extracted entities with new information"""
    
    def __init__(self, llm_session: LLMSession):
        """Initialize entity update step"""
        stopping_condition = PydanticStoppingCondition(
            model_class=EntityList,
            max_retries=2
        )
        
        super().__init__(
            name="entity_update",
            stopping_condition=stopping_condition
        )
        self.llm_session = llm_session
    
    async def execute(self, context: PipelineContext) -> Union[List[Entity], StepResult]:
        """Execute entity updates"""
        config = context.data.get_typed(ProcessingConfig)
        chapter = context.data.get_typed(Chapter)
        
        if not config or not chapter:
            return StepResult(
                value=None,
                status=StoppingStatus.ERROR,
                error=ValueError("Missing required configuration or chapter data")
            )
        
        # Get newly extracted entities
        new_entities = context.data.get(f"entity_extraction_result", [])
        if not new_entities:
            return StepResult(
                value=None,
                status=StoppingStatus.ERROR,
                error=ValueError("No extracted entities found")
            )
        
        # Get previous entities if available
        previous_entities = context.data.get("previous_entities", [])
        
        # If no previous entities, just return the new ones
        if not previous_entities:
            # Mark each entity with this chapter as appearance
            for entity in new_entities:
                entity.appearances = [chapter.id]
                entity.first_appearance = chapter.id
                entity.last_appearance = chapter.id
            
            return new_entities
        
        # Create entity update prompt
        from shuscribe.services.llm.prompts.manager import PromptManager
        prompt_manager = PromptManager()
        messages = prompt_manager.entity.update(
            previous_entities=previous_entities,
            new_entities=new_entities,
            chapter_id=chapter.id
        )
        
        # Generate the updated entities
        response = await self.llm_session.generate(
            provider_name=config.provider_name,
            model=config.model,
            messages=messages,
            config=GenerationConfig(
                temperature=0.2,
                response_schema=EntityList
            )
        )
        
        # Parse response
        try:
            # Look for JSON in the response
            json_pattern = r'(\[.*\])'
            match = re.search(json_pattern, response.text, re.DOTALL)
            if match:
                entities_json = match.group(0)
            else:
                entities_json = response.text
            
            # Parse JSON
            entities_data = json.loads(entities_json)
            
            # Convert to Entity objects
            updated_entities = [Entity.parse_obj(entity_data) for entity_data in entities_data]
            return updated_entities
            
        except (json.JSONDecodeError, ValidationError) as e:
            # Return a StepResult with retry status
            return StepResult(
                value=response.text,
                status=StoppingStatus.RETRY,
                error=e
            )