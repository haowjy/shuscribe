# shuscribe/services/llm/prompts/template.py

from abc import abstractmethod
import os
from typing import Dict, List, Optional, Any, Type
import yaml
from pydantic import BaseModel, Field
from jinja2 import Environment
import importlib.resources
import logging

from shuscribe.schemas.base import BaseOutputSchema
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


class PromptTemplateFactory:
    """Enhanced prompt template supporting multi-turn conversations with Jinja2"""
    
    def __init__(self, config: PromptTemplateConfig):
        self.config = config
        self.env = Environment(autoescape=False)
    
    @classmethod
    def from_yaml_string(cls, yaml_string: str) -> 'PromptTemplateFactory':
        data = yaml.safe_load(yaml_string)
        config = PromptTemplateConfig(**data)
        return cls(config)
    
    @classmethod
    def from_name(cls, name: str, package="shuscribe.services.llm.prompts.prompt") -> 'PromptTemplateFactory':
        try:
            yaml_file = f"{name}.yaml"
            yaml_text = importlib.resources.read_text(package, yaml_file)
            return cls.from_yaml_string(yaml_text)
        except (FileNotFoundError, ModuleNotFoundError, ImportError) as e:
            raise ValueError(f"Prompt template '{name}' not found in package '{package}': {str(e)}")
    
    def _render_template(self, content: str, variables: Dict[str, Any]) -> str:
        template = self.env.from_string(content)
        return template.render(**variables)


class PromptTemplate:
    """Wrapper around a PromptTemplateFactory that allows for custom formatting logic"""
    
    def __init__(self, name: str, package: str):
        self.name = name
        self.package = package
        self.factory = PromptTemplateFactory.from_name(self.name, self.package)
        
        self.default_provider: str = "gemini"
        self.default_model: str = "gemini-2.0-flash-001"
        self.default_temperature: float = 0.4
        
        self._response_schema: Type[BaseOutputSchema] | None = None
    
    @property
    def response_schema(self) -> Type[BaseOutputSchema] | None:
        return self._response_schema
    
    @response_schema.setter
    def response_schema(self, schema: Type[BaseOutputSchema]):
        self._response_schema = schema
    
    
    @classmethod
    def from_yaml_string(cls, yaml_string: str) -> 'PromptTemplate':
        factory = PromptTemplateFactory.from_yaml_string(yaml_string)
        pt = cls("", "")
        pt.factory = factory
        return pt
    
    def reload(self) -> 'PromptTemplate':
        env = os.environ.get("ENVIRONMENT", "prod").lower()
        if env == "prod":
            logging.warning("SECURITY: Attempted to reload template in production environment")
            return self
        
        self.factory = PromptTemplateFactory.from_name(self.name, self.package)
        return self
    
    @abstractmethod
    def format(self, **kwargs) -> List[Message]:
        """Format the template with the given variables."""
        formatted_messages = []
        
        # Add system message if present
        if self.factory.config.system_prompt:
            formatted_messages.append(Message(
                role=MessageRole.SYSTEM,
                content=self.factory._render_template(self.factory.config.system_prompt, kwargs)
            ))
        
        # Add any additional messages
        if isinstance(self.factory.config.messages, list):
            formatted_messages.extend(self.factory.config.messages)
                
        # Add user message with prompt if present
        if self.factory.config.prompt:
            formatted_messages.append(Message(
                role=MessageRole.USER,
                content=self.factory._render_template(self.factory.config.prompt, kwargs)
            ))
        
        return formatted_messages