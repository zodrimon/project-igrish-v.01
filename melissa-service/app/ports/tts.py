from abc import ABC, abstractmethod

class TTSProvider(ABC):
    """Port for Text-to-Speech capabilities."""
    
    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        """Synthesize text into raw audio bytes."""
        pass

class MockTTSAdapter(TTSProvider):
    """A trivial mock implementation for testing."""
    
    def __init__(self, fixed_audio: bytes = b"mock audio"):
        self.fixed_audio = fixed_audio

    async def synthesize(self, text: str) -> bytes:
        return self.fixed_audio
