"""
Core data models for LLM interactions (inputs and outputs).
"""
from typing import Any, Dict, Optional

from pydantic import BaseModel


class LLMMessage(BaseModel):
    """Standard message format for LLM interactions"""
    role: str  # 'system', 'user', 'assistant'
    content: str


class LLMResponse(BaseModel):
    """Standard response format from LLM providers"""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None 