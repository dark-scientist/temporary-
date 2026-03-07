# Dotryder — Voice RAG Pipeline

Fully offline voice-based RAG assistant. Speak your question, get a spoken answer from your documents.

## Tech Stack
- STT: faster-whisper (Whisper small, CPU)
- Embeddings: nomic-embed-text via Ollama
- Vector DB: FAISS
- LLM: gemma:2b (fast) / gemma3:4b (quality) via Ollama
- TTS: espeak-ng
- API: FastAPI
- Frontend: React + Vite

## Quick Start
See `setup.md` for full setup instructions.

## Usage
```bash
# Terminal 1
ollama serve

# Terminal 2
python api.py

# Terminal 3
cd frontend && npm run dev

# Open browser
http://localhost:5173
```

## API Endpoints
- GET  `/health`
- POST `/chat`
- POST `/voice`
- POST `/tts`
- POST `/upload-documents`
- POST `/process-pdf-directory`

## Model Selection
Edit `src/config.py` — set `USE_QUALITY_MODEL = True` for gemma3:4b

## Benchmark Models
```bash
python util/compare_models.py
```
