import pytest
import asyncio
from app.ports.sensor import ContextSensor
from app.core.context_snapshot import ContextSnapshot

class FakeSensor(ContextSensor):
    def __init__(self, name):
        self._name = name
        self.state_val = "initial"
        
    @property
    def name(self):
        return self._name
        
    def get_current_state(self):
        return {"val": self.state_val}

@pytest.mark.asyncio
async def test_context_snapshot_polling():
    snapshot = ContextSnapshot()
    sensor1 = FakeSensor("fake1")
    snapshot.register_sensor(sensor1)
    
    snapshot.start(interval_seconds=0.1)
    
    # Should be empty before first poll or immediately after start
    # wait for first poll
    await asyncio.sleep(0.15)
    
    state = snapshot.get_state()
    assert state == {"fake1": {"val": "initial"}}
    
    # Update fake sensor
    sensor1.state_val = "updated"
    
    # Wait for next poll
    await asyncio.sleep(0.15)
    
    state = snapshot.get_state()
    assert state == {"fake1": {"val": "updated"}}
    
    snapshot.stop()
