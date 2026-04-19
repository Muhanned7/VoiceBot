import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import requests

SERVER_URL = "http://127.0.0.1:8000"
TEST_WAV = "test_wav.wav"
RUNS = 3

print("\n--- Latency Evaluation ---\n")

latencies = []

for i in range(RUNS):
    with open(TEST_WAV, "rb") as f:
        start = time.time()
        response = requests.post(
            f"{SERVER_URL}/voicebot",
            files={"file": ("test_wav.wav", f, "audio/wav")}
        )

        end = time.time()

    latency = round(end - start, 3)
    latencies.append(latency)
    status = "ok" if response.status_code == 200 else "failed"
    print(f"Run {i + 1}: {latency}s — {status}")

avg = round(sum(latencies) / len(latencies), 3)
minimum = round(min(latencies), 3)
maximum = round(max(latencies), 3)

print(f"\nAverage : {avg}s")
print(f"Min     : {minimum}s")
print(f"Max     : {maximum}s")

if avg < 5.0:
    print(f"\nPassed — average latency {avg}s is under the 5s target")
else:
    print(f"\nFailed — average latency {avg}s exceeds the 5s target")