import pytest
import asyncio
from app.core.db import SessionLocal
from app.models import Goal, Base
from app.memory.context_aggregator import build_augmented_prompt, _get_structured_context
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

@pytest.mark.asyncio
async def test_structured_context(monkeypatch):
    import app.memory.context_aggregator
    
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    monkeypatch.setattr(app.memory.context_aggregator, "SessionLocal", TestingSessionLocal)
    
    async with TestingSessionLocal() as db:
        db.add(Goal(description="Finish AD lab tonight"))
        await db.commit()
        
    context = await _get_structured_context()
    assert len(context) > 0
    assert "Finish AD lab tonight" in context[0]

@pytest.mark.asyncio
async def test_build_augmented_prompt_with_snapshot(monkeypatch):
    from app.core.context_snapshot import global_context_snapshot
    from app.ports.sensor import ContextSensor
    
    class FakeSensor(ContextSensor):
        @property
        def name(self): return "active_window"
        def get_current_state(self, preferences=None): return {"title": "VS Code", "process": "Code.exe"}
        
    global_context_snapshot._sensors.clear()
    global_context_snapshot.register_sensor(FakeSensor())
    global_context_snapshot._update_snapshot()
    
    messages = await build_augmented_prompt("hello")
    # System prompt is the first message
    system_msg = messages[0]["content"]
    assert "Real-Time Context Snapshot:" in system_msg
    assert "[active_window]: {'title': 'VS Code', 'process': 'Code.exe'}" in system_msg
