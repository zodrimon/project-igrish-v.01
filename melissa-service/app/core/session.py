import asyncio
import logging
from typing import Optional
from app.core.conversation import global_conversation_buffer

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds
        self._timeout_task: Optional[asyncio.Task] = None
        self._is_active = False

    def ping(self):
        """
        Called when user activity is detected (wake word, speech).
        Resets the timeout.
        """
        if not self._is_active:
            logger.info("New conversation session started.")
            self._is_active = True
            
        # Cancel existing timeout task
        if self._timeout_task and not self._timeout_task.done():
            self._timeout_task.cancel()
            
        # Create a new timeout task
        loop = asyncio.get_running_loop()
        self._timeout_task = loop.create_task(self._wait_for_timeout())

    async def _wait_for_timeout(self):
        try:
            await asyncio.sleep(self.timeout_seconds)
            self.end_session()
        except asyncio.CancelledError:
            pass # Pinged again, timeout reset

    def end_session(self):
        if self._is_active:
            logger.info("Conversation session timed out. Clearing context.")
            self._is_active = False
            global_conversation_buffer.clear()

global_session_manager = SessionManager()
