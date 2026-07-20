import pytest
from app.adapters.sensors.process_list import ProcessListSensor

def test_process_list_sensor():
    sensor = ProcessListSensor()
    assert sensor.name == "running_processes"
    
    state = sensor.get_current_state()
    assert isinstance(state, dict)
    assert "count" in state
    assert "processes" in state
    assert isinstance(state["processes"], list)
    assert state["count"] == len(state["processes"])
    
    # We should have at least the python process running the test
    assert state["count"] > 0
    assert any("python" in proc.lower() for proc in state["processes"])
