import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.memory.nudge_log import NudgeLogManager
from app.models import NudgeLog, Base

@pytest.mark.asyncio
async def test_nudge_log_cooldown(monkeypatch):
    import app.memory.nudge_log
    
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    monkeypatch.setattr(app.memory.nudge_log, "SessionLocal", TestingSessionLocal)
    
    nudge_type = "hydration"
    
    # Initially not on cooldown
    is_cooldown = await NudgeLogManager.is_on_cooldown(nudge_type)
    assert not is_cooldown
    
    # Log a nudge with 30 min cooldown
    await NudgeLogManager.log_nudge(nudge_type, "Drink water!", cooldown_minutes=30)
    
    # Should now be on cooldown
    is_cooldown = await NudgeLogManager.is_on_cooldown(nudge_type)
    assert is_cooldown
    
    # Manually backdate the log entry to simulate time passing
    async with TestingSessionLocal() as session:
        past_time = datetime.now(timezone.utc) - timedelta(minutes=40)
        await session.execute(
            update(NudgeLog)
            .where(NudgeLog.nudge_type == nudge_type)
            .values(cooldown_until=past_time)
        )
        await session.commit()
        
    # Should no longer be on cooldown
    is_cooldown = await NudgeLogManager.is_on_cooldown(nudge_type)
    assert not is_cooldown
