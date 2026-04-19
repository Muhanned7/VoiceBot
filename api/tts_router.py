from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from core.models import synthesizer
from core.tts.synthesizer import Synthesizer
from utils.config_loader import load_settings
from utils.logger import get_logger

logger = get_logger(__name__)
cfg = load_settings()

router = APIRouter()
'''
synthesizer = Synthesizer(
    language=cfg.tts.language,
    slow=cfg.tts.slow
)
'''

class TextInput(BaseModel):
    text: str

@router.post("/synthesize")
def synthesize_speech(payload: TextInput):
    logger.info(f"TTS request: '{payload.text[:50]}'")

    try:
        audio_bytes = synthesizer.synthesize(payload.text)
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg"
        )
    except ValueError as e:
        logger.warning(f"Empty text: {str(e)}")
        return JSONResponse(status_code=400, content={"error": str(e)})

    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "TTS synthesis failed."})
