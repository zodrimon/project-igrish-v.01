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
        
    from app.core.llm_registry import get_llm_provider
    from app.core.prompt_builder import build_prompt
    from app.core.conversation import global_conversation_buffer
    from app.core.streaming import chunk_sentences
    from app.core.session import global_session_manager
    from app.memory.store_semantic import global_semantic_store
    from app.core.db import SessionLocal
    from app.models import Turn
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
    
    # Query semantic memory for relevant context
    def _query_semantic():
        return global_semantic_store.query_memory(text, n_results=3)
    relevant_memories = await asyncio.to_thread(_query_semantic)
    
    messages = build_prompt(text, conversation_history=history, relevant_memories=relevant_memories)
    
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
