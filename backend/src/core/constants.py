# backend/src/core/constants.py
"""
Application constants and enums
"""

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