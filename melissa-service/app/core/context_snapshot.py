from typing import Dict, Any, List
from app.ports.sensor import ContextSensor
import time
import asyncio
import logging

logger = logging.getLogger(__name__)

class ContextSnapshot:
    """
    Holds a short-lived snapshot of the user's environment (e.g., active window, screen text).
    Sensors update this periodically.
    Raw data is NOT persisted to the database.
    """
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._sensors: List[ContextSensor] = []
        self._last_updated: float = 0.0
        self._poll_task = None
        self._is_running = False
        
    def register_sensor(self, sensor: ContextSensor):
        self._sensors.append(sensor)
        
    def get_state(self) -> Dict[str, Any]:
        return dict(self._state)
        
    def _update_snapshot(self):
        new_state = {}
        for sensor in self._sensors:
            try:
                new_state[sensor.name] = sensor.get_current_state()
            except Exception as e:
                logger.error(f"Sensor {sensor.name} failed to update: {e}")
                
        self._state = new_state
        self._last_updated = time.time()
        
    async def _poll_loop(self, interval_seconds: float):
        while self._is_running:
            self._update_snapshot()
            await asyncio.sleep(interval_seconds)
            
    def start(self, interval_seconds: float = 2.0):
        if self._is_running:
            return
        self._is_running = True
        self._poll_task = asyncio.create_task(self._poll_loop(interval_seconds))
        
    def stop(self):
        self._is_running = False
        if self._poll_task and not self._poll_task.done():
            self._poll_task.cancel()
            
global_context_snapshot = ContextSnapshot()
