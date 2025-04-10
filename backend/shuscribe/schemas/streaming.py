# shuscribe/schemas/stream.py

from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal, Optional, List, Dict, Any, TextIO

import yaml
from shuscribe.schemas.provider import LLMUsage

# Define the StreamStatus enum
class StreamStatus(str, Enum):
    """Enum representing the possible states of a streaming session."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETE = "complete"
    ERROR = "error"

class StreamEvent(BaseModel):
    """Pydantic model representing an event in a streaming session."""
    type: Literal["in_progress", "complete", "error"]
    text: str = Field(default="")
    error: Optional[str] = None
    usage: Optional[LLMUsage] = None # only populated for the final chunk

# Define the StreamChunk model
class StreamChunk(BaseModel):
    """Pydantic model representing a chunk of streamed data."""
    status: StreamStatus
    session_id: str
    
    text: str = Field(default="")
    accumulated_text: str = Field(default="")
    usage: Optional[LLMUsage] = None # only populated for the final chunk
    
    error: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list) # TODO
    metadata: Dict[str, Any] = Field(default_factory=dict) # TODO
    