import io
import asyncio
from typing import Optional
from faster_whisper import WhisperModel
from app.ports.stt import STTProvider

class WhisperSTTAdapter(STTProvider):
    """STT Adapter using faster-whisper."""
    
    def __init__(self, model_size: str = "tiny.en", device: str = "cpu", compute_type: str = "int8"):
        # Load the model synchronously on initialization
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    async def transcribe(self, audio: bytes) -> str:
        """Transcribe raw audio bytes into text.
        
        Uses asyncio.to_thread to avoid blocking the event loop.
        """
        def _transcribe_sync():
            # faster-whisper can accept a file-like object
            audio_stream = io.BytesIO(audio)
            segments, _ = self.model.transcribe(audio_stream, beam_size=5)
            # segments is a generator, so we need to iterate to get the text
            return "".join([segment.text for segment in segments]).strip()
            
        # Run the CPU-bound transcription in a separate thread
        text = await asyncio.to_thread(_transcribe_sync)
        return text
