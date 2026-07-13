from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response
from core.asr.audio_utils import prepare_audio
from core.asr.transcriber import Transcriber
from core.tts.synthesizer import Synthesizer
import base64
from core.models import transcriber, synthesizer
from core.agent.agent import build_agent, run_turn
from core.agent.database import init_db
from utils.exceptions import (
    UnsupportedAudioFormat,
    AudioTooShort,
    TranscriptionEmpty,
    ModelNotLoaded
)
from utils.config_loader import load_settings
from utils.logger import get_logger


logger = get_logger(__name__)
cfg = load_settings()

router = APIRouter()

# Built once at import time, reused across requests. MemorySaver keeps each
# session's conversation history in-process, keyed by session_id.
init_db()
voice_agent = build_agent()


def load_all():
    transcriber.load()


@router.post("/voicebot")
async def voicebot(file: UploadFile = File(...), session_id: str = Form(...)):
    """
    session_id: stable ID for the current conversation, generated once by
    the frontend when a call/chat session starts and re-sent on every turn
    of that same session. This is what gives the agent multi-turn memory —
    without it (or if it changes every request) the agent has no memory of
    earlier turns.
    """
    logger.info(f"Voicebot request received: {file.filename} (session={session_id})")

    try:
        # Step 1 — ASR
        audio_bytes = await file.read()
        audio = prepare_audio(audio_bytes, file.filename)
        transcript = transcriber.transcribe(audio)
        text = transcript["text"]
        logger.info(f"Transcript: '{text}'")

        # Step 2 — Agent (replaces intent classification + fixed response
        # generation). The agent decides on its own whether to just reply,
        # or call check_order_status / check_account / process_refund.
        response_text = run_turn(voice_agent, text, thread_id=session_id)
        logger.info(f"Agent response: '{response_text[:50]}'")

        # Step 3 — TTS
        audio_out = synthesizer.synthesize(response_text)
        audio_b64 = base64.b64encode(audio_out).decode("utf-8")
        logger.info("Voicebot pipeline complete")

        return JSONResponse(content={
            "transcript": text,
            "response": response_text,
            "audio": audio_b64
        })

    except UnsupportedAudioFormat as e:
        logger.warning(f"Bad format: {e.message}")
        return JSONResponse(status_code=400, content={"error": e.message})

    except AudioTooShort as e:
        logger.warning(f"Audio too short: {e.message}")
        return JSONResponse(status_code=400, content={"error": e.message})

    except TranscriptionEmpty as e:
        logger.warning(f"Empty transcript: {e.message}")
        return JSONResponse(status_code=422, content={"error": e.message})

    except ModelNotLoaded as e:
        logger.error(f"Model not loaded: {e.message}")
        return JSONResponse(status_code=503, content={"error": e.message})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Something went wrong."})