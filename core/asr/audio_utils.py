import wave
from io import BytesIO
from utils.exceptions import UnsupportedAudioFormat, AudioTooShort

SUPPORTED_FORMATS = ["wav"]
MIN_DURATION_SECONDS = 1.0

def validate_audio(file_bytes: bytes, filename: str) -> None:
    extension = filename.split(".")[-1].lower()
    if extension not in SUPPORTED_FORMATS:
        raise UnsupportedAudioFormat(
            f"Unsupported format: {extension}. Only WAV is supported right now."
        )
     
def get_audio_duration(file_bytes: bytes) -> float:
    with wave.open(BytesIO(file_bytes)) as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = frames / rate
        return duration

def prepare_audio(file_bytes: bytes, filename: str) -> BytesIO:
    validate_audio(file_bytes, filename)

    duration = get_audio_duration(file_bytes)
    if duration < MIN_DURATION_SECONDS:
        raise ValueError(f"Audio too short: {duration:.2f}s. Minimum is {MIN_DURATION_SECONDS}s.")
    
    return BytesIO(file_bytes)