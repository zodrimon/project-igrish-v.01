import asyncio
from typing import List, Dict, Any, AsyncGenerator
from app.ports.llm import LLMProvider

class MockLLMAdapter(LLMProvider):
    def __init__(self, mock_response: str = "This is a mock response from the LLM adapter."):
        self.mock_response = mock_response

    async def generate(self, messages: List[Dict[str, Any]], stream: bool = True) -> AsyncGenerator[str, None]:
        """
        Mock implementation of generate. Returns the mock response split into chunks.
        """
        words = self.mock_response.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            if stream:
                await asyncio.sleep(0.05) # simulate network latency
