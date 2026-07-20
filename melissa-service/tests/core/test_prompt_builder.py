import pytest
from app.core.prompt_builder import build_prompt, get_system_prompt

def test_build_prompt_basic():
    user_input = "Hello"
    messages = build_prompt(user_input)
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "Boss" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Hello"

def test_build_prompt_with_history():
    user_input = "What is the weather?"
    history = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello Boss"}
    ]
    messages = build_prompt(user_input, history)
    
    assert len(messages) == 4
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Hi"
    assert messages[2]["role"] == "assistant"
    assert messages[2]["content"] == "Hello Boss"
    assert messages[3]["role"] == "user"
    assert messages[3]["content"] == "What is the weather?"
