from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from core.models import classifier
from core.intent.classifier import IntentClassifier
from utils.exceptions import ModelNotLoaded, LowConfidenceIntent
from utils.config_loader import load_settings
from utils.logger import get_logger

logger = get_logger(__name__)
cfg = load_settings()

router = APIRouter()
#classifier = IntentClassifier(model_path=cfg.intent.model_path)

class TextInput(BaseModel):
    text: str

@router.post("/predict")
def predict_intent(payload: TextInput):
    logger.info(f"Received text: '{payload.text}'")

    try:
        result = classifier.predict(payload.text)
        return {
            "text": payload.text,
            "intent": result["intent"],
            "confidence": result["confidence"]
        }

    except LowConfidenceIntent as e:
        logger.warning(f"Low confidence: {e.message}")
        return JSONResponse(status_code=200, content={
            "text": payload.text,
            "intent": "general_inquiry",
            "confidence": e.confidence,
            "warning": "Low confidence — defaulting to general_inquiry"
        })

    except ModelNotLoaded as e:
        logger.error(f"Model not loaded: {e.message}")
        return JSONResponse(status_code=503, content={"error": e.message})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Something went wrong."})