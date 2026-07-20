import pytest
from app.adapters.sensors.active_window import ActiveWindowSensor

def test_active_window_sensor():
    sensor = ActiveWindowSensor()
    assert sensor.name == "active_window"
    
    state = sensor.get_current_state()
    # It might run headless or without a foreground window, so we just verify the structure
    assert isinstance(state, dict)
    assert "title" in state
    assert "process" in state
    # Either it gets the window or returns None if no foreground window exists
