"""
WikiGen Schemas

Pydantic schemas for WikiGen agent inputs and outputs.
Provides type safety, validation, and JSON schema generation for structured outputs.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class Arc(BaseModel):
    """Individual story arc with metadata"""
    model_config = ConfigDict(extra='forbid')
    
    id: int = Field(..., ge=1, description="Arc number (starting from 1)")
    title: str = Field(..., min_length=1, description="Descriptive title for this arc")
    start_chapter: int = Field(..., ge=1, description="First chapter number in this arc")
    end_chapter: int = Field(..., ge=1, description="Last chapter number in this arc")
    summary: str = Field(..., min_length=10, description="Brief summary of this arc's narrative content")
    key_events: str = Field(..., min_length=5, description="Major plot points and character developments")
    is_finalized: bool = Field(
        default=True,
        description="Indicates if an arc's end is definitive. Set to false if it ends on a chunk boundary and might be extended by the next chunk of the story."
    )
    
    def model_post_init(self, __context: Any) -> None:
        """Validate that end_chapter >= start_chapter"""
        if self.end_chapter < self.start_chapter:
            raise ValueError(f"end_chapter ({self.end_chapter}) must be >= start_chapter ({self.start_chapter})")


class StoryStats(BaseModel):
    """Story analysis statistics"""
    model_config = ConfigDict(extra='forbid')


class ArcAnalysisResult(BaseModel):
    """Complete arc analysis result with validation"""
    model_config = ConfigDict(extra='forbid')
    
    # New fields for story prediction and growth analysis (required for better schema compatibility)
    story_prediction: str = Field(
        ..., 
        min_length=50, 
        description="Analysis of likely future story developments and plot directions"
    )
    growth_assessment: str = Field(
        ...,
        min_length=20,
        description="Assessment of how the story is likely to expand and evolve"
    )
    arc_strategy: str = Field(..., min_length=10, description="Explanation of the arc division approach")
    arcs: List[Arc] = Field(..., min_length=1, description="List of identified arcs")
    
    def model_post_init(self, __context: Any) -> None:
        """Validate arc consistency and coverage"""
        # Sort arcs by start chapter for validation
        sorted_arcs = sorted(self.arcs, key=lambda a: a.start_chapter)
        
        # Validate no gaps or overlaps
        for i in range(len(sorted_arcs) - 1):
            current = sorted_arcs[i]
            next_arc = sorted_arcs[i + 1]
            
            if current.end_chapter >= next_arc.start_chapter:
                raise ValueError(
                    f"Arc overlap: Arc {current.id} ends at chapter {current.end_chapter}, "
                    f"but Arc {next_arc.id} starts at chapter {next_arc.start_chapter}"
                )
            
            if current.end_chapter + 1 != next_arc.start_chapter:
                raise ValueError(
                    f"Arc gap: Arc {current.id} ends at chapter {current.end_chapter}, "
                    f"but Arc {next_arc.id} starts at chapter {next_arc.start_chapter}"
                )


# JSON Schema generation for structured outputs
def get_arc_analysis_schema() -> Dict[str, Any]:
    """Get JSON schema for ArcAnalysisResult for use with structured outputs"""
    return ArcAnalysisResult.model_json_schema()


# Example usage and schema preview
if __name__ == "__main__":
    import json
    
    schema = get_arc_analysis_schema()
    print("JSON Schema for ArcAnalysisResult:")
    print(json.dumps(schema, indent=2)) 