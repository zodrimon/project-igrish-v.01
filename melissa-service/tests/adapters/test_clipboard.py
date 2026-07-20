import pytest
from app.adapters.sensors.clipboard import ClipboardSensor

def test_clipboard_sensor_disabled():
    sensor = ClipboardSensor(enabled=False)
    assert sensor.name == "clipboard"
    state = sensor.get_current_state()
    assert state["enabled"] is False
    assert state["content"] is None

def test_clipboard_sensor_enabled():
    sensor = ClipboardSensor(enabled=True)
    state = sensor.get_current_state()
    assert state["enabled"] is True
    # Content could be anything, just ensure it's in the dict
    assert "content" in state
