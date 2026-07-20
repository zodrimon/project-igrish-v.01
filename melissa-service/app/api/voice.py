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
    
    llm_provider = get_llm_provider()
    messages = build_prompt(text)
    
    llm_response_chunks = []
    async for chunk in llm_provider.generate(messages, stream=False):
        llm_response_chunks.append(chunk)
        
    llm_text = "".join(llm_response_chunks)
    logger.info(f"LLM Response: '{llm_text}'")
        
    audio_bytes = await tts_adapter.synthesize(llm_text)
    logger.info(f"Synthesized audio: {len(audio_bytes)} bytes")
    
    return Response(content=audio_bytes, media_type="audio/wav")
