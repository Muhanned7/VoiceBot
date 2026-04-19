from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from core.asr.transcriber import Transcriber
from core.asr.audio_utils import prepare_audio
from utils.exceptions import UnsupportedAudioFormat, AudioTooShort, TranscriptionEmpty
from utils.config_loader import load_settings
from utils.logger import get_logger
from core.models import transcriber

logger = get_logger(__name__)
cfg = load_settings()

router = APIRouter()
#transcriber = Transcriber(model_name="base", device="cpu")

@router.on_event("startup")
async def load_model():
    transcriber.load()

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}")

    try:
        audio_bytes = await file.read()
        audio = prepare_audio(audio_bytes, file.filename)
        result = transcriber.transcribe(audio)
        return {
            "filename": file.filename,
            "text": result["text"],
            "language": result["language"]
        }
    except UnsupportedAudioFormat as e:
        logger.warning(f"Bad format: {e.message}")
        return JSONResponse(status_code=400, content={"error": e.message})
    
    except AudioTooShort as e:
        logger.warning(f"Audio too short: {e.message}")
        return JSONResponse(status_code=400, content={"error": e.message})
    
    except TranscriptionEmpty as e:
        logger.warning(f"Empty transcript: {e.message}")
        return JSONResponse(status_code=422, content={"error": e.message})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Something went wrong."})