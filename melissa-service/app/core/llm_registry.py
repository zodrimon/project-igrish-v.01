import logging
from typing import Optional
from app.ports.llm import LLMProvider
from app.adapters.llm.openai_adapter import OpenAIAdapter
from app.adapters.llm.claude_adapter import ClaudeAdapter
from app.adapters.llm.gemini_adapter import GeminiAdapter
from app.adapters.llm.mock import MockLLMAdapter
from app.core.secrets import get_secret

logger = logging.getLogger(__name__)

def get_llm_provider() -> LLMProvider:
    """
    Returns the active LLMProvider based on the LLM_PROVIDER setting.
    Falls back to mock if none specified or invalid.
    """
    provider = get_secret("LLM_PROVIDER") or "mock"
    model = get_secret("LLM_MODEL")
    
    logger.info(f"Initializing LLM Provider: {provider} (model: {model or 'default'})")
    
    provider = provider.lower()
    
    if provider == "openai":
        return OpenAIAdapter(model=model) if model else OpenAIAdapter()
    elif provider == "claude" or provider == "anthropic":
        return ClaudeAdapter(model=model) if model else ClaudeAdapter()
    elif provider == "gemini":
        return GeminiAdapter(model=model) if model else GeminiAdapter()
    else:
        if provider != "mock":
            logger.warning(f"Unknown LLM_PROVIDER '{provider}', falling back to mock.")
        return MockLLMAdapter()
