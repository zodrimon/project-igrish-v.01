import asyncio
from datetime import date
import logging
from sqlalchemy import select
from app.core.db import SessionLocal
from app.models import Preference
from app.core.context_snapshot import global_context_snapshot

logger = logging.getLogger(__name__)

class BriefingScheduler:
    def __init__(self, check_interval_seconds: float = 60.0):
        self.check_interval_seconds = check_interval_seconds
        self._is_running = False
        self._task = None
        
    async def _has_briefed_today(self) -> bool:
        async with SessionLocal() as session:
            result = await session.execute(select(Preference).where(Preference.key == "last_briefing_date"))
            pref = result.scalar_one_or_none()
            today_str = date.today().isoformat()
            if pref and pref.value == today_str:
                return True
            return False
            
    async def _mark_briefed_today(self):
        async with SessionLocal() as session:
            today_str = date.today().isoformat()
            result = await session.execute(select(Preference).where(Preference.key == "last_briefing_date"))
            pref = result.scalar_one_or_none()
            if pref:
                pref.value = today_str
            else:
                session.add(Preference(key="last_briefing_date", value=today_str))
            await session.commit()
            
    def _is_user_active(self) -> bool:
        snapshot = global_context_snapshot.get_state()
        
        # Activity is indicated by active_window changing or input_activity being non-zero
        input_data = snapshot.get("input_activity", {})
        keys_pressed = input_data.get("keys_pressed", 0)
        mouse_moves = input_data.get("mouse_moves", 0)
        
        # We also consider having an active window as activity, but only if they are actually interacting.
        # Let's rely on input_activity for a clearer signal.
        if keys_pressed > 0 or mouse_moves > 0:
            return True
            
        return False
        
    async def loop(self):
        while self._is_running:
            if not await self._has_briefed_today():
                if self._is_user_active():
                    logger.info("First activity of the day detected. Triggering briefing.")
                    await self._mark_briefed_today()
                    
                    # Trigger briefing
                    from app.api.voice import _trigger_briefing
                    asyncio.create_task(_trigger_briefing())
            
            await asyncio.sleep(self.check_interval_seconds)
            
    def start(self):
        if self._is_running:
            return
        self._is_running = True
        self._task = asyncio.create_task(self.loop())
        
    def stop(self):
        self._is_running = False
        if self._task and not self._task.done():
            self._task.cancel()

global_briefing_scheduler = BriefingScheduler()
