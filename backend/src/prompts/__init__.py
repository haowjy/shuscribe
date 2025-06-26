# backend/src/prompts/__init__.py

from pathlib import Path
from .prompt_manager import PromptManager

# Define the path to this directory.
PROMPTS_DIR = Path(__file__).parent

# Create a single, globally accessible instance of our manager.
# Any module can now `from src.prompts import prompt_manager` to use it.
prompt_manager = PromptManager(PROMPTS_DIR)