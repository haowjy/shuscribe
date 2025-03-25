# # shuscribe/services/llm/pipeline/base_pipeline.py

# import os
# import asyncio
# import logging
# import time
# import json
# from typing import AsyncGenerator, Dict, List, Optional, Any, Type, TypeVar, Generic, Union
# from abc import ABC, abstractmethod
# from pathlib import Path
# from datetime import datetime

# from shuscribe.schemas.streaming import StreamChunk, StreamStatus
# from shuscribe.services.llm.session import LLMSession
# from shuscribe.schemas.provider import LLMUsage

# logger = logging.getLogger(__name__)

# T = TypeVar('T')
# StepResult = TypeVar('StepResult')
# StepInput = TypeVar('StepInput')

# class PipelineStep(Generic[StepInput, StepResult], ABC):
#     """Base class for a pipeline step that can process data in streaming or non-streaming mode."""
    
#     def __init__(self, name: str):
#         self.name = name
#         self.retries = 3  # Default retry count
#         self._cached_result: Optional[StepResult] = None
        
#     @abstractmethod
#     async def process(self, input_data: StepInput, stream: bool = False) -> StepResult:
#         """Process the input data and return the result."""
#         pass
    
#     @abstractmethod
#     async def process_stream(self, input_data: StepInput) -> AsyncGenerator[StreamChunk, None]:
#         """Process the input data and yield stream chunks."""
#         pass
    
#     async def execute(self, input_data: StepInput, stream: bool = False) -> Union[StepResult, AsyncGenerator[StreamChunk, None]]:
#         """Execute the step with retry logic."""
#         if stream:
#             return self.process_stream(input_data)
        
#         for attempt in range(self.retries):
#             try:
#                 result = await self.process(input_data, stream=False)
#                 self._cached_result = result
#                 return result
#             except Exception as e:
#                 if attempt < self.retries - 1:
#                     delay = (attempt + 1) * 2  # Simple exponential backoff
#                     logger.error(f"Step '{self.name}' failed (attempt {attempt+1}/{self.retries}): {str(e)}. Retrying in {delay}s...")
#                     await asyncio.sleep(delay)
#                 else:
#                     logger.error(f"Step '{self.name}' failed after {self.retries} attempts: {str(e)}")
#                     raise
    
#     def save_result(self, result: StepResult, output_dir: Path, filename: str) -> Path:
#         """Save the step result to a file."""
#         os.makedirs(output_dir, exist_ok=True)
#         output_path = output_dir / filename
        
#         # If the result is a Pydantic model, use its json serialization
#         if hasattr(result, "model_dump_json"):
#             with open(output_path, "w") as f:
#                 f.write(result.model_dump_json(indent=2))
#         # If it's a StreamChunk
#         elif isinstance(result, StreamChunk):
#             with open(output_path, "w") as f:
#                 f.write(result.model_dump_json(indent=2))
#         # Otherwise use standard JSON serialization
#         else:
#             with open(output_path, "w") as f:
#                 json.dump(result, f, indent=2)
        
#         return output_path
    
#     def load_result(self, input_path: Path, result_class: Optional[Type[StepResult]] = None) -> Optional[StepResult]:
#         """Load a previously saved result."""
#         if not input_path.exists():
#             return None
        
#         try:
#             with open(input_path, "r") as f:
#                 content = f.read()
            
#             if result_class:
#                 if hasattr(result_class, "model_validate_json"):
#                     return result_class.model_validate_json(content)
#                 elif hasattr(result_class, "parse_raw"):
#                     return result_class.parse_raw(content)
            
#             # Default JSON loading
#             return json.loads(content)
#         except Exception as e:
#             logger.error(f"Failed to load result from {input_path}: {str(e)}")
#             return None


# class LLMPipelineStep(PipelineStep[StepInput, StepResult]):
#     """A pipeline step that uses an LLM for processing."""
    
#     def __init__(self, name: str, provider_name: str, model: str):
#         super().__init__(name)
#         self.provider_name = provider_name
#         self.model = model
#         self.usage: Optional[LLMUsage] = None
    
#     async def process_stream(self, input_data: StepInput) -> AsyncGenerator[StreamChunk, None]:
#         """Process using the LLM in streaming mode."""
#         # This needs to be implemented by subclasses
#         raise NotImplementedError("Streaming not implemented for this step")
    
#     async def generate_with_llm(self, messages: List[Any], config=None, stream: bool = False):
#         """Helper method to generate content using the LLM."""
#         async with LLMSession.session_scope() as session:
#             if stream:
#                 async for chunk in session.generate_stream(
#                     provider_name=self.provider_name,
#                     model=self.model,
#                     messages=messages,
#                     config=config
#                 ):
#                     yield chunk
#                     # Store usage if available
#                     if chunk.usage:
#                         self.usage = chunk.usage
#             else:
#                 response = await session.generate(
#                     provider_name=self.provider_name,
#                     model=self.model,
#                     messages=messages,
#                     config=config
#                 )
#                 self.usage = response.usage
#                 return response


# class Pipeline:
#     """Base pipeline class that executes a series of steps."""
    
#     def __init__(self, name: str, output_dir: Optional[Path] = None):
#         self.name = name
#         self.steps: List[PipelineStep] = []
#         self.output_dir = output_dir or Path(f"./pipeline_outputs/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
#         self.results: Dict[str, Any] = {}
    
#     def add_step(self, step: PipelineStep) -> "Pipeline":
#         """Add a step to the pipeline."""
#         self.steps.append(step)
#         return self
    
#     async def execute(self, initial_input: Any = None, start_from_step: int = 0, stream: bool = False) -> Dict[str, Any]:
#         """Execute all pipeline steps."""
#         current_input = initial_input
#         os.makedirs(self.output_dir, exist_ok=True)
        
#         # Create a metadata file for this pipeline run
#         metadata = {
#             "pipeline_name": self.name,
#             "start_time": datetime.now().isoformat(),
#             "steps": [step.name for step in self.steps],
#             "stream_mode": stream
#         }
        
#         with open(self.output_dir / "pipeline_metadata.json", "w") as f:
#             json.dump(metadata, f, indent=2)
        
#         # Execute each step
#         for i, step in enumerate(self.steps[start_from_step:], start=start_from_step):
#             logger.info(f"Executing step {i+1}/{len(self.steps)}: {step.name}")
#             step_start_time = time.time()
            
#             try:
#                 if stream:
#                     # In streaming mode, we need to collect all chunks to pass to the next step
#                     chunks = []
#                     async for chunk in await step.execute(current_input, stream=True):
#                         # Pass the chunk to any listeners (could be UI updates)
#                         self._emit_stream_chunk(step.name, chunk)
#                         chunks.append(chunk)
                    
#                     # For the next step, use the last complete chunk
#                     complete_chunks = [c for c in chunks if c.status == StreamStatus.COMPLETE]
#                     if complete_chunks:
#                         result = complete_chunks[-1]
#                     else:
#                         result = chunks[-1] if chunks else None
#                 else:
#                     # In non-streaming mode, just wait for the result
#                     result = await step.execute(current_input, stream=False)
                
#                 # Save the result
#                 if result:
#                     result_path = step.save_result(
#                         result, 
#                         self.output_dir, 
#                         f"step_{i}_{step.name}.json"
#                     )
#                     logger.info(f"Step {step.name} result saved to {result_path}")
                
#                 # Store the result for the pipeline output
#                 self.results[step.name] = result
                
#                 # Update the input for the next step
#                 current_input = result
                
#                 # Log completion
#                 elapsed = time.time() - step_start_time
#                 logger.info(f"Step {step.name} completed in {elapsed:.2f}s")
                
#             except Exception as e:
#                 logger.error(f"Pipeline failed at step {step.name}: {str(e)}")
#                 # Update metadata with failure information
#                 metadata["end_time"] = datetime.now().isoformat()
#                 metadata["status"] = "failed"
#                 metadata["failed_step"] = step.name
#                 metadata["error"] = str(e)
                
#                 with open(self.output_dir / "pipeline_metadata.json", "w") as f:
#                     json.dump(metadata, f, indent=2)
                
#                 raise
        
#         # Update metadata with success information
#         metadata["end_time"] = datetime.now().isoformat()
#         metadata["status"] = "completed"
        
#         with open(self.output_dir / "pipeline_metadata.json", "w") as f:
#             json.dump(metadata, f, indent=2)
        
#         return self.results
    
#     def load_step_result(self, step_index: int, result_class=None) -> Any:
#         """Load a previously saved step result."""
#         step = self.steps[step_index]
#         result_path = self.output_dir / f"step_{step_index}_{step.name}.json"
#         return step.load_result(result_path, result_class)
    
#     def _emit_stream_chunk(self, step_name: str, chunk: StreamChunk):
#         """Handle streaming output. Override this in subclasses to implement UI updates."""
#         # By default, just log the chunk
#         if chunk.text:
#             logger.debug(f"[{step_name}] {chunk.text}")