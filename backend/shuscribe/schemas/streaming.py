# shuscribe/schemas/stream.py

from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal, Optional, List, Dict, Any
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
    type: Literal["in_progress", "complete", "error"]
    text: str
    usage: Optional[LLMUsage] = None # only populated for the final chunk

# Define the StreamChunk model
class StreamChunk(BaseModel):
    """Pydantic model representing a chunk of streamed data."""
    event: StreamEvent
    accumulated_text: str = Field(default="")
    session_id: str
    status: StreamStatus
    error: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list) # TODO
    metadata: Dict[str, Any] = Field(default_factory=dict) # TODO