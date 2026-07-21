from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.core.db import SessionLocal
from app.models import NudgeLog

class NudgeLogManager:
    @staticmethod
    async def log_nudge(nudge_type: str, content: str, cooldown_minutes: int = 30):
        """Logs a nudge and sets a cooldown for that nudge type."""
        async with SessionLocal() as session:
            cooldown_until = datetime.now(timezone.utc) + timedelta(minutes=cooldown_minutes)
            
            log_entry = NudgeLog(
                nudge_type=nudge_type,
                content=content,
                cooldown_until=cooldown_until
            )
            session.add(log_entry)
            await session.commit()
            
    @staticmethod
    async def is_on_cooldown(nudge_type: str) -> bool:
        """Returns True if the given nudge type is currently on cooldown."""
        async with SessionLocal() as session:
            now = datetime.now(timezone.utc)
            # Find the most recent nudge of this type
            result = await session.execute(
                select(NudgeLog)
                .where(NudgeLog.nudge_type == nudge_type)
                .order_by(NudgeLog.created_at.desc())
                .limit(1)
            )
            latest_nudge = result.scalar_one_or_none()
            
            if not latest_nudge or not latest_nudge.cooldown_until:
                return False
                
            # If cooldown_until is naive, make it aware (SQLite sometimes drops tz)
            cooldown = latest_nudge.cooldown_until
            if cooldown.tzinfo is None:
                cooldown = cooldown.replace(tzinfo=timezone.utc)
                
            return cooldown > now
