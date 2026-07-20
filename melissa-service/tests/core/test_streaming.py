import pytest
import asyncio
from app.core.streaming import chunk_sentences

@pytest.mark.asyncio
async def test_chunk_sentences():
    async def fake_llm_stream():
        chunks = [
            "Hello", " there! ",
            "How ", "are you doing today?",
            " I am ", "fine. Thank ", "you."
        ]
        for c in chunks:
            yield c
            
    sentences = []
    async for sentence in chunk_sentences(fake_llm_stream()):
        sentences.append(sentence)
        
    assert len(sentences) == 4
    assert sentences[0] == "Hello there!"
    assert sentences[1] == "How are you doing today?"
    assert sentences[2] == "I am fine."
    assert sentences[3] == "Thank you."

@pytest.mark.asyncio
async def test_chunk_sentences_incomplete_end():
    async def fake_llm_stream():
        chunks = ["This is a sentence. And this is"]
        for c in chunks:
            yield c
            
    sentences = []
    async for sentence in chunk_sentences(fake_llm_stream()):
        sentences.append(sentence)
        
    assert len(sentences) == 2
    assert sentences[0] == "This is a sentence."
    assert sentences[1] == "And this is"
