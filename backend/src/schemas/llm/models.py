"""
Core data models for LLM interactions (inputs and outputs).
"""
from typing import Any, Dict, Optional
from enum import Enum

from pydantic import BaseModel


class LLMMessage(BaseModel):
    """Standard message format for LLM interactions"""
    role: str  # 'system', 'user', 'assistant'
    content: str


class ChunkType(str, Enum):
    """Type of content in a streaming chunk"""
    THINKING = "thinking"  # Model's reasoning process
    CONTENT = "content"    # Actual response content
    UNKNOWN = "unknown"    # Default when type cannot be determined


class ThinkingEffort(str, Enum):
    """Level of thinking/reasoning for LLM models that support thinking modes"""
    LOW = "low"        # Minimal reasoning
    MEDIUM = "medium"  # Moderate reasoning
    HIGH = "high"      # Deep reasoning
    AUTO = "auto"      # Let the model decide the appropriate level


class LLMResponse(BaseModel):
    """Standard response format from LLM providers"""
    content: str
    model: str
    chunk_type: ChunkType = ChunkType.UNKNOWN  # Type of chunk for streaming responses
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None 