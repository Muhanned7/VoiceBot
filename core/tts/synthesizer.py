import io
from gtts import gTTS
from utils.logger import get_logger

logger = get_logger(__name__)

class Synthesizer:
    def __init__(self, language: str = "en", slow: bool = False):
        self.language = language
        self.slow = slow

    def synthesize(self, text: str) -> bytes:
        if not text or not text.strip():
            raise ValueError("Cannot synthesize empty text.")
        
        logger.info(f"Synthesizing: '{text[:50]}'")

        tts = gTTS(text=text, lang=self.language, slow=self.slow)

        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        logger.info("Synthesis complete")
        return audio_buffer.read()