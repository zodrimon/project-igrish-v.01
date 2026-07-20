from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: List[Dict[str, Any]], stream: bool = True) -> AsyncGenerator[str, None]:
        """
        Generates a response from the LLM based on the provided messages.
        
        Args:
            messages: A list of message dictionaries (e.g., [{"role": "user", "content": "hello"}])
            stream: Whether to stream the response back as an async generator yielding text chunks.
            
        Returns:
            An async generator yielding string chunks of the response.
        """
        pass
