# backend/src/agents/wikigen/planner_agent.py

"""
Wiki Planner Agent

Plans wiki structure and article organization. Determines what articles to create 
and how to organize them for optimal user experience.

Key Responsibilities:
- Determines article types needed for current arc
- Plans article structure and organization  
- Identifies cross-referencing opportunities
- Handles fresh vs. update planning modes
- Creates file structure and naming conventions

Key Features:
- Fresh mode for new wikis
- Update mode for existing wikis  
- Entity analysis and categorization
- Cross-reference planning
- Structured article planning
- Consistent organization schemes
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

# TODO: Import proper types when schemas are defined
# from src.database.models.story import FullStoryBase as Story, Chapter
# from src.database.models.workspace import Arc
# NOTE: WikiPlan, ArticlePlan, and EntityAnalysis may need to be created in domain models
from src.services.llm.llm_service import LLMService
from src.prompts import prompt_manager
from src.agents.base_agent import BaseAgent


class WikiPlannerAgent(BaseAgent):
    """
    Plans wiki structure and article organization for optimal user experience.
    
    Analyzes story content to determine what articles should be created,
    how they should be structured, and how they should reference each other.
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
            llm_service: LLM service for making planning calls
            default_provider: Default LLM provider for wiki planning
            default_model: Default model optimized for planning and organization
        """
        super().__init__(
            llm_service=llm_service,
            default_provider=default_provider,
            default_model=default_model
        )
    
    async def create_plan(
        self,
        arc_content: str,
        story_metadata: Dict[str, Any],
        mode: str,  # "fresh" or "update"
        user_id: UUID,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        previous_summaries: Optional[List[Any]] = None,  # TODO: List[ArcSummary]
        existing_wiki: Optional[Any] = None  # TODO: WikiArchive
    ) -> Any:  # TODO: Replace with WikiPlan type
        """
        Main planning method that creates comprehensive wiki structure.
        
        Handles both "fresh" and "update" modes for different use cases.
        
        Fresh Mode Process:
        1. Analyze arc content for entities
        2. Categorize entities by type and importance
        3. Plan article structures for each entity
        4. Create file organization scheme
        5. Plan cross-referencing strategy
        
        Update Mode Process:
        1. Analyze new arc content
        2. Compare with existing wiki structure
        3. Plan updates to existing articles
        4. Identify new articles needed
        5. Maintain consistency with previous arcs
        
        Args:
            arc_content: Text content of the current arc
            story_metadata: Story title, genre, etc.
            mode: "fresh" for new wikis, "update" for existing
            user_id: UUID of the user making the request
            api_key: Optional API key for direct usage
            provider: Optional LLM provider override (uses default if not provided)
            model: Optional LLM model override (uses default if not provided)
            previous_summaries: Summaries from previous arcs (update mode)
            existing_wiki: Previous wiki archive (update mode)
            
        Returns:
            WikiPlan object with detailed article plans and organization
            
        Output Format:
            <WikiPlan>
              <Articles>
                <Article title="Story Wiki" type="main" file="Story_Wiki.md">
                  <Preview>Main wiki page summarizing the story</Preview>
                  <Structure>
                    # Synopsis
                    # Characters  
                    # Plot Summary
                    ## Arc 1: The Awakening
                  </Structure>
                </Article>
                <!-- Additional articles -->
              </Articles>
            </WikiPlan>
        """
        # TODO: Implement planning logic
        raise NotImplementedError("Wiki planning not yet implemented")
    
    def _analyze_entities(self, arc_content: str) -> Any:  # TODO: EntityAnalysis
        """
        Identifies characters, locations, concepts, and events in arc content.
        
        Categorizes entities by:
        - Type (character, location, concept, event)
        - Importance (major, minor, mentioned)
        - Complexity (needs dedicated article vs. brief mention)
        
        Args:
            arc_content: Text content to analyze
            
        Returns:
            EntityAnalysis object with categorized entities
        """
        # TODO: Implement entity analysis
        # This could use NLP techniques or LLM analysis to identify entities
        pass
    
    def _plan_article_structure(self, entity: Any, article_type: str) -> Any:  # TODO: ArticleStructure
        """
        Creates detailed structure plan for individual articles.
        
        Defines appropriate sections based on entity type:
        - Characters: Overview, History, Relationships, Development
        - Locations: Description, Geography, History, Significance
        - Concepts: Definition, Origins, Usage, Examples
        - Events: Overview, Participants, Consequences, Timeline
        
        Args:
            entity: Entity object to plan structure for
            article_type: Type of article (character, location, etc.)
            
        Returns:
            ArticleStructure object with sections and content plan
        """
        # TODO: Implement structure planning
        pass
    
    def _identify_cross_references(
        self, 
        entities: List[Any], 
        existing_articles: Optional[List[Any]] = None
    ) -> List[Any]:  # TODO: List[CrossReference]
        """
        Identifies opportunities for wiki-style linking between articles.
        
        Maps relationships between entities and plans linking strategy:
        - Character relationships and interactions
        - Location connections and geography
        - Concept dependencies and usage
        - Event participants and consequences
        
        Args:
            entities: List of entities from current arc
            existing_articles: Articles from previous arcs (update mode)
            
        Returns:
            List of CrossReference objects for linking strategy
        """
        # TODO: Implement cross-reference identification
        return []
    
    def _create_file_organization(self, entities: List[Any]) -> Dict[str, Any]:
        """
        Plans file structure and naming conventions for wiki articles.
        
        Creates organized directory structure:
        - characters/ for character articles
        - locations/ for location articles  
        - concepts/ for concept articles
        - events/ for event articles
        - Main wiki page at root
        
        Args:
            entities: List of entities to organize
            
        Returns:
            Dictionary mapping entities to file paths
        """
        # TODO: Implement file organization planning
        return {}
    
    def _load_planning_prompts(
        self, 
        mode: str, 
        context: Dict[str, Any]
    ) -> List[Any]:  # TODO: List[LLMMessage]
        """
        Loads and renders planning prompts based on mode and context.
        
        Uses wikigen.planning prompt group with appropriate variables.
        
        Args:
            mode: "fresh" or "update" for different prompt variants
            context: Variables for prompt rendering
            
        Returns:
            List of rendered LLMMessage objects
        """
        # TODO: Implement prompt loading
        # planning_prompts = prompt_manager.get_group("wikigen.planning")
        # Render with mode-specific context
        return []
    
    # Implementation of BaseAgent's abstract method
    async def execute(self, *args, **kwargs):
        """
        Execute the wiki planning process.
        
        This is a convenience method that calls create_plan with the provided arguments.
        """
        return await self.create_plan(*args, **kwargs) 