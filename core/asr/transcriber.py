import whisper
import os
import tempfile
from io import BytesIO
from utils.logger import get_logger
from utils.config_loader import load_settings
cfg = load_settings()

logger = get_logger(__name__)


class Transcriber:
    def __init__(self, model_name: str = "base", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.model = None
    
    def load(self) -> None:
        logger.info(f"Loading Whisper model: {self.model_name}")
        self.model = whisper.load_model(self.model_name, device=self.device,download_root=cfg.cache.whisper)
        logger.info("Whisper model loaded successfully")

    def transcribe(self, audio: BytesIO) -> dict:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        logger.info("Starting transcription")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio.read())
            tmp_path = tmp.name
            logger.info(f"Temp file created at: {tmp_path}")
        
        try:
            logger.info(f"Passing to Whisper: {tmp_path}")
            result = self.model.transcribe(tmp_path)
        finally:
            os.remove(tmp_path)
        
        #audio.seek(0)
        #result = self.model.transcribe(audio.name if hasattr(audio, 'name') else audio)

        text = result["text"].strip()
        language = result.get("language", "en")

        logger.info("Transcription complete: '{text[:50]}...'")
        
        return {
            "text": text,
            "language": language
        } 
        