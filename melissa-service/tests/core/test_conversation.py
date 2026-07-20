import pytest
from app.core.conversation import ConversationBuffer

def test_conversation_buffer_add_turn():
    buffer = ConversationBuffer(max_turns=2)
    buffer.add_turn("hello", "hi boss")
    
    history = buffer.get_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "hi boss"

def test_conversation_buffer_max_turns():
    buffer = ConversationBuffer(max_turns=2)
    
    buffer.add_turn("turn 1", "resp 1")
    buffer.add_turn("turn 2", "resp 2")
    
    assert len(buffer.get_history()) == 4
    
    # Adding a 3rd turn should evict the 1st turn
    buffer.add_turn("turn 3", "resp 3")
    
    history = buffer.get_history()
    assert len(history) == 4
    assert history[0]["content"] == "turn 2"
    assert history[1]["content"] == "resp 2"
    assert history[2]["content"] == "turn 3"
    assert history[3]["content"] == "resp 3"

def test_conversation_buffer_clear():
    buffer = ConversationBuffer()
    buffer.add_turn("hello", "hi")
    buffer.clear()
    assert len(buffer.get_history()) == 0
