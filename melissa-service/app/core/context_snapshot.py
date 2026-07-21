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
        self._active_seconds: float = 0.0
        
    def register_sensor(self, sensor: ContextSensor):
        self._sensors.append(sensor)
        
    def get_state(self) -> Dict[str, Any]:
        return dict(self._state)
        
    def _update_snapshot(self, prefs: Dict[str, str] = None):
        if prefs is None:
            prefs = {}
        new_state = {}
        for sensor in self._sensors:
            try:
                new_state[sensor.name] = sensor.get_current_state(prefs)
            except Exception as e:
                logger.error(f"Sensor {sensor.name} failed to update: {e}")
                
                
        idle_seconds = new_state.get("input_activity", {}).get("idle_seconds", 0)
        if idle_seconds < 10.0:
            if self._last_updated:
                self._active_seconds += (time.time() - self._last_updated)
        else:
            self._active_seconds = 0.0
            
        # Focus mode: > 60 seconds of continuous activity (idle < 10s)
        new_state["focus_mode"] = {
            "is_active": self._active_seconds > 60.0,
            "active_seconds": round(self._active_seconds, 1)
        }
                
        self._state = new_state
        self._last_updated = time.time()
        
    async def _poll_loop(self, interval_seconds: float):
        from app.core.db import SessionLocal
        from app.models import Preference
        from sqlalchemy import select

        while self._is_running:
            prefs = {}
            try:
                async with SessionLocal() as session:
                    result = await session.execute(select(Preference).where(Preference.key.like("sensor.%")))
                    for pref in result.scalars():
                        prefs[pref.key] = pref.value
            except Exception as e:
                logger.error(f"Failed to load preferences: {e}")

            self._update_snapshot(prefs)
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
