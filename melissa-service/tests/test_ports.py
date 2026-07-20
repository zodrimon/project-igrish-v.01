import pytest
from app.ports.stt import MockSTTAdapter
from app.ports.tts import MockTTSAdapter

@pytest.mark.asyncio
async def test_mock_stt_adapter():
    adapter = MockSTTAdapter("hello test")
    result = await adapter.transcribe(b"fake audio")
    assert result == "hello test"

@pytest.mark.asyncio
async def test_mock_tts_adapter():
    adapter = MockTTSAdapter(b"hello audio")
    result = await adapter.synthesize("test text")
    assert result == b"hello audio"
