import logging
from fastapi import APIRouter, UploadFile, File

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/voice", tags=["Voice"])

@router.post("/stream")
async def stream_audio(audio: UploadFile = File(...)):
    """
    Debug endpoint to receive captured audio from the shell.
    """
    content = await audio.read()
    logger.info(f"Received audio chunk of size {len(content)} bytes. Filename: {audio.filename}")
    return {"status": "ok", "bytes_received": len(content)}
