# shuscribe/schemas/provider.py

from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional, List, Dict

class ProviderName(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    # OPENROUTER = "openrouter"
    # GROQ = "groq"
    # COHERE = "cohere"

class LLMUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    
class LLMResponse(BaseModel):
    """Generic response model for any provider"""
    text: str
    model: str
    usage: LLMUsage
    raw_response: Any = Field(..., exclude=True)
    
    # Generic fields for various provider capabilities
    tool_calls: Optional[List[Dict[str, Any]]] = None
    citations: Optional[List[Dict[str, Any]]] = None
    media: Optional[List[Dict[str, Any]]] = None  # For generated images/videos
    context_id: Optional[str] = None  # For caching/context management
    class Config:
        json_encoders = {
            # Optionally, add custom JSON encoders if you decide to serialize other complex fields later
            # Example: You can serialize complex objects by converting them to strings
            # YourCustomType: lambda v: str(v),
        }