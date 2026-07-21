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
        
        # Focus mode gating for heuristics
        if snapshot.get("focus_mode", {}).get("is_active", False):
            self._distraction_start_time = None
            return None
            
        
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
                
            # Read preferences
            async with SessionLocal() as session:
                from app.models import Preference
                prefs_result = await session.execute(select(Preference).where(Preference.key.like("nudge.%")))
                prefs = {p.key: p.value for p in prefs_result.scalars()}
                
                sensitivity = prefs.get("nudge.sensitivity", "normal")
                mute_categories = prefs.get("nudge.mute_categories", "").split(",")
                
                if sensitivity == "off" or category in [c.strip() for c in mute_categories if c.strip()]:
                    self._distraction_start_time = None
                    return None
                    
                # Adjust threshold based on sensitivity
                adjusted_threshold = self.distraction_threshold_seconds
                if sensitivity == "gentle":
                    adjusted_threshold *= 2.0  # Wait twice as long
                    
                elapsed = time.time() - self._distraction_start_time
                if elapsed >= adjusted_threshold:
                    # Check if we have an active goal
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
            # Global focus mode gate
            snapshot = self.snapshot_provider.get_state()
            if snapshot.get("focus_mode", {}).get("is_active", False):
                await asyncio.sleep(self.check_interval_seconds)
                continue
                
            nudge_trigger = await self.evaluate_heuristics()
            
            # Evaluate plugins if no heuristic nudge
            if not nudge_trigger:
                from app.core.plugin_loader import global_plugin_registry
                for p in global_plugin_registry.get_all_plugins():
                    try:
                        trigger = await p.evaluate_proactive_triggers()
                        if trigger:
                            nudge_trigger = trigger
                            break
                    except Exception as e:
                        import logging
                        logging.getLogger(__name__).error(f"Plugin {p.name} proactive error: {e}")
            
            if nudge_trigger:
                from app.core.llm_registry import get_llm_provider
                from app.core.prompt_builder import get_system_prompt
                from app.api.voice import wake_word_event_queue
                import logging
                
                logger = logging.getLogger(__name__)
                llm = get_llm_provider()
                
                # Construct the prompt for the nudge
                nudge_type = nudge_trigger.get("nudge_type", "unknown")
                if nudge_type == "distraction":
                    prompt = (
                        f"{get_system_prompt()}\n\n"
                        f"The user is currently distracted by using {nudge_trigger.get('app_name', 'an app')}. "
                        f"However, they have an active goal: '{nudge_trigger.get('goal_description', 'unknown')}'. "
                        f"Please provide a single, brief, friendly sentence to nudge them back on track. "
                        f"Do not be overly critical. Keep it conversational and spoken-style."
                    )
                elif nudge_trigger.get("content"):
                    prompt = f"{get_system_prompt()}\n\n{nudge_trigger['content']}"
                else:
                    logger.warning(f"Unknown nudge trigger format: {nudge_trigger}")
                    await asyncio.sleep(self.check_interval_seconds)
                    continue
                
                messages = [{"role": "system", "content": prompt}]
                
                try:
                    # Generate the text
                    # The generate method is an async generator for streaming
                    llm_stream = llm.generate(messages, stream=False)
                    # wait, some adapters yield strings even if stream=False.
                    # let's collect the full response.
                    nudge_text = ""
                    async for chunk in llm_stream:
                        nudge_text += chunk
                        
                    nudge_text = nudge_text.strip()
                    logger.info(f"Generated nudge: {nudge_text}")
                    
                    if nudge_text:
                        # Log it
                        await NudgeLogManager.log_nudge(
                            nudge_type=nudge_trigger["nudge_type"],
                            content=nudge_text,
                            cooldown_minutes=30
                        )
                        
                        # Trigger audio on frontend
                        wake_word_event_queue.put_nowait(f"NUDGE_AUDIO:{nudge_text}")
                except Exception as e:
                    logger.error(f"Failed to generate or send nudge: {e}")
                    
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
