# shuscribe/services/llm/pipeline/conditions.py

import re
import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional, Type, Union, Callable
from pydantic import BaseModel, ValidationError
from shuscribe.services.llm.pipeline.base import PipelineContext


class StoppingStatus(str, Enum):
    """Status of a stopping condition evaluation"""
    CONTINUE = "continue"      # Continue processing, condition not yet satisfied
    COMPLETE = "complete"      # Condition satisfied, step is complete
    RETRY = "retry"            # Condition failed, retry the step
    ERROR = "error"            # Unrecoverable error, cannot proceed


class StoppingCondition(ABC):
    """Base abstract class for all stopping conditions"""
    
    def __init__(self, 
                 max_retries: int = 3, 
                 error_message: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """Initialize stopping condition with retry settings"""
        self.max_retries = max_retries
        self.error_message = error_message
        self.metadata = metadata or {}
        self._retry_count = 0
    
    @abstractmethod
    def evaluate(self, result: Any, context: 'PipelineContext') -> StoppingStatus:
        """
        Evaluate whether the condition is satisfied
        
        Args:
            result: The result to evaluate
            context: The pipeline context
            
        Returns:
            StoppingStatus indicating whether to continue, complete, retry, or error
        """
        pass
    
    def reset(self) -> None:
        """Reset internal state, including retry counter"""
        self._retry_count = 0
    
    def _increment_retry(self) -> bool:
        """
        Increment the retry counter and check if max retries exceeded
        
        Returns:
            True if retry is possible, False if max retries reached
        """
        self._retry_count += 1
        return self._retry_count <= self.max_retries


class CompletionStoppingCondition(StoppingCondition):
    """Simplest condition that completes after a single execution"""
    
    def evaluate(self, result: Any, context: 'PipelineContext') -> StoppingStatus:
        if result is None:
            if self._increment_retry():
                return StoppingStatus.RETRY
            return StoppingStatus.ERROR
        return StoppingStatus.COMPLETE


class JsonStoppingCondition(StoppingCondition):
    """Ensures result is valid JSON"""
    
    def __init__(self, 
                 schema: Optional[Dict[str, Any]] = None, 
                 required_keys: Optional[List[str]] = None,
                 **kwargs):
        """
        Initialize JSON validation stopping condition
        
        Args:
            schema: Optional JSON Schema for validation
            required_keys: List of keys that must exist in the JSON
            **kwargs: Additional parameters for StoppingCondition
        """
        super().__init__(**kwargs)
        self.schema = schema
        self.required_keys = required_keys or []
    
    def evaluate(self, result: Any, context) -> StoppingStatus:
        # Check if result is present
        if not result:
            if self._increment_retry():
                return StoppingStatus.RETRY
            return StoppingStatus.ERROR
        
        # Try to parse JSON
        try:
            # If already a dict, no need to parse
            if isinstance(result, dict):
                json_result = result
            else:
                # Try to find JSON in the text if it's a string
                if isinstance(result, str):
                    # Look for JSON structure in the text
                    json_pattern = r'(\{.*\}|\[.*\])'
                    match = re.search(json_pattern, result, re.DOTALL)
                    if match:
                        json_text = match.group(0)
                    else:
                        json_text = result
                    
                    json_result = json.loads(json_text)
                else:
                    # Unknown type
                    if self._increment_retry():
                        return StoppingStatus.RETRY
                    return StoppingStatus.ERROR
            
            # Check required keys
            for key in self.required_keys:
                if key not in json_result:
                    if self._increment_retry():
                        return StoppingStatus.RETRY
                    return StoppingStatus.ERROR
            
            # Validate against schema if provided
            if self.schema:
                # Schema validation would go here
                # For simplicity, not implementing full JSON Schema validation
                pass
            
            return StoppingStatus.COMPLETE
            
        except json.JSONDecodeError:
            if self._increment_retry():
                return StoppingStatus.RETRY
            return StoppingStatus.ERROR


class PydanticStoppingCondition(StoppingCondition):
    """Ensures result can be parsed as a specific Pydantic model"""
    
    def __init__(self, model_class: Type[BaseModel], **kwargs):
        """
        Initialize Pydantic model validation stopping condition
        
        Args:
            model_class: Pydantic model class to validate against
            **kwargs: Additional parameters for StoppingCondition
        """
        super().__init__(**kwargs)
        self.model_class = model_class
    
    def evaluate(self, result: Any, context) -> StoppingStatus:
        # Check if result is present
        if not result:
            if self._increment_retry():
                return StoppingStatus.RETRY
            return StoppingStatus.ERROR
        
        try:
            # If already the correct model instance, we're done
            if isinstance(result, self.model_class):
                return StoppingStatus.COMPLETE
            
            # Try to parse as JSON if it's a string
            if isinstance(result, str):
                try:
                    # Look for JSON structure in the text
                    json_pattern = r'(\{.*\}|\[.*\])'
                    match = re.search(json_pattern, result, re.DOTALL)
                    if match:
                        json_text = match.group(0)
                        parsed_dict = json.loads(json_text)
                    else:
                        # Try parsing the whole text as JSON
                        parsed_dict = json.loads(result)
                    
                    # Validate with Pydantic
                    self.model_class.parse_obj(parsed_dict)
                    return StoppingStatus.COMPLETE
                    
                except (json.JSONDecodeError, ValidationError):
                    if self._increment_retry():
                        return StoppingStatus.RETRY
                    return StoppingStatus.ERROR
            
            # If it's a dict, try direct Pydantic parsing
            elif isinstance(result, dict):
                try:
                    self.model_class.parse_obj(result)
                    return StoppingStatus.COMPLETE
                except ValidationError:
                    if self._increment_retry():
                        return StoppingStatus.RETRY
                    return StoppingStatus.ERROR
            
            # Unknown type
            if self._increment_retry():
                return StoppingStatus.RETRY
            return StoppingStatus.ERROR
            
        except Exception:
            if self._increment_retry():
                return StoppingStatus.RETRY
            return StoppingStatus.ERROR


class ContentMatchStoppingCondition(StoppingCondition):
    """Checks if the result contains specific patterns or text"""
    
    def __init__(self, 
                 patterns: List[Union[str, re.Pattern]], 
                 require_all: bool = False,
                 min_length: Optional[int] = None,
                 **kwargs):
        """
        Initialize content matching stopping condition
        
        Args:
            patterns: List of strings or regex patterns to match
            require_all: If True, all patterns must match; if False, any match is sufficient
            min_length: Minimum content length required
            **kwargs: Additional parameters for StoppingCondition
        """
        super().__init__(**kwargs)
        self.patterns = [
            pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, re.DOTALL)
            for pattern in patterns
        ]
        self.require_all = require_all
        self.min_length = min_length
    
    def evaluate(self, result: Any, context) -> StoppingStatus:
        # Check if result is present
        if not result:
            if self._increment_retry():
                return StoppingStatus.RETRY
            return StoppingStatus.ERROR
        
        # Convert to string if necessary
        content = str(result)
        
        # Check minimum length
        if self.min_length is not None and len(content) < self.min_length:
            if self._increment_retry():
                return StoppingStatus.RETRY
            return StoppingStatus.ERROR
        
        # Check patterns
        matches = [bool(pattern.search(content)) for pattern in self.patterns]
        
        if self.require_all and all(matches):
            return StoppingStatus.COMPLETE
        elif not self.require_all and any(matches):
            return StoppingStatus.COMPLETE
        
        # Retry if patterns don't match
        if self._increment_retry():
            return StoppingStatus.RETRY
        return StoppingStatus.ERROR


class CustomStoppingCondition(StoppingCondition):
    """Uses a custom function to evaluate stopping condition"""
    
    def __init__(self, 
                 evaluation_fn: Callable[[Any, 'PipelineContext'], StoppingStatus],
                 **kwargs):
        """
        Initialize custom stopping condition
        
        Args:
            evaluation_fn: Function that evaluates the result and returns a StoppingStatus
            **kwargs: Additional parameters for StoppingCondition
        """
        super().__init__(**kwargs)
        self.evaluation_fn = evaluation_fn
    
    def evaluate(self, result: Any, context) -> StoppingStatus:
        try:
            status = self.evaluation_fn(result, context)
            if status == StoppingStatus.RETRY and not self._increment_retry():
                return StoppingStatus.ERROR
            return status
        except Exception:
            if self._increment_retry():
                return StoppingStatus.RETRY
            return StoppingStatus.ERROR