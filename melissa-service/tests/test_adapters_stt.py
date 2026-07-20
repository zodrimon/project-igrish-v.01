import os
import pytest
from app.adapters.stt.whisper import WhisperSTTAdapter

@pytest.mark.asyncio
async def test_whisper_adapter_transcribe():
    adapter = WhisperSTTAdapter(model_size="tiny", device="cpu", compute_type="int8")
    
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "hello.mp3")
    with open(fixture_path, "rb") as f:
        audio_bytes = f.read()
        
    text = await adapter.transcribe(audio_bytes)
    
    # Check if 'hello' is in the transcription (ignoring case and punctuation)
    # gTTS generated "hello world"
    normalized_text = text.lower().replace(".", "").replace(",", "").strip()
    assert "hello" in normalized_text
