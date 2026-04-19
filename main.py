from fastapi import FastAPI
import uvicorn
import yaml
from utils.config_loader import load_settings
from utils.logger import setup_logger, get_logger
from core.asr.transcriber import Transcriber
from api.asr_router import router as asr_router
from api.intent_router import router as intent_router
from api.response_router import router as response_router
from api.tts_router import router as tts_router
from api.voicebot_router import router as voicebot_router
from core.models import load_all_models
import os

cfg = load_settings()
# set cache dirs before any model is imported
os.environ["HF_HOME"] = cfg.cache.huggingface
os.environ["TRANSFORMERS_CACHE"] = cfg.cache.huggingface
os.environ["TORCH_HOME"] = cfg.cache.torch
setup_logger()
logger = get_logger(__name__)


app = FastAPI(
    title=cfg.app.name,
    version=cfg.app.version,
    description="AI-powered voice bot for customer support"
)

app.include_router(asr_router, prefix="/asr", tags=["ASR"])
app.include_router(intent_router, prefix="/intent", tags=["Intent"])
app.include_router(response_router, prefix="/response", tags=["Response"])
app.include_router(tts_router, prefix="/tts", tags=["TTS"])
app.include_router(voicebot_router, tags=["VoiceBot"])

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {cfg.app.name} v{cfg.app.version}")
    load_all_models()
    logger.info(f"Server running on {cfg.server.host}: {cfg.server.port}")

@app.get("/health")
def health_check():
    logger.info("Health check called")
    return {
        "status": "ok",
        "app": cfg.app.name,
        "version": cfg.app.version
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=cfg.server.host,
        port=cfg.server.port,
        reload=cfg.server.reload
    )