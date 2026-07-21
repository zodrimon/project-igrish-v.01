import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.decision_loop import DecisionLoop
from app.models import Goal, Base, Preference
from app.memory.nudge_log import NudgeLogManager

class FakeSnapshotProvider:
    def __init__(self):
        self.state = {}
        
    def get_state(self):
        return self.state
        
    def set_active_window(self, app_name, window_title):
        self.state["active_window"] = {
            "app_name": app_name,
            "window_title": window_title
        }

class FakeClassifier:
    def classify(self, app_name, window_title):
        if app_name == "Twitter":
            return "distraction"
        return "coding"

@pytest.mark.asyncio
async def test_decision_loop_settings(monkeypatch):
    import app.core.decision_loop
    import app.memory.nudge_log
    
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    monkeypatch.setattr(app.core.decision_loop, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(app.memory.nudge_log, "SessionLocal", TestingSessionLocal)
    
    current_time = 1000.0
    def mock_time():
        return current_time
    monkeypatch.setattr(app.core.decision_loop.time, "time", mock_time)
    
    async with TestingSessionLocal() as session:
        goal = Goal(description="Test goal", status="active")
        session.add(goal)
        await session.commit()
            
    provider = FakeSnapshotProvider()
    loop = DecisionLoop(snapshot_provider=provider, distraction_threshold_seconds=100.0)
    loop._classifier = FakeClassifier()
    
    # 1. Test "off" sensitivity
    async with TestingSessionLocal() as session:
        session.add(Preference(key="nudge.sensitivity", value="off"))
        await session.commit()
        
    provider.set_active_window("Twitter", "timeline")
    await loop.evaluate_heuristics() # Start timer
    current_time += 150.0 # Pass threshold
    res = await loop.evaluate_heuristics()
    assert res is None # Should be blocked by "off"
    
    # 2. Test "gentle" sensitivity (threshold doubled)
    async with TestingSessionLocal() as session:
        from sqlalchemy import update
        await session.execute(update(Preference).where(Preference.key == "nudge.sensitivity").values(value="gentle"))
        await session.commit()
        
    provider.set_active_window("Twitter", "timeline")
    await loop.evaluate_heuristics() # Start timer
    current_time += 150.0 # Pass normal threshold (100s)
    res = await loop.evaluate_heuristics()
    assert res is None # Should be blocked because gentle threshold is 200s
    
    current_time += 60.0 # Total 210s
    res = await loop.evaluate_heuristics()
    assert res is not None # Now it should trigger
    assert res["nudge_type"] == "distraction"
    
    # Reset cooldown manually for the test
    async with TestingSessionLocal() as session:
        from sqlalchemy import text
        await session.execute(text("DELETE FROM nudge_log"))
        await session.commit()
        
    # 3. Test mute categories
    async with TestingSessionLocal() as session:
        await session.execute(update(Preference).where(Preference.key == "nudge.sensitivity").values(value="normal"))
        session.add(Preference(key="nudge.mute_categories", value="distraction, social"))
        await session.commit()
        
    provider.set_active_window("Twitter", "timeline")
    await loop.evaluate_heuristics() # Start timer
    current_time += 150.0
    res = await loop.evaluate_heuristics()
    assert res is None # Blocked by mute_categories
