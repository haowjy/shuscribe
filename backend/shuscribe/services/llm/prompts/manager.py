# shuscribe/services/llm/prompts/manager.py

from typing import Dict
import importlib.resources
from importlib.resources import files, as_file
import logging

from shuscribe.services.llm.prompts.template import PromptTemplate

logger = logging.getLogger(__name__)

class PromptManager:
    """Manager for prompt templates with domain organization"""
    
    _instance = None
    
    def __init__(self, base_package="shuscribe.services.llm.prompts.templates"):
        self.base_package = base_package
        self._cache: Dict[str, PromptTemplate] = {}
        
        # Lazy-loaded groups
        self._entity_group = None
        self._chapter_group = None
        self._wiki_group = None
        
        self._scan_templates()
    
    def __new__(cls, base_package="shuscribe.services.llm.prompts.templates"):
        if cls._instance is None:
            cls._instance = super(PromptManager, cls).__new__(cls)
            cls._instance.base_package = base_package
            cls._instance._cache = {}
        return cls._instance
    
    def _scan_templates(self):
        """Scan available templates using importlib.resources"""
        logger.info(f"Scanning prompt templates in package {self.base_package}")
        try:
            # First, check if the base package exists
            base_resources = files(self.base_package)
            if not base_resources.is_dir():
                logger.warning(f"Base package {self.base_package} is not a directory")
                return
                
            # Get domain directories
            domains = []
            with as_file(base_resources) as path:
                for item in path.iterdir():
                    if item.is_dir():
                        domains.append(item.name)
            
            # Scan each domain
            for domain in domains:
                domain_package = f"{self.base_package}.{domain}"
                try:
                    domain_resources = files(domain_package)
                    if domain_resources.is_dir():
                        templates = []
                        with as_file(domain_resources) as domain_path:
                            for file_path in domain_path.glob("*.yaml"):
                                templates.append(file_path.stem)
                        
                        if templates:
                            logger.info(f"Domain '{domain}' templates: {', '.join(templates)}")
                except (ModuleNotFoundError, ImportError, ValueError):
                    logger.warning(f"Could not scan domain package {domain_package}")
                    
        except (ModuleNotFoundError, ImportError, ValueError):
            logger.warning(f"Could not access base template package {self.base_package}")
    
    def get(self, domain: str, name: str) -> PromptTemplate:
        """
        Get a prompt template by domain and name
        
        Args:
            domain: Domain folder name (entity, chapter, wiki)
            name: Template name within the domain
            
        Returns:
            PromptTemplate instance
        """
        cache_key = f"{domain}/{name}"
        if cache_key not in self._cache:
            package = f"{self.base_package}.{domain}"
            try:
                yaml_file = f"{name}.yaml"
                yaml_text = importlib.resources.read_text(package, yaml_file)
                self._cache[cache_key] = PromptTemplate.from_yaml_string(yaml_text)
            except (FileNotFoundError, ModuleNotFoundError, ImportError) as e:
                raise ValueError(f"Prompt template '{domain}/{name}' not found: {str(e)}")
        return self._cache[cache_key]
    
    @property
    def entity(self):
        """Get the entity prompt group"""
        if self._entity_group is None:
            from shuscribe.services.llm.prompts.groups import EntityPromptGroup
            self._entity_group = EntityPromptGroup(self)
        return self._entity_group
    
    @property
    def chapter(self):
        """Get the chapter prompt group"""
        if self._chapter_group is None:
            from shuscribe.services.llm.prompts.groups import ChapterPromptGroup
            self._chapter_group = ChapterPromptGroup(self)
        return self._chapter_group
    
    @property
    def wiki(self):
        """Get the wiki prompt group"""
        if self._wiki_group is None:
            from shuscribe.services.llm.prompts.groups import WikiPromptGroup
            self._wiki_group = WikiPromptGroup(self)
        return self._wiki_group