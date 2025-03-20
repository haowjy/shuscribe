# shuscribe/services/llm/pipeline/__init__.py

from shuscribe.services.llm.pipeline.base import PipelineContext
from shuscribe.services.llm.pipeline.flow import FlowControl, FlowDecision

from shuscribe.services.llm.pipeline.base_steps import (
    PipelineStep
)
from shuscribe.services.llm.pipeline.exceptions import (
    MaxIterationsExceededError
)

# Main pipeline class
class AdvancedPipeline:
    """Advanced pipeline with conditional branching and loops"""
    
    def __init__(self, name: str):
        """Initialize pipeline"""
        self.name = name
        self._steps = {}  # name -> step
        self._default_sequence = []  # Default step execution order
        self._branches = {}  # step_name -> [ConditionalBranch]
        self._max_iterations = {}  # step_name -> max iterations
        
    def add_step(self, step: PipelineStep) -> 'AdvancedPipeline':
        """Add a step to the pipeline"""
        step_name = step.get_name()
        if step_name in self._steps:
            raise ValueError(f"Step with name '{step_name}' already exists")
        
        self._steps[step_name] = step
        self._default_sequence.append(step_name)
        return self
        
    async def run(self, context: PipelineContext) -> PipelineContext:
        """Run the pipeline with flow control"""
        step_index = 0
        iteration_count = 0
        max_total_iterations = 1000  # Safety to prevent infinite loops
        
        while step_index < len(self._default_sequence) and iteration_count < max_total_iterations:
            iteration_count += 1
            
            # Get current step
            current_step_name = self._default_sequence[step_index]
            current_step = self._steps[current_step_name]
            
            # Track iterations for this specific step
            step_iterations = context.data.increment_iteration(current_step_name)
            max_step_iterations = self._max_iterations.get(current_step_name, 100)
            
            # Check if we've exceeded max iterations for this step
            if step_iterations > max_step_iterations:
                raise MaxIterationsExceededError(
                    f"Step '{current_step_name}' exceeded maximum iterations ({max_step_iterations})",
                    current_step_name
                )
            
            # Process the step
            step_context = context.with_step(current_step_name)
            import asyncio
            step_context.start_time = asyncio.get_event_loop().time()
            
            try:
                step_context = await current_step.process(step_context)
                step_context.end_time = asyncio.get_event_loop().time()
                context = step_context
            except Exception as e:
                context.metadata[f"{current_step_name}_error"] = str(e)
                context.flow_control = FlowControl.end()
                break
            
            # Use flow control from returned context
            flow_control = context.flow_control
            
            # Handle flow control decision
            if flow_control.decision == FlowDecision.CONTINUE:
                # Move to next step in sequence
                step_index += 1
                    
            elif flow_control.decision == FlowDecision.REPEAT:
                # Stay on current step (step_index doesn't change)
                pass
                
            elif flow_control.decision == FlowDecision.GOTO:
                if not flow_control.target_step:
                    raise ValueError("GOTO decision requires a target step")
                    
                if flow_control.target_step not in self._steps:
                    raise ValueError(f"Target step '{flow_control.target_step}' does not exist")
                    
                try:
                    step_index = self._default_sequence.index(flow_control.target_step)
                except ValueError:
                    raise ValueError(f"Target step '{flow_control.target_step}' is not in the sequence")
                    
            elif flow_control.decision == FlowDecision.END:
                # End pipeline execution
                break
        
        if iteration_count >= max_total_iterations:
            raise MaxIterationsExceededError(f"Pipeline exceeded maximum total iterations ({max_total_iterations})", self.name)
            
        return context