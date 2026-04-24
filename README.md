# VoiceBot — AI-Powered Voice Bot for Customer Support

A production-ready voice bot system that handles customer support queries through
speech interaction. The system accepts voice input, converts speech to text,
classifies user intent, generates a contextual response, and returns synthesized
speech output — all accessible through a React web interface.

---

## System Architecture
Audio Input (WAV / WebM / OGG)
↓
Format Detection        ← detects actual format from file bytes, not filename
↓
ffmpeg conversion       ← converts any format to WAV 16kHz mono
↓
ASR — Whisper           → transcript text
↓
Intent — BERT           → intent label + confidence score
↓
Response — Templates    → response text
↓
TTS — gTTS              → audio output (MP3 base64 encoded)
↓
JSON Response           → transcript + intent + confidence + response + audio
↓
React Frontend          → displays results, plays audio

---

## Project Structure

Updated README.md
Open README.md and replace everything with this:
markdown# VoiceBot — AI-Powered Voice Bot for Customer Support

A production-ready voice bot system that handles customer support queries through
speech interaction. The system accepts voice input, converts speech to text,
classifies user intent, generates a contextual response, and returns synthesized
speech output — all accessible through a React web interface.

---

## System Architecture
Audio Input (WAV / WebM / OGG)
↓
Format Detection        ← detects actual format from file bytes, not filename
↓
ffmpeg conversion       ← converts any format to WAV 16kHz mono
↓
ASR — Whisper           → transcript text
↓
Intent — BERT           → intent label + confidence score
↓
Response — Templates    → response text
↓
TTS — gTTS              → audio output (MP3 base64 encoded)
↓
JSON Response           → transcript + intent + confidence + response + audio
↓
React Frontend          → displays results, plays audio

---

## Project Structure
voicebot/
api/
asr_router.py            POST /asr/transcribe
intent_router.py         POST /intent/predict
response_router.py       POST /response/generate
tts_router.py            POST /tts/synthesize
voicebot_router.py       POST /voicebot  (unified endpoint)
core/
asr/
audio_utils.py         validates, detects format, converts to WAV
transcriber.py         loads Whisper, runs transcription
intent/
dataset.py             tokenizes CSV, splits train/eval
trainer.py             fine-tunes BERT on intents dataset
classifier.py          loads saved model, runs inference
response/
generator.py           maps intent to response template
tts/
synthesizer.py         converts text to speech via gTTS
models.py                single shared model instances
frontend/
src/
App.jsx                root component, state management, API calls
components/
Recorder.jsx         microphone recording via MediaRecorder API
Uploader.jsx         WAV file upload via file picker
ResultCard.jsx       displays transcript, intent, confidence, response
AudioPlayer.jsx      plays MP3 audio response with progress bar
index.css              global styles
vite.config.js           dev server + API proxy config
config/
config.yaml              all configuration values
config.example.yaml      template for new developers
response_templates.yaml  intent to response mapping
data/
raw/
intents.csv            labeled training dataset (12 intents)
scripts/
eval_asr.py              measures Word Error Rate
eval_intent.py           measures F1, plots confusion matrix
eval_latency.py          measures end-to-end response time
utils/
config_loader.py         typed Pydantic config wrapper
logger.py                structured loguru logger
exceptions.py            typed exception hierarchy
main.py                    FastAPI application entry point
requirements.txt           all dependencies

---

## Frontend

A React web interface built with Vite. No curl commands needed.

### Features

- Record voice directly from the browser microphone
- Upload a WAV file from your machine
- Automatic format detection and conversion (WAV, WebM, OGG)
- Spinner while the pipeline processes
- Result card showing transcript, intent, confidence score with color coding
- Audio player with play/pause and progress bar
- Reset button to ask another question
- Error screen with retry option

### How it works

User records or uploads audio
↓
React sends one POST /voicebot request
↓
Backend returns JSON with:

transcript  (what Whisper heard)
intent      (what BERT classified)
confidence  (how sure the model is)
response    (the customer support reply)
audio       (MP3 encoded as base64)
↓
React decodes base64 audio → creates blob URL → AudioPlayer plays it
ResultCard displays all text data

### Running the frontend

```cmd
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

---

## API Endpoints

| Method | Endpoint | Input | Output |
|--------|----------|-------|--------|
| GET | /health | — | server status |
| POST | /asr/transcribe | WAV file | transcript text |
| POST | /intent/predict | JSON text | intent + confidence |
| POST | /response/generate | JSON intent | response text |
| POST | /tts/synthesize | JSON text | MP3 audio |
| POST | /voicebot | audio file | JSON with transcript, intent, confidence, response, audio |

### /voicebot response format

```json
{
  "transcript": "where is my order",
  "intent": "order_status",
  "confidence": 0.4567,
  "response": "Your order is currently being processed and will ship within 2 business days.",
  "audio": "//NExAA..."
}
```

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
- Node.js 18+
- ffmpeg installed and on PATH
- Git

### Install ffmpeg on Windows

```cmd
winget install ffmpeg
```

Close and reopen your terminal after installing so PATH updates.

### Clone and setup backend

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

### Run the backend

```cmd
python main.py
```

### Setup and run the frontend

```cmd
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Audio Format Support

The system detects the actual audio format from file bytes — not the filename extension. This means browser-recorded audio (WebM/OGG) works even when labelled as WAV.

| Format | Source | Supported |
|--------|--------|-----------|
| WAV | file upload | ✓ |
| WebM | browser recording (Chrome) | ✓ |
| OGG | browser recording (Firefox) | ✓ |
| MP3 | file upload | ✓ |
| M4A | file upload | ✓ |

ffmpeg handles all format conversion before Whisper processes the audio.

---

## Testing

### Full pipeline via browser

1. Run backend: `python main.py`
2. Run frontend: `cd frontend && npm run dev`
3. Open `http://localhost:5173`
4. Record or upload audio
5. See transcript, intent, response and hear the audio reply

### Full pipeline via curl

```cmd
curl -X POST http://127.0.0.1:8000/voicebot -F "file=@test.wav"
```

### Individual endpoint tests

```cmd
curl -X POST http://127.0.0.1:8000/asr/transcribe -F "file=@test.wav"

curl -X POST http://127.0.0.1:8000/intent/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"where is my order\"}"

curl -X POST http://127.0.0.1:8000/response/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"intent\": \"order_status\"}"
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
| End-to-end Latency | ~3-5s on CPU | < 5s |

---

## Known Limitations and Planned Improvements

### Intent classifier accuracy — in progress

Current accuracy is 0.64. Root cause is insufficient training data.
Planned fix — expand dataset using Bitext customer support dataset
and retrain with distilbert-base-uncased.

### Confidence scores are low

The model predicts correct intents but with low confidence scores
(0.15-0.45). This triggers the low confidence fallback more often
than ideal. Improves with more training data.

### TTS engine

Currently using gTTS which requires internet. Planned addition of
Coqui TTS as an offline alternative with configurable voice and speed.

### GPU support

Config has device: "cpu". Switch to device: "cuda" if a GPU is
available. Not tested on GPU yet.

---

## Architecture Decisions

### Single /voicebot endpoint returns everything

The frontend makes one request and receives transcript, intent,
confidence, response text and audio all in one JSON response.
Audio is base64 encoded so it can travel inside JSON without
a separate binary endpoint.

### Format detection from file bytes not filename

Browser MediaRecorder records WebM but labels it as WAV.
Trusting the filename caused RIFF header errors. Reading
the first few bytes of the file identifies the true format
regardless of what the filename says.

### Shared model instances via core/models.py

A single file owns all model instances. Every router imports
from it. This prevents loading Whisper and BERT multiple times
into memory.

### Template responses over generative

Template responses are fast, predictable, and cannot hallucinate.
For customer support where accuracy matters more than creativity
this is the right default. A generative layer can be added later.

### Individual routers alongside the unified endpoint

The unified /voicebot endpoint handles production use.
Individual routers exist for testing each module in isolation
without running the full pipeline.

---

## Dependencies

### Backend

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

### Frontend

| Library | Purpose |
|---------|---------|
| React | UI framework |
| Vite | dev server and bundler |
| MediaRecorder API | browser microphone recording |
| Web Audio API | audio playback |



