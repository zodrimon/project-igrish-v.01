from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api import voice

import sys
import os
import traceback
from logging.handlers import RotatingFileHandler

# Set up logs directory
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "melissa.log")

# Configure root logger to output to both console and rotating file
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)

# Rotating file handler (10MB max, keep 5 backups)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5)
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception
import asyncio
from contextlib import asynccontextmanager
from app.adapters.sensors.wake_word import WakeWordSensor
from app.api.voice import wake_word_event_queue
from app.core.context_snapshot import global_context_snapshot
from app.adapters.sensors.active_window import ActiveWindowSensor
from app.adapters.sensors.process_list import ProcessListSensor
from app.adapters.sensors.clipboard import ClipboardSensor
from app.adapters.sensors.input_activity import InputActivitySensor
from app.adapters.sensors.system_state import SystemStateSensor

def on_wake_detected():
    # Push to queue (needs to be thread-safe since WakeWordSensor runs in a thread)
    loop = asyncio.get_running_loop()
    loop.call_soon_threadsafe(wake_word_event_queue.put_nowait, "WAKE_WORD_DETECTED")

wake_sensor = WakeWordSensor(on_wake=on_wake_detected)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize snapshot
    global_context_snapshot.register_sensor(ActiveWindowSensor())
    global_context_snapshot.register_sensor(ProcessListSensor())
    global_context_snapshot.register_sensor(ClipboardSensor())
    global_context_snapshot.register_sensor(InputActivitySensor())
    global_context_snapshot.register_sensor(SystemStateSensor())
    global_context_snapshot.start(interval_seconds=2.0)
    
    from app.core.scheduler import global_briefing_scheduler
    from app.core.plugin_loader import global_plugin_registry
    
    global_plugin_registry.load_plugins()
    global_briefing_scheduler.start()
    wake_sensor.start()
    yield
    wake_sensor.stop()
    global_briefing_scheduler.stop()
    global_context_snapshot.stop()

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
from app.api import settings
app.include_router(settings.router)


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
