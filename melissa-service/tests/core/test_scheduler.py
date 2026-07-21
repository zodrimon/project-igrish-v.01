import pytest
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models import Base, Preference
from app.core.scheduler import BriefingScheduler

class FakeSnapshotProvider:
    def __init__(self):
        self.state = {"input_activity": {"keys_pressed": 0, "mouse_moves": 0}}
        
    def get_state(self):
        return self.state
        
    def set_active(self):
        self.state["input_activity"]["keys_pressed"] = 10

@pytest.fixture
async def setup_db(monkeypatch):
    import app.core.scheduler
    
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    monkeypatch.setattr(app.core.scheduler, "SessionLocal", TestingSessionLocal)
    return TestingSessionLocal

@pytest.mark.asyncio
async def test_briefing_scheduler(monkeypatch):
    import app.core.scheduler
    
    # 1. Setup DB directly (like the other async tests)
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    monkeypatch.setattr(app.core.scheduler, "SessionLocal", TestingSessionLocal)
    
    provider = FakeSnapshotProvider()
    monkeypatch.setattr(app.core.scheduler, "global_context_snapshot", provider)
    
    scheduler = BriefingScheduler()
    
    # Not active yet, has not briefed today
    assert not await scheduler._has_briefed_today()
    assert not scheduler._is_user_active()
    
    # Make user active
    provider.set_active()
    assert scheduler._is_user_active()
    
    # Trigger logic manually (since loop is a continuous task)
    if not await scheduler._has_briefed_today():
        if scheduler._is_user_active():
            await scheduler._mark_briefed_today()
            
    assert await scheduler._has_briefed_today()
    
    # Check DB
    async with TestingSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(Preference).where(Preference.key == "last_briefing_date"))
        pref = result.scalar_one_or_none()
        assert pref is not None
        assert pref.value == date.today().isoformat()
        
    # Set DB to yesterday
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    async with TestingSessionLocal() as session:
        result = await session.execute(select(Preference).where(Preference.key == "last_briefing_date"))
        pref = result.scalar_one_or_none()
        pref.value = yesterday
        await session.commit()
        
    assert not await scheduler._has_briefed_today()
