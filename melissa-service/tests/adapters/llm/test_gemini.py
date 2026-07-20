import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from app.adapters.llm.gemini_adapter import GeminiAdapter
from google.genai import types

@pytest.fixture
def mock_secrets():
    with patch("app.adapters.llm.gemini_adapter.get_secret", return_value="fake-api-key"):
        yield

@pytest.mark.asyncio
async def test_gemini_generate_non_streaming(mock_secrets):
    adapter = GeminiAdapter()
    
    with patch.object(adapter, 'client') as mock_client:
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        
        messages = [{"role": "system", "content": "system prompt"}, {"role": "user", "content": "hello"}]
        chunks = []
        async for chunk in adapter.generate(messages, stream=False):
            chunks.append(chunk)
            
        assert chunks == ["Test response"]
        
        # Verify the correct arguments were passed
        mock_client.aio.models.generate_content.assert_called_once()
        call_kwargs = mock_client.aio.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-2.5-flash"
        assert len(call_kwargs["contents"]) == 1
        assert call_kwargs["contents"][0]["role"] == "user"
        assert call_kwargs["contents"][0]["parts"][0]["text"] == "hello"
        assert call_kwargs["config"].system_instruction == "system prompt"

@pytest.mark.asyncio
async def test_gemini_generate_streaming(mock_secrets):
    adapter = GeminiAdapter()
    
    async def mock_stream(*args, **kwargs):
        async def inner_stream():
            for word in ["Test ", "response ", "stream"]:
                chunk = MagicMock()
                chunk.text = word
                yield chunk
        return inner_stream()
            
    with patch.object(adapter, 'client') as mock_client:
        mock_client.aio.models.generate_content_stream = mock_stream
        
        messages = [{"role": "user", "content": "hello"}]
        chunks = []
        async for chunk in adapter.generate(messages, stream=True):
            chunks.append(chunk)
            
        assert chunks == ["Test ", "response ", "stream"]
