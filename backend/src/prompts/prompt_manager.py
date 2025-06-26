# backend/src/prompts/prompt_manager.py

import toml
from pathlib import Path
from typing import Dict, Any

from jinja2 import Environment, FileSystemLoader, Template

class PromptGroup:
    """
    A scoped view into a part of the prompt data tree.
    Provides methods to get nested data and render templates relative to its scope.
    """
    def __init__(self, data: Dict[str, Any], manager: 'PromptManager'):
        self._data = data
        self._manager = manager # Reference to the main manager for rendering

    def get(self, key: str) -> Any:
        """
        Retrieves data from within this group using a dot-notation key.
        e.g., if the group is 'wikigen.planning', key can be 'messages' or 'examples.good_plan_1'.
        """
        parts = key.split('.')
        current_data = self._data
        for part in parts:
            try:
                current_data = current_data[part]
            except (KeyError, TypeError): # TypeError handles cases where current_data is not a dict
                raise KeyError(f"Key '{key}' not found within this prompt group.")
        return current_data

    def render(self, template_string: str, **kwargs: Any) -> str:
        """A convenience method to access the main manager's render function."""
        return self._manager.render(template_string, **kwargs)

class PromptManager:
    """
    Loads all TOML prompt files and provides scoped access via PromptGroup objects.
    """
    def __init__(self, prompts_dir: Path):
        # ... (constructor remains the same as the previous version) ...
        if not prompts_dir.is_dir():
            raise FileNotFoundError(f"Prompts directory not found: {prompts_dir}")
        
        self.prompts_dir = prompts_dir
        
        jinja_search_paths = [str(prompts_dir)]
        for subdir in prompts_dir.iterdir():
            if subdir.is_dir() and (subdir / "_common").is_dir():
                jinja_search_paths.append(str(subdir))
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(jinja_search_paths),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.jinja_env.filters['tojson'] = __import__('json').dumps
        self._data = self._load_all_toml_files()

    def _load_all_toml_files(self) -> Dict[str, Any]:
        # ... (this method remains the same) ...
        nested_data = {}
        for toml_file in self.prompts_dir.rglob("*.toml"):
            if any(part.startswith('_') for part in toml_file.parts):
                continue
            relative_path_parts = toml_file.relative_to(self.prompts_dir).with_suffix('').parts
            current_level = nested_data
            for part in relative_path_parts:
                current_level = current_level.setdefault(part, {})
            current_level.update(toml.load(toml_file))
        return nested_data

    def get_group(self, key: str) -> PromptGroup:
        """
        Retrieves a scoped PromptGroup for a part of the data tree.
        e.g., "wikigen.planning"
        """
        parts = key.split('.')
        current_data = self._data
        for part in parts:
            try:
                current_data = current_data[part]
            except KeyError:
                raise KeyError(f"Prompt group key '{key}' not found. Missing part: '{part}'")
        
        if not isinstance(current_data, dict):
            raise TypeError(f"Key '{key}' points to a value, not a group (dictionary).")
            
        return PromptGroup(current_data, self)

    def render(self, template_string: str, **kwargs: Any) -> str:
        """The master render function, used by PromptGroup objects."""
        template: Template = self.jinja_env.from_string(template_string)
        return template.render(**kwargs)