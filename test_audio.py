from core.asr.audio_utils import prepare_audio


try:
    prepare_audio(b"fake data", "document.pdf")
except ValueError as e:
    print(f"Test 1 passed: {e}")


with open("file_example_WAV_1MG.wav", "rb") as f:
    audio_bytes = f.read()
result = prepare_audio(audio_bytes, "file_example_WAV_1MG.wav")
print(f"test 2 passed: got BytesIO object: {type(result)}")