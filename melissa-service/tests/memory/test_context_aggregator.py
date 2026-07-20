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
