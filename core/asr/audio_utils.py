import wave
import subprocess
import os
import uuid
from io import BytesIO
from utils.exceptions import UnsupportedAudioFormat, AudioTooShort
from utils.logger import get_logger

SUPPORTED_FORMATS = ["wav", "webm", "ogg", "mp3", "m4a"]
MIN_DURATION_SECONDS = 1.0

logger = get_logger(__name__)

def detect_format(file_bytes: bytes) -> str:
    # check actual file signature, not filename
    if file_bytes[:4] == b"RIFF":
        return "wav"
    if file_bytes[:4] == b"\x1aE\xdf\xa3":
        return "webm"
    if file_bytes[:4] == b"OggS":
        return "ogg"
    if file_bytes[:3] == b"ID3" or file_bytes[:2] == b"\xff\xfb":
        return "mp3"
    # default to webm for browser recordings
    return "webm"
PROJECT_ROOT = os.path.dirname(  # voicebot/
    os.path.dirname(              # core/
        os.path.dirname(          # asr/
            os.path.abspath(__file__)  # audio_utils.py
        )
    )
)
PROCESSED_DIR = os.path.normpath(os.path.join(PROJECT_ROOT, "data", "processed"))
PROCESSED_DIR = os.path.normpath(PROCESSED_DIR)
def convert_to_wav(input_bytes: bytes, input_format: str) -> bytes:
    input_path = os.path.join(PROCESSED_DIR, f"tmp_in_{uuid.uuid4().hex}.{input_format}")
    output_path = os.path.join(PROCESSED_DIR, f"tmp_out_{uuid.uuid4().hex}.wav")


    with open(input_path, "wb") as f:
        f.write(input_bytes)

    try:
        result = subprocess.run([
            "ffmpeg", "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            output_path
        ], text=True, capture_output=True)
        # Log EVERYTHING
        logger.error(f"ffmpeg returncode: {result.returncode}")
        logger.error(f"ffmpeg stderr: {result.stderr}")
        logger.error(f"ffmpeg stdout: {result.stdout}")
        logger.error(f"input file exists: {os.path.exists(input_path)}")
        logger.error(f"input file size: {os.path.getsize(input_path)}")
        with open(output_path, "rb") as f:
            wav_bytes = f.read()

        return wav_bytes

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)


def validate_audio(file_bytes: bytes, filename: str) -> None:
    extension = filename.split(".")[-1].lower()
    if extension not in SUPPORTED_FORMATS:
        raise UnsupportedAudioFormat(
            f"Unsupported format: {extension}. Supported: {SUPPORTED_FORMATS}"
        )


def get_audio_duration(file_bytes: bytes) -> float:
    with wave.open(BytesIO(file_bytes)) as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        return frames / rate


def prepare_audio(file_bytes: bytes, filename: str) -> BytesIO:
    # detect actual format from file content, not filename
    actual_format = detect_format(file_bytes)

    if actual_format != "wav":
        file_bytes = convert_to_wav(file_bytes, actual_format)

    duration = get_audio_duration(file_bytes)
    if duration < MIN_DURATION_SECONDS:
        raise AudioTooShort(
            f"Audio too short: {duration:.2f}s. Minimum is {MIN_DURATION_SECONDS}s."
        )

    return BytesIO(file_bytes)