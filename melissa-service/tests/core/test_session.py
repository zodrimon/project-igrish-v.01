import pytest
import asyncio
from app.core.session import SessionManager
from app.core.conversation import global_conversation_buffer

@pytest.mark.asyncio
async def test_session_lifecycle():
    # Setup
    global_conversation_buffer.clear()
    global_conversation_buffer.add_turn("hi", "hello")
    assert len(global_conversation_buffer.get_history()) == 2
    
    manager = SessionManager(timeout_seconds=0.1)
    await manager.ping()
    assert manager._is_active is True
    
    # Wait less than timeout, should still be active
    await asyncio.sleep(0.05)
    await manager.ping() # Reset timeout
    assert manager._is_active is True
    assert len(global_conversation_buffer.get_history()) == 2
    
    # Wait for timeout
    await asyncio.sleep(0.15)
    assert manager._is_active is False
    assert len(global_conversation_buffer.get_history()) == 0
