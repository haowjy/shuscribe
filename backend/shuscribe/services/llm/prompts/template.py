# shuscribe/services/llm/prompts/template.py

from typing import Dict, List, Optional, Union, Any
import yaml
from pydantic import BaseModel, Field
from jinja2 import Environment
import importlib.resources
import logging

from shuscribe.schemas.llm import Message, MessageRole

logger = logging.getLogger(__name__)

class PromptTemplateConfig(BaseModel):
    """Configuration for a prompt template loaded from YAML"""
    name: str
    description: str
    version: str = "1.0"
    author: Optional[str] = None
    system_prompt: Optional[str] = None
    prompt: Optional[str] = None
    messages: Optional[List[Message | str]] = Field(default_factory=list)


class PromptTemplate:
    """Enhanced prompt template supporting multi-turn conversations with Jinja2"""
    
    def __init__(self, config: PromptTemplateConfig):
        self.config = config
        self.env = Environment(autoescape=False)
    
    @classmethod
    def from_yaml_string(cls, yaml_string: str) -> 'PromptTemplate':
        data = yaml.safe_load(yaml_string)
        config = PromptTemplateConfig(**data)
        return cls(config)
    
    @classmethod
    def from_name(cls, name: str, package="shuscribe.services.llm.prompts.prompt") -> 'PromptTemplate':
        try:
            yaml_file = f"{name}.yaml"
            yaml_text = importlib.resources.read_text(package, yaml_file)
            return cls.from_yaml_string(yaml_text)
        except (FileNotFoundError, ModuleNotFoundError, ImportError) as e:
            raise ValueError(f"Prompt template '{name}' not found in package '{package}': {str(e)}")
    
    def format(self, **kwargs) -> List[Message]:
        """Format the template with the given variables."""
        formatted_messages = []
        
        # Add system message if present
        if self.config.system_prompt:
            formatted_messages.append(Message(
                role=MessageRole.SYSTEM,
                content=self._render_template(self.config.system_prompt, kwargs)
            ))
        
        # Add any additional messages
        if isinstance(self.config.messages, list):
            formatted_messages.extend(self.config.messages)
                
        # Add user message with prompt if present
        if self.config.prompt:
            formatted_messages.append(Message(
                role=MessageRole.USER,
                content=self._render_template(self.config.prompt, kwargs)
            ))
        
        return formatted_messages
    
    def _render_template(self, content: str, variables: Dict[str, Any]) -> str:
        template = self.env.from_string(content)
        return template.render(**variables)
