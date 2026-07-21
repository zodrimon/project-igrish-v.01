from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from app.core.db import SessionLocal
from app.models import Preference
from sqlalchemy import select, update

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])

class SettingsUpdate(BaseModel):
    settings: Dict[str, str]

@router.get("")
async def get_settings():
    async with SessionLocal() as db:
        result = await db.execute(select(Preference))
        prefs = result.scalars().all()
        return {p.key: p.value for p in prefs}

@router.post("")
async def update_settings(update_data: SettingsUpdate):
    async with SessionLocal() as db:
        for key, value in update_data.settings.items():
            result = await db.execute(select(Preference).where(Preference.key == key))
            existing = result.scalar_one_or_none()
            if existing:
                existing.value = value
            else:
                db.add(Preference(key=key, value=value))
        await db.commit()
    return {"status": "success"}
