import io
import wave
import asyncio
from piper import PiperVoice
from app.ports.tts import TTSProvider
from huggingface_hub import hf_hub_download

class PiperTTSAdapter(TTSProvider):
    """TTS Adapter using Piper TTS."""

    def __init__(self, repo_id: str = "rhasspy/piper-voices", 
                 model_file: str = "en/en_US/lessac/low/en_US-lessac-low.onnx",
                 config_file: str = "en/en_US/lessac/low/en_US-lessac-low.onnx.json"):
        # Download (or get from cache) the model and config
        self.model_path = hf_hub_download(repo_id=repo_id, filename=model_file)
        self.config_path = hf_hub_download(repo_id=repo_id, filename=config_file)
        
        # Load the voice synchronously on initialization
        self.voice = PiperVoice.load(self.model_path, config_path=self.config_path)

    async def synthesize(self, text: str) -> bytes:
        """Synthesize text into raw audio bytes (WAV format)."""
        def _synthesize_sync():
            with io.BytesIO() as wav_io:
                with wave.open(wav_io, "wb") as wav_file:
                    first = True
                    for chunk in self.voice.synthesize(text):
                        if first:
                            wav_file.setnchannels(chunk.sample_channels)
                            wav_file.setsampwidth(chunk.sample_width)
                            wav_file.setframerate(chunk.sample_rate)
                            first = False
                        wav_file.writeframes(chunk.audio_int16_bytes)
                return wav_io.getvalue()
                
        # Run CPU-bound synthesis in a separate thread
        audio_bytes = await asyncio.to_thread(_synthesize_sync)
        return audio_bytes
