from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse, Response
from core.asr.audio_utils import prepare_audio
from core.asr.transcriber import Transcriber
from core.intent.classifier import IntentClassifier
from core.response.generator import ResponseGenerator
from core.tts.synthesizer import Synthesizer
import base64
from core.models import transcriber, classifier, generator, synthesizer
from utils.exceptions import (
    UnsupportedAudioFormat,
    AudioTooShort,
    TranscriptionEmpty,
    LowConfidenceIntent,
    ModelNotLoaded
)
from utils.config_loader import load_settings
from utils.logger import get_logger



logger = get_logger(__name__)
cfg = load_settings()

router = APIRouter()
'''
transcriber = Transcriber(
    model_name=cfg.asr.model_name,
    device=cfg.asr.device
)

classifier = IntentClassifier(
    model_path=cfg.intent.model_path
)

generator = ResponseGenerator()
synthesizer = Synthesizer(
    language=cfg.tts.language,
    slow=cfg.tts.slow
)
'''

def load_all():
    transcriber.load()
    classifier.load()
    generator.load()
    
@router.post("/voicebot")
async def voicebot(file: UploadFile = File(...)):
    logger.info(f"Voicebot request received: {file.filename}")

    try:
        # Step 1 — ASR
        audio_bytes = await file.read()
        audio = prepare_audio(audio_bytes, file.filename)
        transcript = transcriber.transcribe(audio)
        text = transcript["text"]
        logger.info(f"Transcript: '{text}'")

        # Step 2 — Intent
        intent_result = classifier.predict(text)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        logger.info(f"Intent: {intent} ({confidence})")

        # Step 3 — Response
        response_text = generator.generate(intent)
        logger.info(f"Response: '{response_text[:50]}'")

        # Step 4 — TTS
        audio_out = synthesizer.synthesize(response_text)
        print(type(audio_out))  # Add this temporarily
        print(len(audio_out))
        logger.info("Voicebot pipeline complete")

        return JSONResponse(content={
        "transcript": text,
        "intent": intent,
        "confidence": confidence,
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

    except LowConfidenceIntent as e:
        logger.warning(f"Low confidence, using fallback response")
        response_text = generator.generate("general_inquiry")
        audio_out = synthesizer.synthesize(response_text)
        print(type(audio_out))  # Add this temporarily
        print(len(audio_out))
        audio_b64 = base64.b64encode(audio_out).decode("utf-8")
        return JSONResponse(content={
            "transcript": "",
            "intent": "general_inquiry",
            "confidence": 0.0,
            "response": response_text,
            "audio": audio_b64
        })

    except ModelNotLoaded as e:
        logger.error(f"Model not loaded: {e.message}")
        return JSONResponse(status_code=503, content={"error": e.message})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Something went wrong."})



