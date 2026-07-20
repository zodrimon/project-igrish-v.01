from typing import List, Dict, Any, AsyncGenerator
from openai import AsyncOpenAI
from app.ports.llm import LLMProvider
from app.core.secrets import get_secret

class OpenAIAdapter(LLMProvider):
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        api_key = get_secret("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in secrets")
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(self, messages: List[Dict[str, Any]], stream: bool = True) -> AsyncGenerator[str, None]:
        if stream:
            stream_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            async for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            yield response.choices[0].message.content or ""
