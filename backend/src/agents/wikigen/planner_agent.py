# backend/src/agents/wikigen/planner_agent.py

import json
import logging
from textwrap import dedent
from typing import Dict, Any, List

# Import the globally available prompt_manager instance
from src.prompts import prompt_manager

# Import the refined logging setup function
from src.core.logging import setup_application_logging, configure_console_logging
from src.config import settings # Assuming src.config exists and provides settings

# Get a logger instance for this module.
logger = logging.getLogger(__name__)

class PlannerAgent:
    def __init__(self, llm_service: Any):
        self.llm_service = llm_service

    def create_plan(
        self,
        story_title: str,
        story_content: str,
        include_examples: bool = False
    ) -> Dict[str, Any]:
        """Creates a plan by fetching and rendering prompt data."""

        # 1. Get a scoped "group" for the planning prompts.
        planning_prompts = prompt_manager.get_group("wikigen.planning")

        # 2. Get raw data structures (messages, examples)
        raw_message_templates: List[Dict[str, str]] = planning_prompts.get("messages")

        # 3. Prepare dynamic data for rendering.
        render_kwargs: Dict[str, Any] = {
            "story_title": story_title,
            "story_content": story_content,
        }

        if include_examples:
            examples_data = planning_prompts.get("examples")
            render_kwargs["examples"] = list(examples_data.values())
        else:
            render_kwargs["examples"] = None

        # 4. Render each message's content.
        final_messages: List[Dict[str, str]] = []
        for msg_template in raw_message_templates:
            rendered_content = planning_prompts.render(
                msg_template['content'],
                **render_kwargs
            )
            final_messages.append({"role": msg_template['role'], "content": rendered_content})

        # 5. Log the Final Messages in a readable, detailed format.
        logger.info("--- LLM Messages (Start) ---")
        for i, msg in enumerate(final_messages):
            logger.info(f"  Message {i+1} [Role: {msg['role']}] ({len(msg['content'])} chars):")
            # Indent the content for readability in the logs
            logger.debug(f"\n{msg['content']}\n") # Use debug for the actual content
            logger.info("-" * 40) # Separator for messages
        logger.info("--- LLM Messages (End) ---")

        # 6. Call the LLM Service (mocked for demo)
        mock_response_content = json.dumps({
            "title": "Mock Plan",
            "arcs": ["mock_arc_1", "mock_arc_2"],
            "entities": ["mock_entity_A", "mock_entity_B"]
        })
        try:
            return json.loads(mock_response_content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse mock LLM response as JSON: {e}")
            return {"error": "Invalid JSON response from LLM", "raw_response": mock_response_content}


# === Testing/Demo Code ===
if __name__ == "__main__":
    # --- IMPORTANT: Configure logging specifically for this test run ---
    # Configure the root logger for clean, message-only output on stdout.
    configure_console_logging(
        log_level="DEBUG", # Set level to DEBUG to see all prompt content
        log_format='%(message)s' # Only print the message, no timestamp/name/level
    )
    # Then set up the application loggers (e.g., "shuscribe" logger) if needed
    # This ensures your custom `shuscribe` logger (and other named ones)
    # follow the desired debug levels.
    setup_application_logging(log_level="DEBUG") 

    # Mock LLM Service for testing
    class MockLLMService:
        def call_llm(self, messages: List[Dict[str, str]]) -> str:
            logger.info("\n=== Mock LLM Service Called ===")
            logger.debug(f"Received {len(messages)} messages for LLM processing.")
            return json.dumps({
                "title": "The Enchanted Forest Adventure",
                "arcs": [
                    {
                        "name": "The Discovery", 
                        "summary": "Hero finds the magical artifact", 
                        "start_page": 1, 
                        "end_page": 10
                    }
                ],
                "entities": [
                    {"name": "Elara", "type": "PERSON", "importance": "Main protagonist"}
                ]
            })

    # Create agent instance
    planner = PlannerAgent(llm_service=MockLLMService())

    # Test story content
    test_story = dedent("""
    In the quiet village of Oakhaven, young Elara, a gifted but naive spellcaster,
    discovered an ancient prophecy detailing the rise of the Shadow King in the
    Forbidden Peaks. Alongside her childhood friend, Finn, a skilled tracker,
    she embarked on a perilous journey through the Whispering Woods,
    seeking the legendary Sunstone, the only artifact capable of defeating him.
    """)

    logger.info("=" * 60)
    logger.info("TESTING PLANNER AGENT")
    logger.info("=" * 60)

    # Test 1: Without examples
    logger.info("\n🧪 TEST 1: Planning WITHOUT examples")
    logger.info("-" * 40)
    try:
        plan_result = planner.create_plan(
            story_title="The Crystal of Aethermoor",
            story_content=test_story,
            include_examples=False
        )
        logger.info("✅ SUCCESS: Plan generated without examples")
        # Ensure JSON result is on a new line after the label
        logger.info(f"📊 Result:\n{json.dumps(plan_result, indent=2)}")
        
    except Exception as e:
        logger.error(f"❌ ERROR in Test 1: {e}", exc_info=True)

    # Test 2: With examples
    logger.info("\n🧪 TEST 2: Planning WITH examples")
    logger.info("-" * 40)
    try:
        plan_result = planner.create_plan(
            story_title="The Crystal of Aethermoor",
            story_content=test_story,
            include_examples=True
        )
        logger.info("✅ SUCCESS: Plan generated with examples")
        # Ensure JSON result is on a new line after the label
        logger.info(f"📊 Result:\n{json.dumps(plan_result, indent=2)}")
        
    except Exception as e:
        logger.error(f"❌ ERROR in Test 2: {e}", exc_info=True)

    logger.info("\n" + "=" * 60)
    logger.info("TESTING COMPLETE")
    logger.info("=" * 60)