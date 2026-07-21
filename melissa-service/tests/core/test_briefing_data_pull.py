import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models import Base, Goal

class FakeSemanticStore:
    def __init__(self):
        self.queries = []
    def query_memory(self, query: str, n_results: int = 5):
        self.queries.append(query)
        if "unfinished" in query:
            return ["finish writing the tests", "clean up the codebase"]
        if "priorities" in query:
            return ["launch the product today"]
        return []

@pytest.mark.asyncio
async def test_pull_briefing_data(monkeypatch):
    import app.core.briefing
    
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    monkeypatch.setattr(app.core.briefing, "SessionLocal", TestingSessionLocal)
    
    # 1. Setup active goals
    async with TestingSessionLocal() as session:
        session.add(Goal(description="Active goal 1", status="active"))
        session.add(Goal(description="Active goal 2", status="active"))
        session.add(Goal(description="Completed goal", status="completed"))
        await session.commit()
        
    # 2. Setup mock semantic store
    fake_store = FakeSemanticStore()
    monkeypatch.setattr(app.core.briefing, "global_semantic_store", fake_store)
    
    # 3. Pull data
    data = await app.core.briefing.pull_briefing_data()
    
    # 4. Verify
    assert "active_goals" in data
    assert len(data["active_goals"]) == 2
    assert data["active_goals"][0]["description"] == "Active goal 1"
    
    assert "unfinished_items" in data
    assert data["unfinished_items"] == ["finish writing the tests", "clean up the codebase"]
    
    assert "priorities" in data
    assert data["priorities"] == ["launch the product today"]
    
    assert len(fake_store.queries) == 2
