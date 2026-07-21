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
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                tmp.write(audio)
                tmp_path = tmp.name
                
            try:
                segments, _ = self.model.transcribe(tmp_path, beam_size=5)
                text = "".join([segment.text for segment in segments]).strip()
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            return text
            
        # Run the CPU-bound transcription in a separate thread
        text = await asyncio.to_thread(_transcribe_sync)
        return text
