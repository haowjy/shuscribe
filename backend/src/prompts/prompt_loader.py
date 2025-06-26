# backend/src/prompts/prompt_loader.py

import toml
from pathlib import Path
from typing import Dict, Any

from jinja2 import Environment, Template # Ensure Environment and Template are imported

class PromptNamespace:
    """
    A class that acts like a module, allowing dot-notation access to
    nested dictionary data loaded from TOML files.
    """
    def __init__(self, data: Dict[str, Any]):
        for key, value in data.items():
            if isinstance(value, dict):
                # Recursively convert nested dicts to PromptNamespace
                setattr(self, key, PromptNamespace(value))
            else:
                setattr(self, key, value)

    def __repr__(self) -> str:
        return f"<PromptNamespace keys={list(self.__dict__.keys())}>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Recursively converts the PromptNamespace object and its nested
        PromptNamespace objects back into a standard Python dictionary.
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, PromptNamespace):
                # Recursively convert nested namespaces
                result[key] = value.to_dict()
            else:
                # Add primitive values directly
                result[key] = value
        return result


class PromptLoader:
    """
    Loads all TOML prompt files into a dynamic, package-like object structure
    and provides a Jinja2 rendering engine.
    """
    # Modified __init__ to accept a pre-configured jinja_env
    def __init__(self, prompts_dir: Path, jinja_env: Environment):
        if not prompts_dir.is_dir():
            raise FileNotFoundError(f"Prompts directory not found: {prompts_dir}")
        
        self.prompts_dir = prompts_dir
        # Use the passed Jinja Environment instance
        self.jinja_env = jinja_env

    def load(self) -> PromptNamespace:
        """
        Scans the prompts directory, loads all TOML files, and returns a
        single root PromptNamespace object.
        """
        nested_data = {}
        for toml_file in self.prompts_dir.rglob("*.toml"):
            # Ensure _common directories are skipped if they contain TOMLs (though they shouldn't in this setup)
            if any(part.startswith('_') for part in toml_file.parts):
                continue

            relative_path_parts = toml_file.relative_to(self.prompts_dir).with_suffix('').parts
            
            current_level = nested_data
            for part in relative_path_parts:
                current_level = current_level.setdefault(part, {})
            
            current_level.update(toml.load(toml_file))

        return PromptNamespace(nested_data)

    def render(self, template_string: str, **kwargs: Any) -> str:
        """
        Renders a given Jinja2 template string with the provided variables.
        """
        template: Template = self.jinja_env.from_string(template_string)
        return template.render(**kwargs)