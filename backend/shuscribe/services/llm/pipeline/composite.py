# shuscribe/services/llm/pipeline/composite.py

import asyncio
from typing import List, Dict, Any

from shuscribe.services.llm.pipeline.base import PipelineContext
from shuscribe.services.llm.pipeline.base_steps import PipelineStep, EnhancedPipelineStep
from shuscribe.services.llm.pipeline.flow import FlowControl


class CompositeParallelStep(PipelineStep):
    """
    A step that executes multiple steps in parallel,
    waiting for all stopping conditions to be satisfied
    """
    
    def __init__(self, 
                 name: str, 
                 steps: List[EnhancedPipelineStep],
                 max_concurrency: int = 5,
                 fail_fast: bool = True):
        """Initialize composite parallel step"""
        super().__init__(name)
        self.steps = steps
        self.max_concurrency = max_concurrency
        self.fail_fast = fail_fast
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process all steps in parallel with controlled concurrency"""
        # Create a semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrency)
        
        # Create a dictionary to store tasks and their metadata
        tasks = {}
        step_contexts = {}
        
        # Start executing steps with semaphore control
        for step in self.steps:
            # Create a context for this specific step
            step_context = context.with_step(step.name)
            step_contexts[step.name] = step_context
            
            # Create and store the task
            tasks[step.name] = {
                'task': asyncio.create_task(self._execute_step_with_semaphore(step, step_context, semaphore)),
                'started_at': asyncio.get_event_loop().time(),
                'completed_at': None,
                'error': None
            }
        
        # Wait for all tasks to complete
        pending = [task_info['task'] for task_info in tasks.values()]
        
        while pending:
            # Wait for at least one task to complete
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            
            # Process completed tasks
            for done_task in done:
                # Find which step this task belongs to
                step_name = None
                for name, task_info in tasks.items():
                    if task_info['task'] == done_task:
                        step_name = name
                        break
                
                if step_name:
                    # Update task metadata
                    tasks[step_name]['completed_at'] = asyncio.get_event_loop().time()
                    
                    # Check for errors
                    try:
                        # Get the result but don't do anything with it yet
                        done_task.result()
                    except Exception as e:
                        tasks[step_name]['error'] = e
                        
                        # Handle failure in fail-fast mode
                        if self.fail_fast:
                            # Cancel all pending tasks
                            for pending_task in pending:
                                pending_task.cancel()
                            pending = []
                            break
        
        # All tasks have completed or been cancelled
        # Consolidate results
        consolidated_context = self._consolidate_results(context, tasks, step_contexts)
        
        # Check if any steps failed
        errors = [info['error'] for info in tasks.values() if info['error'] is not None]
        if errors:
            consolidated_context.flow_control = FlowControl.end()
            consolidated_context.metadata[f"{self.name}_failed"] = True
            # Store first error for reference
            consolidated_context.metadata[f"{self.name}_error"] = str(errors[0])
        else:
            consolidated_context.flow_control = FlowControl.continue_flow()
        
        return consolidated_context
    
    async def _execute_step_with_semaphore(self, 
                                          step: EnhancedPipelineStep, 
                                          step_context: PipelineContext,
                                          semaphore: asyncio.Semaphore) -> None:
        """Execute a step with semaphore control"""
        async with semaphore:
            await step.process(step_context)
    
    def _consolidate_results(self, 
                            original_context: PipelineContext,
                            tasks: Dict[str, Dict],
                            step_contexts: Dict[str, PipelineContext]) -> PipelineContext:
        """Consolidate results from all steps into a single context"""
        # Create a new context with the original metadata
        consolidated = PipelineContext(
            workflow_id=original_context.workflow_id,
            step_id=self.name,
            metadata=original_context.metadata.copy()
        )
        
        # Copy original data
        for key in original_context.data.keys():
            consolidated.data.set(key, original_context.data.get(key))
        
        # Add each step's data and metadata to the consolidated context
        for step_name, task_info in tasks.items():
            step_context = step_contexts.get(step_name)
            if not step_context:
                continue
            
            # Calculate duration
            duration = None
            if task_info['started_at'] and task_info['completed_at']:
                duration = task_info['completed_at'] - task_info['started_at']
            
            # Add execution metadata
            consolidated.metadata[f"{step_name}_duration"] = duration
            consolidated.metadata[f"{step_name}_success"] = task_info['error'] is None
            
            if task_info['error']:
                consolidated.metadata[f"{step_name}_error"] = str(task_info['error'])
                continue
            
            # Only copy results from successful steps
            if not task_info['error']:
                # Copy step result
                result_value = step_context.data.get(f"{step_name}_result")
                if result_value is not None:
                    consolidated.data.set(f"{step_name}_result", result_value)
                
                # Copy step status
                status = step_context.data.get(f"{step_name}_status")
                if status is not None:
                    consolidated.data.set(f"{step_name}_status", status)
        
        return consolidated