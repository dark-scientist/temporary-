# Dotryder Voice RAG API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
4. [API Endpoints](#api-endpoints)
5. [How API Calls Work](#how-api-calls-work)
6. [Frontend Integration](#frontend-integration)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Dotryder Voice RAG API is a FastAPI-based backend that powers a fully offline voice-enabled Retrieval-Augmented Generation (RAG) system. It combines:

- **Speech-to-Text (STT)**: faster-whisper for audio transcription
- **Embeddings**: BAAI/bge-small-en-v1.5 for document vectorization
- **Vector Database**: FAISS for semantic search
- **Large Language Model (LLM)**: Ollama (llama3.2:3b, qwen2.5:7b, deepseek-r1:7b)
- **Text-to-Speech (TTS)**: Piper for audio generation

All components run locally without internet dependency after initial setup.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                          │
│                   (localhost:5173)                           │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│                   (localhost:8000)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /chat      → Text-based RAG query                   │   │
│  │  /voice     → Voice input → RAG → Voice output       │   │
│  │  /tts       → Text → Audio conversion                │   │
│  │  /upload    → PDF upload & index rebuild             │   │
│  │  /health    → System status check                    │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼             ▼
   ┌────────┐  ┌─────────┐  ┌──────────┐
   │  STT   │  │   RAG   │  │   TTS    │
   │Whisper │  │  FAISS  │  │  Piper   │
   └────────┘  └─────────┘  └──────────┘
                     │
                     ▼
              ┌────────────┐
              │   Ollama   │
              │    LLM     │
              └────────────┘
```

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama installed and running
- Virtual environment at `~/projects/venv/`

### Step 1: Install Ollama Model
```bash
# Pull the default model
ollama pull llama3.2:3b

# Start Ollama server (keep running in separate terminal)
ollama serve
```

### Step 2: Activate Virtual Environment
```bash
source ~/projects/venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
cd version_2
pip install -r requirements.txt
```

### Step 4: Build FAISS Index
```bash
# Place your PDF documents in data/documents/
# Then build the index
python3 build_index.py
```

### Step 5: Start Backend Server
```bash
# Make sure Ollama is running first!
python3 api.py
```

Backend will start at: `http://localhost:8000`
API docs available at: `http://localhost:8000/docs`

### Step 6: Start Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend will start at: `http://localhost:5173`

---

## API Endpoints

### 1. GET `/health`
**Purpose**: Check if backend and RAG system are ready

**Request**: None

**Response**:
```json
{
  "status": "ok",
  "model": "llama3.2:3b",
  "index_loaded": true
}
```

**Called By**: Frontend on mount to verify backend connectivity

---

### 2. POST `/chat`
**Purpose**: Text-based RAG query

**Request Body**:
```json
{
  "message": "What is stoicism?"
}
```

**Response**:
```json
{
  "response": "Stoicism is an ancient Greek philosophy...",
  "sources_used": 3,
  "time_taken": 2.45
}
```

**How It Works**:
1. Receives user text query
2. Retrieves relevant document chunks from FAISS (top 3 by default)
3. Constructs prompt with context
4. Sends to Ollama LLM
5. Returns generated response

**Called By**: `ChatAssistant.jsx` → `handleSendMessage()`

**Code Location**:
```javascript
// frontend/src/components/ChatAssistant.jsx
const response = await fetch(`${API_BASE_URL}/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: userMessage })
})
```

---

### 3. POST `/voice`
**Purpose**: Voice-based RAG query (full pipeline)

**Request**: 
- `multipart/form-data`
- Field: `audio_file` (audio/webm file)

**Response**:
- Audio file (audio/wav)
- Headers:
  - `X-Transcribed-Text`: Original user speech transcription
  - `X-Response-Text`: LLM response text

**How It Works**:
1. Receives audio file from frontend
2. Transcribes audio using faster-whisper (STT)
3. Retrieves relevant context from FAISS
4. Generates response using Ollama LLM
5. Converts response to speech using Piper (TTS)
6. Returns audio file with metadata headers

**Called By**: `ChatAssistant.jsx` → `sendVoiceMessage()`

**Code Location**:
```javascript
// frontend/src/components/ChatAssistant.jsx
const formData = new FormData()
formData.append('audio_file', audioBlob, 'recording.webm')

const response = await fetch(`${API_BASE_URL}/voice`, {
  method: 'POST',
  body: formData
})

// Extract transcription from header
const transcribedText = response.headers.get('X-Transcribed-Text')
```

---

### 4. POST `/tts`
**Purpose**: Convert text to speech (standalone TTS)

**Request Body**:
```json
{
  "text": "Hello, this is a test."
}
```

**Response**:
- Audio file (audio/wav)

**How It Works**:
1. Receives text string
2. Generates audio using Piper TTS
3. Returns WAV audio file

**Called By**: Not currently used in frontend (available for future features)

---

### 5. POST `/upload-documents`
**Purpose**: Upload new PDFs and rebuild index

**Request**:
- `multipart/form-data`
- Field: `files` (array of PDF files)

**Response**:
```json
{
  "status": "success",
  "files_uploaded": 2,
  "chunks_created": 450,
  "filenames": ["doc1.pdf", "doc2.pdf"]
}
```

**How It Works**:
1. Deletes ALL existing documents in `data/documents/`
2. Deletes existing FAISS index in `database/vector_store/`
3. Saves uploaded files to `data/documents/`
4. Rebuilds FAISS index from scratch
5. Returns statistics

**Called By**: Backend only (removed from frontend UI per mentor feedback)

**Note**: This endpoint is available via Swagger UI at `/docs` for testing

---

### 6. POST `/process-pdf-directory`
**Purpose**: Rebuild index from existing documents

**Request Body**:
```json
{
  "directory_path": "./data/documents",
  "rebuild_index": true
}
```

**Response**:
```json
{
  "status": "success",
  "directory": "./data/documents",
  "chunks_created": 992
}
```

**How It Works**:
1. Scans specified directory for PDFs
2. If `rebuild_index: true`, deletes old index
3. Rebuilds FAISS index from all PDFs
4. Returns chunk count

**Called By**: Backend only (removed from frontend UI)

---

## How API Calls Work

### Text Chat Flow

```
User types message in ChatAssistant
         ↓
handleSendMessage() triggered
         ↓
POST /chat with { message: "..." }
         ↓
Backend: api.py → chat() function
         ↓
RAG system retrieves context from FAISS
         ↓
LLM generates response using context
         ↓
Response sent back to frontend
         ↓
Message displayed in chat bubble
```

### Voice Chat Flow

```
User clicks mic button
         ↓
Browser MediaRecorder starts
         ↓
Audio recorded (auto-stops after 3s silence or 10s max)
         ↓
sendVoiceMessage() triggered
         ↓
POST /voice with audio blob
         ↓
Backend: api.py → voice() function
         ↓
STT transcribes audio → text
         ↓
RAG retrieves context from FAISS
         ↓
LLM generates response text
         ↓
TTS converts response → audio
         ↓
Audio + headers sent back
         ↓
Frontend plays audio & displays transcription
```

---

## Frontend Integration

### API Base URL Configuration

```javascript
// frontend/src/components/ChatAssistant.jsx
const API_BASE_URL = 'http://localhost:8000'
```

### CORS Configuration

Backend allows all origins for development:

```python
# api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Transcribed-Text", "X-Response-Text"],
)
```

### Error Handling

All API calls include try-catch blocks:

```javascript
try {
  const response = await fetch(`${API_BASE_URL}/chat`, {...})
  if (!response.ok) throw new Error('Failed to get response')
  const data = await response.json()
  // Handle success
} catch (error) {
  console.error('Chat error:', error)
  addMessage('Sorry, something went wrong.', 'bot')
}
```

---

## Configuration

### Model Selection

Edit `src/config.py`:

```python
# Change this line to switch models
OLLAMA_MODEL = "llama3.2:3b"  # Options: llama3.2:3b, qwen2.5:7b, deepseek-r1:7b
```

### RAG Parameters

Edit `src/config.py`:

```python
CHUNK_SIZE = 500        # Characters per chunk
CHUNK_OVERLAP = 50      # Overlap between chunks
TOP_K = 3               # Number of chunks to retrieve
```

### Audio Settings

Edit `src/config.py`:

```python
SAMPLE_RATE = 16000           # Audio sample rate
SILENCE_THRESHOLD = 0.02      # Silence detection threshold
SILENCE_DURATION = 1.5        # Seconds of silence before stopping
```

---

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
source ~/projects/venv/bin/activate
pip install fastapi uvicorn python-multipart
```

---

### "RAG system not initialized"

**Error**: 503 error on `/chat` or `/voice`

**Solution**: Build the FAISS index first
```bash
python3 build_index.py
```

---

### Ollama connection failed

**Error**: `Connection refused` when calling LLM

**Solution**: Start Ollama server
```bash
ollama serve
```

---

### Voice recording not working

**Issue**: Microphone permission denied

**Solution**: 
1. Check browser permissions
2. Use HTTPS or localhost (required for MediaRecorder API)
3. Verify microphone is not used by another app

---

### CORS errors in browser

**Issue**: `Access-Control-Allow-Origin` error

**Solution**: Verify backend CORS middleware is configured (already set in `api.py`)

---

## File Structure

```
version_2/
├── api.py                    # FastAPI backend (main entry point)
├── build_index.py            # Script to build FAISS index
├── requirements.txt          # Python dependencies
├── src/
│   ├── config.py            # Configuration settings
│   ├── rag.py               # RAG system (FAISS + embeddings)
│   ├── llm.py               # Ollama LLM interface
│   ├── stt.py               # Speech-to-text (Whisper)
│   ├── tts.py               # Text-to-speech (Piper)
│   └── logger.py            # Logging utilities
├── data/
│   └── documents/           # PDF documents (user uploads here)
├── database/
│   └── vector_store/        # FAISS index files
├── model/
│   └── models/              # Embedding model files
├── piper/                   # Piper TTS binaries and voice models
└── frontend/
    ├── src/
    │   ├── components/
    │   │   └── ChatAssistant.jsx  # Main chat component
    │   └── App.jsx
    └── package.json
```

---

## API Testing with Swagger

Access interactive API documentation at:
```
http://localhost:8000/docs
```

This provides:
- Interactive endpoint testing
- Request/response schemas
- Example payloads
- Direct API calls from browser

---

## Performance Notes

- **Text chat**: ~2-3 seconds per query
- **Voice chat**: ~5-7 seconds (includes STT + RAG + LLM + TTS)
- **Index building**: ~1-2 seconds per PDF page
- **Model loading**: ~5-10 seconds on first request (cached afterward)

---

## Security Considerations

**Current Setup**: Development mode only
- CORS allows all origins
- No authentication
- No rate limiting

**For Production**:
1. Restrict CORS to specific domains
2. Add API key authentication
3. Implement rate limiting
4. Use HTTPS
5. Validate file uploads (size, type)
6. Sanitize user inputs

---

## Support

For issues or questions:
1. Check `/health` endpoint first
2. Review backend logs in terminal
3. Check browser console for frontend errors
4. Verify Ollama is running: `ollama list`
5. Ensure FAISS index exists: `ls database/vector_store/`

---

**Last Updated**: March 2026  
**Version**: 2.0  
**Maintainer**: Dotryder Team
