import pytest
from app.core.fact_extractor import extract_facts
from app.core.db import SessionLocal
from app.models import Goal, Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

# We can mock the LLMProvider to test extract_facts logic
class MockLLMProvider:
    async def generate(self, messages, stream=False):
        prompt = messages[0]["content"]
        if "finish my AD lab tonight" in prompt:
            yield '[{"type": "goal", "content": "Finish AD lab tonight"}]'
        elif "what's the weather" in prompt:
            yield '[]'
        else:
            yield '[]'

@pytest.mark.asyncio
async def test_fact_extraction(monkeypatch):
    import app.core.fact_extractor
    monkeypatch.setattr(app.core.fact_extractor, "get_llm_provider", lambda: MockLLMProvider())
    
    # Needs a real DB for test
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    monkeypatch.setattr(app.core.fact_extractor, "SessionLocal", TestingSessionLocal)
    
    # Test positive case
    await extract_facts("I want to finish my AD lab tonight")
    
    async with TestingSessionLocal() as db:
        result = await db.execute(select(Goal))
        goals = result.scalars().all()
        assert len(goals) == 1
        assert goals[0].description == "Finish AD lab tonight"
        
    # Test neutral case
    await extract_facts("what's the weather like?")
    
    async with TestingSessionLocal() as db:
        result = await db.execute(select(Goal))
        goals = result.scalars().all()
        assert len(goals) == 1 # Still just 1 from before
