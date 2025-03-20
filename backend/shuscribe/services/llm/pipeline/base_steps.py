# shuscribe/services/llm/pipeline/base_steps.py

from abc import ABC, abstractmethod
from typing import Any, Union, Optional

from shuscribe.services.llm.pipeline.base import PipelineContext
from shuscribe.services.llm.pipeline.flow import FlowControl, FlowDecision
from shuscribe.services.llm.pipeline.conditions import StoppingCondition, StoppingStatus, CompletionStoppingCondition
from shuscribe.services.llm.pipeline.exceptions import MaxIterationsExceededError


class StepResult:
    """Result of a step execution, including evaluation status"""
    
    def __init__(self, 
                value: Any = None, 
                status: StoppingStatus = StoppingStatus.CONTINUE,
                error: Optional[Exception] = None,
                metadata: Optional[dict] = None):
        """Initialize step result"""
        self.value = value
        self.status = status
        self.error = error
        self.metadata = metadata or {}
    
    @property
    def is_complete(self) -> bool:
        """Check if the step is complete"""
        return self.status == StoppingStatus.COMPLETE
    
    @property
    def is_error(self) -> bool:
        """Check if the step encountered an error"""
        return self.status == StoppingStatus.ERROR
    
    @property
    def should_retry(self) -> bool:
        """Check if the step should be retried"""
        return self.status == StoppingStatus.RETRY
    
    @property
    def should_continue(self) -> bool:
        """Check if the step should continue processing"""
        return self.status == StoppingStatus.CONTINUE


class PipelineStep(ABC):
    """Base class for all pipeline steps"""
    
    def __init__(self, name: str):
        """Initialize pipeline step"""
        self.name = name
    
    @abstractmethod
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process the context and return updated context"""
        pass
    
    def get_name(self) -> str:
        """Get the name of the step"""
        return self.name


class EnhancedPipelineStep(PipelineStep):
    """Enhanced pipeline step with stopping condition support"""
    
    def __init__(self, 
                name: str,
                stopping_condition: Optional[StoppingCondition] = None,
                max_iterations: int = 10):
        """
        Initialize enhanced pipeline step
        
        Args:
            name: Name of the step
            stopping_condition: Condition that determines when the step is complete
            max_iterations: Maximum number of iterations to prevent infinite loops
        """
        super().__init__(name)
        self.stopping_condition = stopping_condition or CompletionStoppingCondition()
        self.max_iterations = max_iterations
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process the context with stopping condition evaluation"""
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Execute the core step logic
            try:
                result = await self.execute(context)
            except Exception as e:
                # Handle execution errors
                result = StepResult(
                    value=None,
                    status=StoppingStatus.ERROR,
                    error=e,
                    metadata={"iteration": iteration}
                )
            
            # If result is not a StepResult, wrap it
            if not isinstance(result, StepResult):
                result = StepResult(value=result)
            
            # Evaluate stopping condition if not already evaluated
            if result.status == StoppingStatus.CONTINUE:
                result.status = self.stopping_condition.evaluate(result.value, context)
            
            # Store the result in context
            context.data.set(f"{self.name}_result", result.value)
            context.data.set(f"{self.name}_status", result.status.value)
            
            # Check if we're done
            if result.is_complete:
                # Step completed successfully
                context.flow_control = FlowControl.continue_flow()
                break
                
            elif result.is_error:
                # Unrecoverable error
                error_msg = f"Step '{self.name}' failed with error: {result.error}" if result.error else f"Step '{self.name}' failed"
                context.metadata[f"{self.name}_error"] = error_msg
                # Decide what to do on error (could be customizable)
                context.flow_control = FlowControl.end()
                break
                
            elif result.should_retry:
                # Need to retry the step
                continue
                
            else:  # should_continue
                # Continue normal processing
                await self.continue_processing(context, result)
        
        # Check for max iterations exceeded
        if iteration >= self.max_iterations:
            error_msg = f"Step '{self.name}' exceeded maximum iterations ({self.max_iterations})"
            context.metadata[f"{self.name}_max_iterations_exceeded"] = True
            context.flow_control = FlowControl.end()
            raise MaxIterationsExceededError(error_msg, self.name)
        
        return context
    
    @abstractmethod
    async def execute(self, context: PipelineContext) -> Union[Any, StepResult]:
        """
        Execute the core step logic
        
        Args:
            context: The pipeline context
            
        Returns:
            Either a raw result or a StepResult
        """
        pass
    
    @abstractmethod
    async def continue_processing(self, context: PipelineContext, result: StepResult) -> None:
        """
        Handle continuing processing (when status is CONTINUE)
        
        Args:
            context: The pipeline context
            result: The current step result
        """
        # Default implementation just continues to the next iteration
        pass