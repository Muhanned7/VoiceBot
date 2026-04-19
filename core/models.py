from core.asr.transcriber import Transcriber
from core.intent.classifier import IntentClassifier
from core.response.generator import ResponseGenerator
from core.tts.synthesizer import Synthesizer
from utils.config_loader import load_settings
from utils.logger import get_logger

logger = get_logger(__name__)
cfg = load_settings()

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


def load_all_models() -> None:
    logger.info("Loading all models")
    transcriber.load()
    classifier.load()
    generator.load()
    logger.info("All models loaded")