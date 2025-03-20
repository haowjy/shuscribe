# shuscribe/services/llm/pipeline/base.py

from typing import Dict, List, Any, Optional, Type, TypeVar
from pydantic import BaseModel

from shuscribe.services.llm.pipeline.flow import FlowControl

T = TypeVar('T', bound=BaseModel)

class PipelineData:
    """Generic container for all data passed between pipeline steps."""
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._iteration_counters: Dict[str, int] = {}
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in the pipeline data"""
        self._data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the pipeline data"""
        return self._data.get(key, default)
    
    def get_typed(self, model_class: Type[T]) -> Optional[T]:
        """Get a value as a specific type"""
        key = model_class.__name__
        value = self._data.get(key)
        if value is None:
            return None
        if isinstance(value, model_class):
            return value
        return model_class.model_validate(value) if isinstance(value, dict) else None
    
    def set_model(self, model: BaseModel) -> None:
        """Set a model in the pipeline data using its class name as key"""
        self._data[model.__class__.__name__] = model
    
    def has(self, key: str) -> bool:
        """Check if a key exists in the pipeline data"""
        return key in self._data
    
    def keys(self) -> List[str]:
        """Get all keys in the pipeline data"""
        return list(self._data.keys())
    
    def increment_iteration(self, step_name: str) -> int:
        """Increment the iteration counter for a step"""
        count = self._iteration_counters.get(step_name, 0) + 1
        self._iteration_counters[step_name] = count
        return count
    
    def get_iteration_count(self, step_name: str) -> int:
        """Get the current iteration count for a step"""
        return self._iteration_counters.get(step_name, 0)
    
    def reset_iteration(self, step_name: str) -> None:
        """Reset the iteration counter for a step"""
        self._iteration_counters[step_name] = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all data to a dictionary"""
        result = {}
        for key, value in self._data.items():
            if hasattr(value, "dict") and callable(value.dict):
                result[key] = value.dict()
            else:
                result[key] = value
        return result


class PipelineContext:
    """Context that's passed between pipeline steps"""
    
    def __init__(self, 
                 workflow_id: str,
                 step_id: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """Initialize pipeline context"""
        self.workflow_id: str = workflow_id
        self.step_id: Optional[str] = step_id
        self.metadata: Dict[str, Any] = metadata or {}
        self.data: PipelineData = PipelineData()
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.flow_control: FlowControl = FlowControl()
        
    def with_step(self, step_id: str) -> 'PipelineContext':
        """Create a new context for a specific step"""
        context = PipelineContext(
            workflow_id=self.workflow_id,
            step_id=step_id,
            metadata=self.metadata.copy()
        )
        context.data = self.data  # Share the same data object
        return context