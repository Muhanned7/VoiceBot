from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from core.models import generator
from core.response.generator import ResponseGenerator
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()
#generator = ResponseGenerator()

class IntentInput(BaseModel):
    intent: str

@router.post("/generate")
def generate_response(payload: IntentInput):
    logger.info(f"Generating response for intent: '{payload.intent}'")
    try:
        response_text = generator.generate(payload.intent)
        return {
            "intent": payload.intent,
            "response": response_text
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Something went wrong."})
    
