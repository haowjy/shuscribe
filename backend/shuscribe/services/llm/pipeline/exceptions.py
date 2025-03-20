# shuscribe/services/llm/pipeline/exceptions.py

from typing import Optional

class PipelineException(Exception):
    """Base exception for pipeline errors"""
    
    def __init__(self, message: str, step_name: Optional[str] = None):
        self.message = message
        self.step_name = step_name
        super().__init__(f"Pipeline error in step '{step_name}': {message}" if step_name else message)


class StepExecutionError(PipelineException):
    """Exception raised when a step fails to execute"""
    pass


class StoppingConditionError(PipelineException):
    """Exception raised when a stopping condition fails"""
    pass


class MaxIterationsExceededError(PipelineException):
    """Exception raised when a step exceeds its maximum iterations"""
    pass