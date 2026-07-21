import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.decision_loop import DecisionLoop
from app.models import Goal, Base
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
async def test_decision_loop_heuristics(monkeypatch):
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
    
    # 1. Setup a fake active goal
    async with TestingSessionLocal() as session:
        goal = Goal(description="Test goal", status="active")
        session.add(goal)
        await session.commit()
            
    # 2. Setup fake snapshot and decision loop
    provider = FakeSnapshotProvider()
    loop = DecisionLoop(snapshot_provider=provider, distraction_threshold_seconds=300.0)
    loop._classifier = FakeClassifier()
    
    # Not distraction -> no nudge
    provider.set_active_window("VS Code", "code")
    res = await loop.evaluate_heuristics()
    assert res is None
    
    # Distraction, but threshold not met yet (0 seconds elapsed)
    provider.set_active_window("Twitter", "timeline")
    res = await loop.evaluate_heuristics()
    assert res is None
    
    # Advance time by 100s (threshold is 300)
    current_time += 100.0
    res = await loop.evaluate_heuristics()
    assert res is None
    
    # Advance time to cross threshold
    current_time += 250.0
    res = await loop.evaluate_heuristics()
    assert res is not None
    assert res["nudge_type"] == "distraction"
    assert res["goal_description"] == "Test goal"
    assert res["app_name"] == "Twitter"
    
    # 3. Test Cooldown
    # If the loop triggers, it resets start_time, so let's log the nudge to cooldown
    await NudgeLogManager.log_nudge("distraction", "test content", cooldown_minutes=30)
    
    # Call once to set start_time again
    current_time += 10.0
    provider.set_active_window("Twitter", "timeline")
    await loop.evaluate_heuristics()
    
    # Advance time to cross threshold again
    current_time += 350.0
    res = await loop.evaluate_heuristics()
    
    # Should be None because of cooldown
    assert res is None
