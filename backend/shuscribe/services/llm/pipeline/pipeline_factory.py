from enum import Enum
from typing import Optional

from shuscribe.schemas.pipeline import WikiGenPipelineConfig
from shuscribe.services.llm.pipeline.base_pipeline import Pipeline
from shuscribe.services.llm.pipeline.pipelines.wikigen import WikiGenerationPipeline

class PipelineType(str, Enum):
    """Enum for different pipeline types"""
    WIKI_GEN = "wiki_gen"

class PipelineFactory:
    """Factory class for creating different types of pipelines"""
    
    @staticmethod
    def create_pipeline(
        pipeline_type: PipelineType,
        session_id: str,
        pipeline_id: str,
        config: WikiGenPipelineConfig
    ) -> Pipeline:
        """
        Create a pipeline instance based on the specified type
        
        Args:
            pipeline_type: Type of pipeline to create
            session_id: Session ID for the pipeline
            pipeline_id: Pipeline ID for tracking
            config: Configuration for the pipeline
            
        Returns:
            An instance of the requested pipeline type
            
        Raises:
            ValueError: If the pipeline type is not supported
        """
        if pipeline_type == PipelineType.WIKI_GEN:
            return WikiGenerationPipeline(session_id, pipeline_id, config)
        else:
            raise ValueError(f"Unsupported pipeline type: {pipeline_type}")
