from typing import List, Dict, Any, AsyncGenerator
from anthropic import AsyncAnthropic
from app.ports.llm import LLMProvider
from app.core.secrets import get_secret

class ClaudeAdapter(LLMProvider):
    def __init__(self, model: str = "claude-3-5-sonnet-20240620"):
        self.model = model
        api_key = get_secret("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in secrets")
        self.client = AsyncAnthropic(api_key=api_key)

    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Ensure messages have valid roles (Anthropic expects 'user' or 'assistant')
        return [{"role": msg["role"], "content": msg["content"]} for msg in messages if msg["role"] in ["user", "assistant"]]
        
    def _extract_system_prompt(self, messages: List[Dict[str, Any]]) -> str:
        system_messages = [msg["content"] for msg in messages if msg["role"] == "system"]
        return "\n".join(system_messages)

    async def generate(self, messages: List[Dict[str, Any]], stream: bool = True) -> AsyncGenerator[str, None]:
        system_prompt = self._extract_system_prompt(messages)
        anthropic_messages = self._convert_messages(messages)
        
        if stream:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=anthropic_messages
            ) as stream_response:
                async for text in stream_response.text_stream:
                    yield text
        else:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=anthropic_messages
            )
            yield response.content[0].text
