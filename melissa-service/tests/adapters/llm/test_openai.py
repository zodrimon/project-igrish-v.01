import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from app.adapters.llm.openai_adapter import OpenAIAdapter

@pytest.fixture
def mock_secrets():
    with patch("app.adapters.llm.openai_adapter.get_secret", return_value="fake-api-key"):
        yield

@pytest.mark.asyncio
async def test_openai_generate_non_streaming(mock_secrets):
    adapter = OpenAIAdapter()
    
    # Mock the AsyncOpenAI client
    with patch.object(adapter, 'client') as mock_client:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        messages = [{"role": "user", "content": "hello"}]
        chunks = []
        async for chunk in adapter.generate(messages, stream=False):
            chunks.append(chunk)
            
        assert chunks == ["Test response"]
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4o",
            messages=messages,
            stream=False
        )

@pytest.mark.asyncio
async def test_openai_generate_streaming(mock_secrets):
    adapter = OpenAIAdapter()
    
    # Mock the streaming response
    async def mock_stream():
        for word in ["Test ", "response ", "stream"]:
            chunk = MagicMock()
            chunk.choices = [MagicMock()]
            chunk.choices[0].delta.content = word
            yield chunk
            
    with patch.object(adapter, 'client') as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=mock_stream())
        
        messages = [{"role": "user", "content": "hello"}]
        chunks = []
        async for chunk in adapter.generate(messages, stream=True):
            chunks.append(chunk)
            
        assert chunks == ["Test ", "response ", "stream"]
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4o",
            messages=messages,
            stream=True
        )
