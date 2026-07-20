import pytest
from unittest.mock import patch
from app.core.llm_registry import get_llm_provider
from app.adapters.llm.openai_adapter import OpenAIAdapter
from app.adapters.llm.claude_adapter import ClaudeAdapter
from app.adapters.llm.gemini_adapter import GeminiAdapter
from app.adapters.llm.mock import MockLLMAdapter

def test_get_llm_provider_openai():
    with patch("app.core.llm_registry.get_secret", side_effect=lambda k: "openai" if k == "LLM_PROVIDER" else "fake-key"):
        with patch("app.adapters.llm.openai_adapter.get_secret", return_value="fake-key"):
            provider = get_llm_provider()
            assert isinstance(provider, OpenAIAdapter)

def test_get_llm_provider_claude():
    with patch("app.core.llm_registry.get_secret", side_effect=lambda k: "claude" if k == "LLM_PROVIDER" else "fake-key"):
        with patch("app.adapters.llm.claude_adapter.get_secret", return_value="fake-key"):
            provider = get_llm_provider()
            assert isinstance(provider, ClaudeAdapter)

def test_get_llm_provider_gemini():
    with patch("app.core.llm_registry.get_secret", side_effect=lambda k: "gemini" if k == "LLM_PROVIDER" else "fake-key"):
        with patch("app.adapters.llm.gemini_adapter.get_secret", return_value="fake-key"):
            provider = get_llm_provider()
            assert isinstance(provider, GeminiAdapter)

def test_get_llm_provider_mock_fallback():
    with patch("app.core.llm_registry.get_secret", side_effect=lambda k: "unknown" if k == "LLM_PROVIDER" else None):
        provider = get_llm_provider()
        assert isinstance(provider, MockLLMAdapter)
        
def test_get_llm_provider_with_model():
    with patch("app.core.llm_registry.get_secret", side_effect=lambda k: "openai" if k == "LLM_PROVIDER" else ("custom-model" if k == "LLM_MODEL" else "fake-key")):
        with patch("app.adapters.llm.openai_adapter.get_secret", return_value="fake-key"):
            provider = get_llm_provider()
            assert isinstance(provider, OpenAIAdapter)
            assert provider.model == "custom-model"
