import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jiwer import wer
from core.asr.transcriber import Transcriber
from core.asr.audio_utils import prepare_audio

transcriber = Transcriber(model_name="base", device="cpu")
transcriber.load()

# small eval set — reference is what was actually said
# add more entries as you record more WAV files
eval_set = [
    {"file": "test_wav.wav", "reference": "where is my order"},
]

total_wer = 0

print("\n--- ASR Evaluation ---\n")

for item in eval_set:
    with open(item["file"], "rb") as f:
        audio_bytes = f.read()

    audio = prepare_audio(audio_bytes, item["file"])
    result = transcriber.transcribe(audio)
    hypothesis = result["text"].lower().strip()
    reference = item["reference"].lower().strip()

    score = wer(reference, hypothesis)
    total_wer += score

    print(f"File      : {item['file']}")
    print(f"Reference : {reference}")
    print(f"Hypothesis: {hypothesis}")
    print(f"WER       : {score:.4f}")
    print()

avg_wer = total_wer / len(eval_set)
print(f"Average WER: {avg_wer:.4f}")
print(f"Average Accuracy: {(1 - avg_wer) * 100:.1f}%")