import logging
from fastapi import APIRouter, UploadFile, File, Response
from app.adapters.stt.whisper import WhisperSTTAdapter
from app.adapters.tts.piper import PiperTTSAdapter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/voice", tags=["Voice"])

logger.info("Loading STT and TTS models...")
stt_adapter = WhisperSTTAdapter()
tts_adapter = PiperTTSAdapter()
logger.info("Models loaded.")

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
        
    audio_bytes = await tts_adapter.synthesize(text)
    logger.info(f"Synthesized audio: {len(audio_bytes)} bytes")
    
    return Response(content=audio_bytes, media_type="audio/wav")
