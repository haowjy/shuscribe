# shuscribe/services/llm/interfaces.py

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Sequence

from shuscribe.schemas.llm import Message, GenerationConfig
from shuscribe.schemas.streaming import StreamEvent
    
class StreamingProvider(ABC):
    @abstractmethod
    async def _stream_generate(
        self, 
        messages: Sequence[Message | str], 
        model: str, 
        config: GenerationConfig
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream generate text completions.
        
        Returns:
            An async generator that yields string chunks.
        """
        yield StreamEvent(
            type="in_progress",
            text="",
            usage=None,
        )  # This is just for type hinting, implementations will override



