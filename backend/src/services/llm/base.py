# backend/src/services/llm/base.py
"""
Base LLM interfaces and abstractions
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

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


# We remove LLMProvider ABC here, as LLMService directly uses Portkey
# and handles provider specifics.

class LLMConfig(BaseModel):
    """Configuration for LLM requests (internal use)"""
    provider: str  # 'openai', 'anthropic', etc.
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    additional_params: Dict[str, Any] = {}