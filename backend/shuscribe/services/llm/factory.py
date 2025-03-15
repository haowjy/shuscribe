# shuscribe/services/llm/factory.py

from typing import Type, Dict
from shuscribe.services.llm.providers.provider import LLMProvider

def get_provider_class(provider_name: str) -> Type[LLMProvider]:
    """
    Get the provider class by name.
    
    Args:
        provider_name: Name of the provider (e.g., 'openai', 'anthropic', 'gemini')
        
    Returns:
        Provider class that can be instantiated
        
    Raises:
        ValueError: If provider is not supported
    """
    from shuscribe.services.llm.providers.openai_provider import OpenAIProvider
    from shuscribe.services.llm.providers.anthropic_provider import AnthropicProvider
    from shuscribe.services.llm.providers.gemini_provider import GeminiProvider
    
    providers: Dict[str, Type[LLMProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
    }
    
    if provider_name not in providers:
        raise ValueError(f"Provider '{provider_name}' not supported. Available providers: {', '.join(providers.keys())}")
    
    return providers[provider_name]