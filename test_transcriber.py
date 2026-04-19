from core.asr.audio_utils import prepare_audio
from core.asr.transcriber import Transcriber

# Step 1 — load and prepare the audio
with open("test_wav.wav", "rb") as f:
    audio_bytes = f.read()

audio = prepare_audio(audio_bytes, "test_wav.wav")

# Step 2 — load the model
transcriber = Transcriber(model_name="base", device="cpu")
transcriber.load()

# Step 3 — transcribe
result = transcriber.transcribe(audio)
print(f"Text     : {result['text']}")
print(f"Language : {result['language']}")