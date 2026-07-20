from typing import List, Dict, Any, AsyncGenerator
from google import genai
from google.genai import types
from app.ports.llm import LLMProvider
from app.core.secrets import get_secret

class GeminiAdapter(LLMProvider):
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.model = model
        api_key = get_secret("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in secrets")
        self.client = genai.Client(api_key=api_key)

    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Gemini expects 'user' or 'model' roles
        gemini_messages = []
        for msg in messages:
            if msg["role"] == "system":
                continue # System instructions are passed separately in Config
            role = "user" if msg["role"] == "user" else "model"
            gemini_messages.append({"role": role, "parts": [{"text": msg["content"]}]})
        return gemini_messages
        
    def _extract_system_prompt(self, messages: List[Dict[str, Any]]) -> str:
        system_messages = [msg["content"] for msg in messages if msg["role"] == "system"]
        return "\n".join(system_messages)

    async def generate(self, messages: List[Dict[str, Any]], stream: bool = True) -> AsyncGenerator[str, None]:
        system_prompt = self._extract_system_prompt(messages)
        gemini_messages = self._convert_messages(messages)
        
        config_kwargs = {}
        if system_prompt:
            config_kwargs["system_instruction"] = system_prompt
            
        config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

        if stream:
            # We use async streaming
            response_stream = await self.client.aio.models.generate_content_stream(
                model=self.model,
                contents=gemini_messages,
                config=config
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        else:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=gemini_messages,
                config=config
            )
            yield response.text or ""
