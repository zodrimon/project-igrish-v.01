from typing import Dict, Any, Optional
import asyncio
import time
from sqlalchemy import select
from app.core.db import SessionLocal
from app.models import Goal
from app.core.context_snapshot import global_context_snapshot
from app.core.classification import AppClassifier
from app.memory.nudge_log import NudgeLogManager

class DecisionLoop:
    def __init__(self, snapshot_provider=None, check_interval_seconds: float = 10.0, distraction_threshold_seconds: float = 300.0):
        self.snapshot_provider = snapshot_provider or global_context_snapshot
        self.check_interval_seconds = check_interval_seconds
        self.distraction_threshold_seconds = distraction_threshold_seconds
        self._is_running = False
        self._task = None
        self._classifier = AppClassifier()
        
        # State tracking
        self._distraction_start_time: Optional[float] = None
        
    async def evaluate_heuristics(self) -> Optional[Dict[str, Any]]:
        """
        Evaluates current state and returns a nudge trigger dictionary if a nudge should happen.
        """
        snapshot = self.snapshot_provider.get_state()
        
        active_window_data = snapshot.get("active_window", {})
        if not active_window_data or not active_window_data.get("app_name"):
            self._distraction_start_time = None
            return None
            
        category = self._classifier.classify(
            active_window_data.get("app_name", ""),
            active_window_data.get("window_title", "")
        )
        
        if category == "distraction":
            if self._distraction_start_time is None:
                self._distraction_start_time = time.time()
                
            elapsed = time.time() - self._distraction_start_time
            if elapsed >= self.distraction_threshold_seconds:
                # Check if we have an active goal
                async with SessionLocal() as session:
                    result = await session.execute(select(Goal).where(Goal.status == "active").limit(1))
                    active_goal = result.scalar_one_or_none()
                    
                if active_goal:
                    # Check cooldown
                    if not await NudgeLogManager.is_on_cooldown("distraction"):
                        # We would trigger here.
                        # Reset tracking so we don't immediately trigger again if cooldown logic is bypassed or short
                        self._distraction_start_time = None
                        
                        return {
                            "nudge_type": "distraction",
                            "goal_description": active_goal.description,
                            "app_name": active_window_data.get("app_name")
                        }
        else:
            # Not in distraction, reset timer
            self._distraction_start_time = None
            
        return None
        
    async def loop(self):
        while self._is_running:
            nudge_trigger = await self.evaluate_heuristics()
            if nudge_trigger:
                # In T7.3 we will use the LLM to phrase this and TTS to speak it.
                # For now, just log it to the DB so the cooldown applies.
                await NudgeLogManager.log_nudge(
                    nudge_type=nudge_trigger["nudge_type"],
                    content=f"Nudge for {nudge_trigger['goal_description']} while using {nudge_trigger['app_name']}",
                    cooldown_minutes=30
                )
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
