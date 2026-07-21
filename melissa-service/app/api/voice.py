import logging
from fastapi import APIRouter, UploadFile, File, Response, Request
from pydantic import BaseModel
from app.adapters.stt.whisper import WhisperSTTAdapter
from app.adapters.tts.piper import PiperTTSAdapter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/voice", tags=["Voice"])

class ToggleRequest(BaseModel):
    enabled: bool

@router.post("/wake-word/toggle")
async def toggle_wake_word(req: ToggleRequest, request: Request):
    sensor = request.app.state.wake_sensor
    if req.enabled:
        sensor.start()
        return {"status": "started"}
    else:
        sensor.stop()
        return {"status": "stopped"}

import asyncio
from fastapi.responses import StreamingResponse

logger.info("Loading STT and TTS models...")
stt_adapter = WhisperSTTAdapter()
tts_adapter = PiperTTSAdapter()
logger.info("Models loaded.")

wake_word_event_queue = asyncio.Queue()

@router.get("/events")
async def voice_events():
    async def event_generator():
        while True:
            msg = await wake_word_event_queue.get()
            yield f"data: {msg}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/tts")
async def synthesize_text(text: str):
    """
    Synthesize provided text to audio and return the stream.
    Used for ad-hoc nudges.
    """
    # PiperTTSAdapter.synthesize_stream takes an async generator of text chunks.
    # We can create a simple generator that yields the entire text.
    async def single_sentence_generator():
        yield text
        
    audio_stream = tts_adapter.synthesize_stream(single_sentence_generator())
    return StreamingResponse(audio_stream, media_type="audio/wav")

@router.post("/stream")
async def stream_audio(audio: UploadFile = File(...)):
    """
    Loopback endpoint: Audio -> STT -> TTS -> Audio
    """
    content = await audio.read()
    logger.info(f"Received audio chunk: {len(content)} bytes. Filename: {audio.filename}")
    
    text = await stt_adapter.transcribe(content)
    logger.info(f"Transcribed text: '{text}'")
    
    if not text or text.strip().lower() in ("", "[silence]", "[blank audio]"):
        return Response(status_code=204)
        
    # Intercept "brief me"
    if "brief me" in text.lower():
        # Trigger briefing manually
        asyncio.create_task(_trigger_briefing())
        return Response(status_code=204)
        
    # Intercept "explain this error" or "explain this file"
    low_text = text.lower()
    if "explain this error" in low_text or "explain this file" in low_text:
        from app.core.context_snapshot import global_context_snapshot
        snapshot = global_context_snapshot.get_state()
        clipboard = snapshot.get("clipboard", {}).get("content", "")
        window_title = snapshot.get("active_window", {}).get("title", "")
        
        project_context = ""
        from app.core.plugin_loader import global_plugin_registry
        for p in global_plugin_registry.get_all_plugins():
            if p.name == "CodingCompanion":
                # get_context_facts is async
                facts = await p.get_context_facts()
                if "active_project" in facts:
                    project_context = f"Project: {facts['active_project']}"
                    
        intent = "error" if "explain this error" in low_text else "file"
        text = (
            f"Please explain this {intent}. "
            f"Here is my clipboard content: '{clipboard}'. "
            f"My active window title is: '{window_title}'. "
            f"{project_context}"
        )
        
    from app.core.llm_registry import get_llm_provider
    from app.core.prompt_builder import build_prompt
    from app.core.conversation import global_conversation_buffer
    from app.core.session import global_session_manager
    from app.memory.store_semantic import global_semantic_store
    from app.core.db import SessionLocal
    from app.models import Turn
    from app.core.fact_extractor import extract_facts
    from app.memory.context_aggregator import build_augmented_prompt
    from app.core.streaming import chunk_sentences
    from fastapi.responses import StreamingResponse
    import uuid
    
    await global_session_manager.ping()
    
    llm_provider = get_llm_provider()
    history = global_conversation_buffer.get_history()
    
    # Store the user's turn in SQL asynchronously
    async def _store_user_turn_sql():
        conv_id = global_session_manager.active_conversation_id
        if conv_id:
            async with SessionLocal() as db:
                turn = Turn(conversation_id=conv_id, role="user", content=text)
                db.add(turn)
                await db.commit()
    asyncio.create_task(_store_user_turn_sql())
    
    # Extract structured facts asynchronously
    asyncio.create_task(extract_facts(text))
    
    messages = await build_augmented_prompt(text)
    
    # Store the user's turn in semantic memory asynchronously
    user_turn_id = str(uuid.uuid4())
    asyncio.create_task(asyncio.to_thread(
        global_semantic_store.store_turn, user_turn_id, text, {"role": "user"}
    ))
    
    llm_stream = llm_provider.generate(messages, stream=True)
    sentence_stream = chunk_sentences(llm_stream)
    
    # We must also capture the full LLM response to add to history.
    # To do this cleanly while streaming, we can wrap the generator.
    async def wrapped_sentence_stream():
        full_text = []
        async for sentence in sentence_stream:
            full_text.append(sentence)
            yield sentence
        
        joined_text = " ".join(full_text)
        global_conversation_buffer.add_turn(text, joined_text)
        
        melissa_turn_id = str(uuid.uuid4())
        asyncio.create_task(asyncio.to_thread(
            global_semantic_store.store_turn, melissa_turn_id, joined_text, {"role": "melissa"}
        ))
        
        # Store Melissa's turn in SQL asynchronously
        async def _store_melissa_turn_sql():
            conv_id = global_session_manager.active_conversation_id
            if conv_id:
                async with SessionLocal() as db:
                    turn = Turn(conversation_id=conv_id, role="melissa", content=joined_text)
                    db.add(turn)
                    await db.commit()
        asyncio.create_task(_store_melissa_turn_sql())
        
    audio_stream = tts_adapter.synthesize_stream(wrapped_sentence_stream())
    
    return StreamingResponse(audio_stream, media_type="audio/wav")

async def _trigger_briefing():
    from app.core.briefing import pull_briefing_data
    from app.core.prompt_builder import build_briefing_prompt
    from app.core.llm_registry import get_llm_provider
    
    try:
        data = await pull_briefing_data()
        messages = build_briefing_prompt(data)
        
        llm = get_llm_provider()
        llm_stream = llm.generate(messages, stream=False)
        
        briefing_text = ""
        async for chunk in llm_stream:
            briefing_text += chunk
            
        briefing_text = briefing_text.strip()
        if briefing_text:
            logger.info(f"Generated briefing: {briefing_text}")
            wake_word_event_queue.put_nowait(f"NUDGE_AUDIO:{briefing_text}")
    except Exception as e:
        logger.error(f"Failed to generate briefing: {e}")

@router.post("/briefing")
async def trigger_briefing():
    """Manually trigger the daily briefing."""
    asyncio.create_task(_trigger_briefing())
    return {"status": "briefing started"}
