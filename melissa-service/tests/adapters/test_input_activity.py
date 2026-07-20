import pytest
from app.adapters.sensors.input_activity import InputActivitySensor

def test_input_activity_sensor():
    sensor = InputActivitySensor()
    assert sensor.name == "input_activity"
    
    state = sensor.get_current_state()
    assert isinstance(state, dict)
    assert "idle_seconds" in state
    assert "is_active" in state
    assert isinstance(state["idle_seconds"], float)
    assert isinstance(state["is_active"], bool)
    assert state["idle_seconds"] >= 0
