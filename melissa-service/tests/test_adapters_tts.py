import pytest
from app.adapters.tts.piper import PiperTTSAdapter

@pytest.mark.asyncio
async def test_piper_adapter_synthesize():
    # Use the default lightweight model
    adapter = PiperTTSAdapter()
    
    audio_bytes = await adapter.synthesize("Hello world.")
    
    # Check that we received some bytes
    assert audio_bytes is not None
    assert len(audio_bytes) > 0
    # Check for WAV header "RIFF"
    assert audio_bytes.startswith(b"RIFF")
