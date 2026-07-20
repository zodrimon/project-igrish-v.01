import io
import wave
import asyncio
from typing import AsyncGenerator
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

    async def synthesize_stream(self, text_stream: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        """Synthesize a stream of text chunks into a continuous WAV stream."""
        # For simplicity, we yield a dummy WAV header first, then PCM chunks.
        # This allows the client to stream the audio continuously.
        first_chunk_yielded = False
        
        async for sentence in text_stream:
            def _synthesize_sentence_sync():
                chunks = []
                for chunk in self.voice.synthesize(sentence):
                    chunks.append(chunk)
                return chunks
                
            audio_chunks = await asyncio.to_thread(_synthesize_sentence_sync)
            
            for chunk in audio_chunks:
                if not first_chunk_yielded:
                    # Yield WAV header
                    with io.BytesIO() as wav_io:
                        with wave.open(wav_io, "wb") as wav_file:
                            wav_file.setnchannels(chunk.sample_channels)
                            wav_file.setsampwidth(chunk.sample_width)
                            wav_file.setframerate(chunk.sample_rate)
                            # Write dummy frame to force header generation
                            wav_file.writeframes(b'\x00' * (chunk.sample_channels * chunk.sample_width))
                        header = wav_io.getvalue()
                        # The standard wave module writes the actual data size. 
                        # To trick the browser, we should ideally patch the size, 
                        # but often just sending the header followed by PCM works for simple players.
                        # Let's patch the size in the RIFF header to 0xFFFFFFFF
                        patched_header = header[:4] + b'\xff\xff\xff\xff' + header[8:40] + b'\xff\xff\xff\xff' + header[44:]
                        yield patched_header
                    first_chunk_yielded = True
                    
                yield chunk.audio_int16_bytes
