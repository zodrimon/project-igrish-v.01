import pytest
import asyncio
from app.adapters.llm.mock import MockLLMAdapter

@pytest.mark.asyncio
async def test_mock_llm_adapter_streaming():
    adapter = MockLLMAdapter(mock_response="Hello Boss")
    
    messages = [{"role": "user", "content": "test"}]
    
    chunks = []
    async for chunk in adapter.generate(messages, stream=True):
        chunks.append(chunk)
        
    result = "".join(chunks)
    assert result == "Hello Boss"
    assert chunks == ["Hello ", "Boss"]
