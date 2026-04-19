from pydantic import BaseModel
import yaml

class AppConfig(BaseModel):
    name: str = "VoiceBot"
    version: str = "0.1.0"
    debug: bool = False


class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True

class IntentConfig(BaseModel):
    model_path: str = "models/intent_classifier"
    confidence_threshold: float = 0.3

class ASRConfig(BaseModel):
    model_name: str = "base"
    device: str = "cpu"
    language: str = "en"

class TTSConfig(BaseModel):
    language: str = "en"
    slow: bool = False

class CacheConfig(BaseModel):
    huggingface: str = "D:/AI_Caches/huggingface"
    whisper: str = "D:/AI_Caches/whisper"
    torch: str = "D:/AI_Caches/torch"


class Settings(BaseModel):
    app: AppConfig = AppConfig()
    server: ServerConfig = ServerConfig()
    asr: ASRConfig = ASRConfig()
    intent: IntentConfig = IntentConfig()
    tts: TTSConfig = TTSConfig()
    cache: CacheConfig = CacheConfig()

def load_settings(path: str = "config/config.yaml") -> Settings:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    return Settings(**raw)