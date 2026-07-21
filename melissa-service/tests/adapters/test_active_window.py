import pytest
from app.adapters.sensors.active_window import ActiveWindowSensor

def test_active_window_sensor():
    sensor = ActiveWindowSensor()
    assert sensor.name == "active_window"
    
    state = sensor.get_current_state()
    # It might run headless or without a foreground window, so we just verify the structure
    assert isinstance(state, dict)
    assert "window_title" in state
    assert "process_name" in state
    assert "category" in state
