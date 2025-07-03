# backend/src/core/constants.py
"""
Application constants and enums
"""

# These are simple lists for UI/validation, not tied to detailed model configs directly here.
from typing import Literal


PROVIDER_ID = Literal[
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

MODEL_NAME = Literal[
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "o3",
    "o4-mini",
    "gemini-2.5-pro",
    "gemini-2.5-pro-preview-05-06",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite-preview-06-17",
    "gemini-2.0-flash-001",
    "claude-opus-4-20250514",
    "claude-sonnet-4-20250514",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-latest",
]