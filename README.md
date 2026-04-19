# VoiceBot — AI-Powered Voice Bot for Customer Support

A production-ready voice bot system that handles customer support queries through
speech interaction. The system accepts voice input, converts speech to text,
classifies user intent, generates a contextual response, and returns synthesized
speech output.

---

## System Architecture

Audio Input (WAV)
↓
ASR — Whisper        → transcript text
↓
Intent — BERT        → intent label + confidence score
↓
Response — Templates → response text
↓
TTS — gTTS           → audio output (MP3)

---

## Project Structure
voicebot/
api/
asr_router.py          POST /asr/transcribe
intent_router.py       POST /intent/predict
response_router.py     POST /response/generate
tts_router.py          POST /tts/synthesize
voicebot_router.py     POST /voicebot  (unified endpoint)
core/
asr/
audio_utils.py       validates and prepares audio input
transcriber.py       loads Whisper, runs transcription
intent/
dataset.py           tokenizes CSV, splits train/eval
trainer.py           fine-tunes BERT on intents dataset
classifier.py        loads saved model, runs inference
response/
generator.py         maps intent to response template
tts/
synthesizer.py       converts text to speech via gTTS
models.py              single shared model instances
config/
config.yaml            all configuration values
config.example.yaml    template for new developers
response_templates.yaml intent to response mapping
data/
raw/
intents.csv          labeled training dataset (12 intents)
scripts/
eval_asr.py            measures Word Error Rate
eval_intent.py         measures F1, plots confusion matrix
eval_latency.py        measures end-to-end response time
utils/
config_loader.py       typed Pydantic config wrapper
logger.py              structured loguru logger
exceptions.py          typed exception hierarchy
main.py                  FastAPI application entry point
requirements.txt         all dependencies

---

## API Endpoints

| Method | Endpoint | Input | Output |
|--------|----------|-------|--------|
| GET | /health | — | server status |
| POST | /asr/transcribe | WAV file | transcript text |
| POST | /intent/predict | JSON text | intent + confidence |
| POST | /response/generate | JSON intent | response text |
| POST | /tts/synthesize | JSON text | MP3 audio |
| POST | /voicebot | WAV file | MP3 audio |

---

## Supported Intents

| Intent | Example phrase |
|--------|---------------|
| order_status | "where is my order" |
| order_cancellation | "I want to cancel my order" |
| refund_request | "I want a refund" |
| subscription_issue | "my subscription is not working" |
| password_reset | "I forgot my password" |
| shipping_query | "how long does shipping take" |
| product_inquiry | "tell me about this product" |
| account_issue | "I cannot log into my account" |
| payment_issue | "my payment failed" |
| return_request | "I want to return a product" |
| complaint | "I am very unhappy with your service" |
| general_inquiry | "can you help me" |

---

## Setup

### Prerequisites

- Python 3.10+
- ffmpeg installed and on PATH
- Git

### Install ffmpeg

```cmd
winget install ffmpeg
```

### Clone and setup

```cmd
git clone https://github.com/Muhanned7/VoiceBot.git
cd VoiceBot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Configure

```cmd
copy config\config.example.yaml config\config.yaml
```

Open `config\config.yaml` and set your cache paths:

```yaml
cache:
  huggingface: "D:/AI_Cache/huggingface"
  whisper: "D:/AI_Cache/whisper"
  torch: "D:/AI_Cache/torch"
```

### Train the intent classifier

```cmd
python -m core.intent.trainer
```

### Run the server

```cmd
python main.py
```

Visit `http://127.0.0.1:8000/docs` for the interactive API explorer.

---

## Testing

### Full pipeline test

```cmd
curl -X POST http://127.0.0.1:8000/voicebot -F "file=@test.wav" --output response.mp3
```

### Individual endpoint tests

```cmd
curl -X POST http://127.0.0.1:8000/asr/transcribe -F "file=@test.wav"

curl -X POST http://127.0.0.1:8000/intent/predict \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"where is my order\"}"

curl -X POST http://127.0.0.1:8000/response/generate \
  -H "Content-Type: application/json" \
  -d "{\"intent\": \"order_status\"}"

curl -X POST http://127.0.0.1:8000/tts/synthesize \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Your order is on its way\"}" \
  --output reply.mp3
```

---

## Evaluation

```cmd
python scripts\eval_asr.py       # Word Error Rate
python scripts\eval_intent.py    # F1 score + confusion matrix
python scripts\eval_latency.py   # end-to-end latency
```

### Current evaluation results

| Metric | Value | Target |
|--------|-------|--------|
| ASR Word Error Rate | ~0.00 on clean audio | < 0.10 |
| Intent Accuracy | 0.64 | 0.85+ |
| Intent F1 Score | 0.61 | 0.85+ |
| End-to-end Latency | ~3s | < 5s |

---

## Known Limitations and Planned Improvements

### Intent classifier accuracy — in progress

Current accuracy is 0.64. The root cause is insufficient training data — approximately
25 examples per intent. Target is 40-60 examples per intent.

Planned fix:
- Expand `data/raw/intents.csv` using the Bitext customer support dataset
- Retrain with `distilbert-base-uncased` for better small-dataset performance
- Add weighted loss for class imbalance

### Audio format support — planned

Currently only WAV is supported. Planned additions:
- MP3 support via pydub conversion
- M4A support for mobile recordings
- Noise reduction preprocessing

### TTS engine — planned

Currently using gTTS which requires internet. Planned:
- Add Coqui TTS as offline alternative
- Configurable speaking rate
- Voice selection

### Frontend UI — not started

A web interface for testing the voicebot without curl commands.
Planned stack: React + Web Audio API.

### GPU support — configured, not tested

`config.yaml` has `device: "cpu"`. Switch to `device: "cuda"` if a GPU
is available. Not tested on GPU yet.

---

## Dependencies

| Library | Purpose |
|---------|---------|
| fastapi | REST API framework |
| uvicorn | ASGI server |
| openai-whisper | speech to text |
| transformers | BERT intent classifier |
| torch | model inference |
| gTTS | text to speech |
| loguru | structured logging |
| pydantic | config validation |
| jiwer | WER evaluation |
| scikit-learn | F1 and confusion matrix |

---

## Architecture Decisions

### Why config.yaml over environment variables

All configuration lives in one file. Changing the Whisper model size,
confidence threshold, or server port is a one line edit with no code changes.

### Why shared model instances

A single `core/models.py` owns all model instances. Every router imports
from it. This prevents loading Whisper and BERT multiple times into memory.

### Why template mapping over generative responses

Template responses are fast, predictable, and cannot hallucinate. For customer
support where accuracy matters more than creativity, mapping is the right choice.
A generative layer can be added on top later.

### Why individual routers alongside the unified endpoint

The unified `/voicebot` endpoint handles production use. Individual routers
exist for testing and debugging each module in isolation without running
the full pipeline.