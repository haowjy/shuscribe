# shuscribe/services/llm/prompts/template.py

from typing import Dict, List, Optional, Union, Any
import yaml
from pydantic import BaseModel
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
    user: Optional[Union[str, List[str]]] = None
    assistant: Optional[Union[str, List[str]]] = None
    tool: Optional[Union[str, List[str]]] = None


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
    
    def format(self, **kwargs) -> List[Union[Message, str]]:
        messages = []
        
        # Add system message if present
        if self.config.system_prompt:
            messages.append(Message(
                role=MessageRole.SYSTEM,
                content=self._render_template(self.config.system_prompt, kwargs)
            ))
        
        # Process all message types
        user_messages = [self.config.user] if isinstance(self.config.user, str) else (self.config.user or [])
        assistant_messages = [self.config.assistant] if isinstance(self.config.assistant, str) else (self.config.assistant or [])
        tool_messages = [self.config.tool] if isinstance(self.config.tool, str) else (self.config.tool or [])
        
        # Determine maximum turns and build conversation
        max_turns = max(len(user_messages), len(assistant_messages), len(tool_messages))
        
        for i in range(max_turns):
            if i < len(user_messages) and user_messages[i]:
                messages.append(Message(
                    role=MessageRole.USER,
                    content=self._render_template(user_messages[i], kwargs)
                ))
            
            if i < len(assistant_messages) and assistant_messages[i]:
                messages.append(Message(
                    role=MessageRole.ASSISTANT,
                    content=self._render_template(assistant_messages[i], kwargs)
                ))
            
            if i < len(tool_messages) and tool_messages[i]:
                messages.append(Message(
                    role=MessageRole.TOOL,
                    content=self._render_template(tool_messages[i], kwargs)
                ))
        
        return messages
    
    def _render_template(self, content: str, variables: Dict[str, Any]) -> str:
        template = self.env.from_string(content)
        return template.render(**variables)