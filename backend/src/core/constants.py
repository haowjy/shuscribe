# backend/src/core/constants.py
"""
Application constants and enums
"""
from enum import Enum


class ProcessingStatus(str, Enum):
    """Story processing status"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING" 
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SubscriptionTier(str, Enum):
    """User subscription tiers"""
    FREE_BYOK = "free_byok"
    PREMIUM = "premium"


class WikiEntityType(str, Enum):
    """Types of wiki entities"""
    CHARACTER = "character"
    LOCATION = "location"
    FACTION = "faction"
    EVENT = "event"
    TERMINOLOGY = "terminology"
    ITEM = "item"


# Popular providers (for UI/validation, not exhaustive)
POPULAR_LLM_PROVIDERS = [
    "openai",
    "anthropic", 
    "google",
    "cohere",
    "mistral",
    "together",
    "groq",
    "azure-openai",
    "bedrock",
    "vertex-ai"
]

# Default configurations for popular providers
DEFAULT_PROVIDER_CONFIGS = {
    "openai": {
        "default_model": "gpt-4.1-nano",
        "models": ["gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "gpt-4o", "gpt-4o-mini", "o3", "o4-mini"]
    },
    "anthropic": {
        "default_model": "claude-3-5-haiku-20241022",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"]
    },
    "google": {
        "default_model": "gemini-1.5-flash",
        "models": ["gemini-2.0-flash-lite", "gemini-1.5-pro", "gemini-1.5-flash"]
    }
}
