import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from app.adapters.llm.claude_adapter import ClaudeAdapter

@pytest.fixture
def mock_secrets():
    with patch("app.adapters.llm.claude_adapter.get_secret", return_value="fake-api-key"):
        yield

@pytest.mark.asyncio
async def test_claude_generate_non_streaming(mock_secrets):
    adapter = ClaudeAdapter()
    
    # Mock the AsyncAnthropic client
    with patch.object(adapter, 'client') as mock_client:
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Test response"
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        
        messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "hello"}]
        chunks = []
        async for chunk in adapter.generate(messages, stream=False):
            chunks.append(chunk)
            
        assert chunks == ["Test response"]
        mock_client.messages.create.assert_called_once_with(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            system="You are a helpful assistant.",
            messages=[{"role": "user", "content": "hello"}]
        )

@pytest.mark.asyncio
async def test_claude_generate_streaming(mock_secrets):
    adapter = ClaudeAdapter()
    
    # Mock the streaming response
    class MockStreamResponse:
        def __init__(self):
            self.text_stream = self._stream()
            
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
        async def _stream(self):
            for word in ["Test ", "response ", "stream"]:
                yield word
                
    with patch.object(adapter, 'client') as mock_client:
        mock_client.messages.stream.return_value = MockStreamResponse()
        
        messages = [{"role": "user", "content": "hello"}]
        chunks = []
        async for chunk in adapter.generate(messages, stream=True):
            chunks.append(chunk)
            
        assert chunks == ["Test ", "response ", "stream"]
        mock_client.messages.stream.assert_called_once_with(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            system="",
            messages=[{"role": "user", "content": "hello"}]
        )
