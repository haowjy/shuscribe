# shuscribe/services/llm/interfaces.py

from abc import ABC, abstractmethod
from typing import List, AsyncGenerator

from shuscribe.schemas.llm import Message, GenerationConfig
class StreamingProvider(ABC):
    @abstractmethod
    async def _stream_generate(
        self, 
        messages: List[Message | str], 
        model: str, 
        config: GenerationConfig
    ) -> AsyncGenerator[str, None]:
        """Stream generate text completions.
        
        Returns:
            An async generator that yields string chunks.
        """
        yield ""  # This is just for type hinting, implementations will override



