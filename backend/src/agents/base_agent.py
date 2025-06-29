"""
Base Agent Class

Provides common functionality for all WikiGen agents including:
- Default provider and model configuration
- LLM service integration
- Common parameter handling
- Error handling patterns
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Type, Union, AsyncIterator
from uuid import UUID
from pydantic import BaseModel

from src.services.llm.llm_service import LLMService
from src.schemas.llm.models import LLMResponse


class BaseAgent(ABC):
    """
    Base class for all WikiGen agents.
    
    Provides default model configuration and common LLM interaction patterns.
    """
    
    def __init__(
        self, 
        llm_service: LLMService,
        default_provider: str = "google",
        default_model: str = "gemini-2.0-flash-001",
        **kwargs
    ):
        """
        Initialize base agent with LLM service and default model configuration.
        
        Args:
            llm_service: LLM service for making API calls
            default_provider: Default LLM provider ID (e.g., 'openai', 'anthropic')
            default_model: Default model name for this agent
            **kwargs: Additional agent-specific configuration
        """
        self.llm_service = llm_service
        self.default_provider = default_provider
        self.default_model = default_model
        
        # Store additional configuration
        self.config = kwargs
        
        # Validate that the default model is available
        self._validate_default_model()
    
    def _validate_default_model(self) -> None:
        """
        Validate that the configured default model is available.
        
        Raises:
            ValueError: If the default model is not found in the LLM catalog
        """
        model_instance = LLMService.get_hosted_model_details(
            self.default_provider, 
            self.default_model
        )
        
        if not model_instance:
            available_models = LLMService.get_hosted_models_for_provider(self.default_provider)
            model_names = [m.model_name for m in available_models] if available_models else []
            
            raise ValueError(
                f"Default model '{self.default_model}' not found for provider '{self.default_provider}'. "
                f"Available models: {model_names}"
            )
    
    def _get_model_params(
        self, 
        provider: Optional[str] = None, 
        model: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Get provider and model, using defaults if not specified.
        
        Args:
            provider: Optional provider override
            model: Optional model override
            
        Returns:
            Tuple of (provider, model) to use
        """
        return (
            provider or self.default_provider,
            model or self.default_model
        )
    
    async def _make_llm_call(
        self,
        messages: list,
        user_id: UUID,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        stream: bool = False,
        response_format: Optional[Type[BaseModel]] = None,
        **llm_kwargs
    ) -> Union[LLMResponse, AsyncIterator[LLMResponse]]:
        """
        Make an LLM call with consistent error handling and streaming support.
        
        Args:
            messages: List of LLMMessage objects
            user_id: User making the request
            api_key: Optional API key (for direct usage)
            provider: Optional provider override
            model: Optional model override
            stream: Whether to return streaming response
            response_format: Optional pydantic model type for structured output
            **llm_kwargs: Additional LLM parameters
            
        Returns:
            LLMResponse object for non-streaming, AsyncIterator[LLMResponse] for streaming
            
        Examples:
            # Non-streaming
            response = await self._make_llm_call(messages, user_id, stream=False)
            # response is LLMResponse
            
            # Streaming  
            response = await self._make_llm_call(messages, user_id, stream=True)
            # response is AsyncIterator[LLMResponse]
            async for chunk in response:
                print(chunk.content)
        """
        final_provider, final_model = self._get_model_params(provider, model)
        
        try:
            response = await self.llm_service.chat_completion(
                provider=final_provider,
                model=final_model,
                messages=messages,
                user_id=user_id,
                api_key=api_key,
                stream=stream,
                response_format=response_format,
                **llm_kwargs
            )
            
            return response
            
        except Exception as e:
            # Add context to the error
            raise RuntimeError(
                f"{self.__class__.__name__} LLM call failed "
                f"(provider={final_provider}, model={final_model}): {e}"
            ) from e
    
    @property
    def agent_name(self) -> str:
        """Get the agent name for logging and debugging."""
        return self.__class__.__name__
    
    def get_config(self) -> Dict[str, Any]:
        """Get agent configuration including defaults."""
        return {
            "agent_name": self.agent_name,
            "default_provider": self.default_provider,
            "default_model": self.default_model,
            "config": self.config
        }
    
    @abstractmethod
    async def execute(self, *args, **kwargs):
        """
        Main execution method for the agent.
        
        Each agent must implement this method with its specific functionality.
        """
        pass
