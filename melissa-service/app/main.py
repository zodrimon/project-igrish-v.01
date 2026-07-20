from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api import voice

logging.basicConfig(level=logging.INFO)

import asyncio
from contextlib import asynccontextmanager
from app.adapters.sensors.wake_word import WakeWordSensor
from app.api.voice import wake_word_event_queue

def on_wake_detected():
    # Push to queue (needs to be thread-safe since WakeWordSensor runs in a thread)
    loop = asyncio.get_running_loop()
    loop.call_soon_threadsafe(wake_word_event_queue.put_nowait, "WAKE_WORD_DETECTED")

wake_sensor = WakeWordSensor(on_wake=on_wake_detected)

@asynccontextmanager
async def lifespan(app: FastAPI):
    wake_sensor.start()
    yield
    wake_sensor.stop()

app = FastAPI(title="Melissa Service", version="0.1.0", lifespan=lifespan)

app.state.wake_sensor = wake_sensor

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

from app.core.db import SessionLocal
from app.models import Base
from sqlalchemy import text
from app.memory.store_semantic import global_semantic_store

@app.delete("/api/memory")
async def purge_memory():
    # Clear semantic memory
    global_semantic_store.clear()
    
    # Clear SQL memory (truncate all tables except alembic_version)
    async with SessionLocal() as db:
        for table in reversed(Base.metadata.sorted_tables):
            await db.execute(text(f"DELETE FROM {table.name}"))
        await db.commit()
        
    return {"status": "success", "message": "Memory purged"}
