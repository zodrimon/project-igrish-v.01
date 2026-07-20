from abc import ABC, abstractmethod

class STTProvider(ABC):
    """Port for Speech-to-Text capabilities."""
    
    @abstractmethod
    async def transcribe(self, audio: bytes) -> str:
        """Transcribe raw audio bytes into text."""
        pass

class MockSTTAdapter(STTProvider):
    """A trivial mock implementation for testing."""
    
    def __init__(self, fixed_response: str = "mock transcription"):
        self.fixed_response = fixed_response

    async def transcribe(self, audio: bytes) -> str:
        return self.fixed_response
