import asyncio
import logging
from typing import Optional
from app.core.conversation import global_conversation_buffer
from app.core.db import SessionLocal
from app.models import Conversation
import datetime

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds
        self._timeout_task: Optional[asyncio.Task] = None
        self._is_active = False
        self.active_conversation_id: Optional[int] = None

    async def ping(self):
        """
        Called when user activity is detected (wake word, speech).
        Resets the timeout.
        """
        if not self._is_active:
            logger.info("New conversation session started.")
            self._is_active = True
            
            # Create a new conversation record in DB
            async with SessionLocal() as db:
                new_conv = Conversation()
                db.add(new_conv)
                await db.commit()
                await db.refresh(new_conv)
                self.active_conversation_id = new_conv.id
            
        # Cancel existing timeout task
        if self._timeout_task and not self._timeout_task.done():
            self._timeout_task.cancel()
            
        # Create a new timeout task
        loop = asyncio.get_running_loop()
        self._timeout_task = loop.create_task(self._wait_for_timeout())

    async def _wait_for_timeout(self):
        try:
            await asyncio.sleep(self.timeout_seconds)
            await self.end_session()
        except asyncio.CancelledError:
            pass # Pinged again, timeout reset

    async def end_session(self):
        if self._is_active:
            logger.info("Conversation session timed out. Clearing context.")
            self._is_active = False
            
            if self.active_conversation_id:
                async with SessionLocal() as db:
                    conv = await db.get(Conversation, self.active_conversation_id)
                    if conv:
                        conv.ended_at = datetime.datetime.now(datetime.timezone.utc)
                        await db.commit()
                        
            self.active_conversation_id = None
            global_conversation_buffer.clear()

global_session_manager = SessionManager()
