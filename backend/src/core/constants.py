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


# These are simple lists for UI/validation, not tied to detailed model configs directly here.
POPULAR_LLM_PROVIDERS = [
    "openai",
    "anthropic", 
    "google",
    # Add others that are commonly supported by Portkey and generally popular
    "cohere",
    "mistral",
    "together",
    "groq",
    "azure-openai",
    "bedrock",
    "vertex-ai"
]