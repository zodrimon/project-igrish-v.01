import pytest
from app.adapters.sensors.system_state import SystemStateSensor

def test_system_state_sensor():
    sensor = SystemStateSensor()
    assert sensor.name == "system_state"
    
    # Initialize CPU percentage
    sensor.get_current_state()
    
    state = sensor.get_current_state()
    assert isinstance(state, dict)
    assert "cpu_percent" in state
    assert "memory_percent" in state
    assert isinstance(state["cpu_percent"], float)
    assert isinstance(state["memory_percent"], float)
    assert 0.0 <= state["cpu_percent"] <= 100.0
    assert 0.0 <= state["memory_percent"] <= 100.0
