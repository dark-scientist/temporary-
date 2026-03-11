"""
Dotryder Voice RAG API - FastAPI Backend

How to run:
# Terminal 1: Start Ollama
# ollama serve
#
# Terminal 2: Start FastAPI backend
# source venv/bin/activate
# pip install fastapi uvicorn python-multipart
# python api.py
#
# Terminal 3: Start React frontend
# cd frontend
# npm install
# npm run dev
#
# Open browser: http://localhost:5173
"""

import sys
import os
import time
import tempfile
import asyncio
import shutil
import logging
import base64
import sqlite3
import re
from typing import Optional
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Add src to path
sys.path.insert(0, './src')

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Import existing modules
from rag import RAGSystem
from llm import OllamaLLM
from stt import SpeechToText
from tts import TextToSpeech
from config import ACTIVE_MODEL

# Global instances
rag_system = None
stt = None
tts = None
llm_client = None
index_loaded = False
executor = ThreadPoolExecutor(max_workers=4)
logger = logging.getLogger("dotryder.api")
DB_PATH = "./logs/users.db"


def _is_greeting_message(message: str) -> bool:
    """Return True for short greeting-only messages."""
    normalized = re.sub(r"[^a-z\s]", " ", (message or "").lower()).strip()
    if not normalized:
        return False
    greeting_phrases = {
        "hi", "hello", "hey", "hii", "heyy",
        "good morning", "good afternoon", "good evening"
    }
    return normalized in greeting_phrases


def _warm_up_llm():
    """Warm the model once at startup to avoid first-request cold latency."""
    if llm_client is None:
        return
    try:
        start = time.time()
        llm_client.generate(
            "Warm up model.",
            "Service startup warmup context."
        )
        print(f"✓ LLM warm-up completed in {time.time() - start:.2f}s\n")
    except Exception as e:
        print(f"⚠️  LLM warm-up skipped: {e}\n")


def _ensure_chat_history_table():
    """Create the chat history table if it does not exist."""
    os.makedirs("./logs", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            question TEXT NOT NULL,
            response TEXT NOT NULL,
            model_used TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            time_taken REAL
        )
        """
    )
    conn.commit()
    conn.close()


def _log_chat_history(username: str, question: str, response: str, time_taken: float):
    """Persist a chat interaction for stats/history endpoints."""
    _ensure_chat_history_table()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO chat_history (username, question, response, model_used, time_taken)
        VALUES (?, ?, ?, ?, ?)
        """,
        (username, question, response, ACTIVE_MODEL, round(time_taken, 2)),
    )
    conn.commit()
    conn.close()


# Request/Response models
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    sources_used: int
    time_taken: float


class TTSRequest(BaseModel):
    text: str


class HealthResponse(BaseModel):
    status: str
    model: str
    index_loaded: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize RAG system and other components on startup."""
    global rag_system, stt, tts, llm_client, index_loaded
    
    print("\n" + "="*60)
    print("  Dotryder Voice RAG API")
    print("  Docs: http://localhost:8000/docs")
    print(f"  Model: {ACTIVE_MODEL}")
    print("="*60 + "\n")
    
    # Check if vector store exists
    vector_store_path = "./database/vector_store"
    if not os.path.exists(vector_store_path) or not os.listdir(vector_store_path):
        print("⚠️  Warning: FAISS index not found!")
        print(f"Please run: python build_index.py")
        print("API will start but /chat and /voice endpoints will fail.\n")
        index_loaded = False
    else:
        try:
            print("[INIT] Loading RAG system...")
            rag_system = RAGSystem()
            index_loaded = True
            print("✓ RAG system loaded\n")
        except Exception as e:
            print(f"❌ Error loading RAG system: {e}\n")
            index_loaded = False
    
    # Initialize STT
    try:
        if shutil.which("ffmpeg") is None:
            print("⚠️  ffmpeg not found in PATH. /voice transcription will not work.")
        print("[INIT] Loading Speech-to-Text...")
        stt = SpeechToText()
        print("✓ STT initialized\n")
    except Exception as e:
        print(f"❌ Error loading STT: {e}\n")
    
    # Initialize TTS
    try:
        print("[INIT] Loading Text-to-Speech...")
        tts = TextToSpeech()
        print("✓ TTS initialized\n")
    except Exception as e:
        print(f"❌ Error loading TTS: {e}\n")

    # Initialize LLM client once to avoid per-request setup cost.
    try:
        print("[INIT] Loading LLM client...")
        llm_client = OllamaLLM()
        _warm_up_llm()
        print("✓ LLM client initialized\n")
    except Exception as e:
        print(f"❌ Error loading LLM client: {e}\n")
        llm_client = None

    # Ensure SQLite schema exists for stats/history endpoints.
    try:
        _ensure_chat_history_table()
    except Exception as e:
        print(f"⚠️  Could not initialize chat history database: {e}\n")
    
    print("="*60)
    print("API Ready! Listening on http://0.0.0.0:8000")
    print("="*60 + "\n")

    yield


# Initialize FastAPI app
app = FastAPI(
    title="Dotryder Voice RAG API",
    description="RAG-powered conversational assistant with voice support",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Transcribed-Text",
        "X-Response-Text",
        "X-Transcribed-Text-B64",
        "X-Response-Text-B64",
    ],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Dotryder Voice RAG API",
        "docs": "/docs",
        "health": "/health",
        "models": "/models"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        model=ACTIVE_MODEL,
        index_loaded=index_loaded
    )


def _generate_response(message: str):
    """Synchronous function to generate response."""
    if llm_client is None:
        raise RuntimeError("LLM client not initialized")

    if _is_greeting_message(message):
        return "Hello, I'm your AI assistant. How may I assist you today?", 0

    start_time = time.time()
    # Retrieve context from RAG
    context = rag_system.retrieve(message)
    retrieval_ms = (time.time() - start_time) * 1000
    
    # Count retrieved chunks, excluding sentinel no-document message.
    if context.strip() == "No documents available in the knowledge base.":
        sources_used = 0
    else:
        sources_used = len([c for c in context.split('\n\n') if c.strip()])
    
    llm_start = time.time()
    response = llm_client.generate(message, context)
    llm_ms = (time.time() - llm_start) * 1000
    print(f"[Perf] retrieve={retrieval_ms:.0f}ms llm={llm_ms:.0f}ms")
    
    return response, sources_used


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, x_username: str = Header(default="anonymous")):
    """
    Text-based chat endpoint.
    Retrieves context from RAG and generates response using LLM.
    """
    if not index_loaded or rag_system is None:
        raise HTTPException(
            status_code=503,
            detail="RAG system not initialized. Please run build_index.py first."
        )
    
    try:
        start_time = time.time()
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        response, sources_used = await loop.run_in_executor(
            executor,
            _generate_response,
            request.message
        )
        
        time_taken = time.time() - start_time

        username = (x_username or "anonymous").strip() or "anonymous"
        try:
            _log_chat_history(username, request.message, response, time_taken)
        except Exception as e:
            print(f"[DB] Chat history write error: {e}")
        
        return ChatResponse(
            response=response,
            sources_used=sources_used,
            time_taken=round(time_taken, 2)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _transcribe_audio(audio_path: str):
    """Synchronous function to transcribe audio."""
    return stt.transcribe_file(audio_path)


def _generate_tts(text: str, output_path: str):
    """Synchronous function to generate TTS."""
    return tts.speak_to_file(text, output_path)


def _audio_suffix(upload: UploadFile) -> str:
    """Infer a temp-file suffix from upload metadata."""
    content_type = (upload.content_type or "").lower()
    filename = (upload.filename or "").lower()

    if "webm" in content_type or filename.endswith(".webm"):
        return ".webm"
    if "ogg" in content_type or filename.endswith(".ogg"):
        return ".ogg"
    if "mp3" in content_type or filename.endswith(".mp3"):
        return ".mp3"
    if "wav" in content_type or filename.endswith(".wav"):
        return ".wav"

    return ".bin"


def _b64_header(text: str) -> str:
    """Encode UTF-8 text to ASCII-safe base64 for HTTP headers."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


@app.post("/voice")
async def voice(
    audio_file: UploadFile = File(...),
    x_username: str = Header(default="anonymous")
):
    """
    Voice-based chat endpoint.
    Transcribes audio, retrieves context, generates response, and returns TTS audio.
    """
    if not index_loaded or rag_system is None:
        raise HTTPException(
            status_code=503,
            detail="RAG system not initialized. Please run build_index.py first."
        )
    
    if stt is None or tts is None:
        raise HTTPException(
            status_code=503,
            detail="Voice components not initialized."
        )

    if shutil.which("ffmpeg") is None:
        raise HTTPException(
            status_code=503,
            detail="ffmpeg is not installed on the server. Voice transcription requires ffmpeg."
        )
    
    temp_audio_path = None
    output_path = None
    
    try:
        voice_start = time.time()
        content = await audio_file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

        # Save uploaded audio to temp file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=_audio_suffix(audio_file)
        ) as temp_audio:
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        # Transcribe audio
        loop = asyncio.get_event_loop()
        transcribed_text = await loop.run_in_executor(
            executor,
            _transcribe_audio,
            temp_audio_path
        )
        transcribe_ms = (time.time() - voice_start) * 1000
        
        if not transcribed_text:
            raise HTTPException(
                status_code=422,
                detail="No speech detected. Please speak clearly and try again."
            )
        
        # Generate response
        response_text, _ = await loop.run_in_executor(
            executor,
            _generate_response,
            transcribed_text
        )
        llm_pipeline_ms = (time.time() - voice_start) * 1000
        
        # Generate TTS audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
            output_path = temp_output.name
        
        await loop.run_in_executor(
            executor,
            _generate_tts,
            response_text,
            output_path
        )
        tts_total_ms = (time.time() - voice_start) * 1000
        print(
            f"[Perf][Voice] transcribe={transcribe_ms:.0f}ms "
            f"to_response={llm_pipeline_ms:.0f}ms total_with_tts={tts_total_ms:.0f}ms"
        )

        username = (x_username or "anonymous").strip() or "anonymous"
        try:
            # Voice interactions are part of chat history and stats.
            _log_chat_history(username, transcribed_text, response_text, 0.0)
        except Exception as e:
            print(f"[DB] Voice chat history write error: {e}")
        
        # Read output audio
        with open(output_path, 'rb') as f:
            audio_data = f.read()
        
        # Clean up temp files
        os.unlink(temp_audio_path)
        os.unlink(output_path)
        
        # Return audio with headers
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/wav",
            headers={
                "X-Transcribed-Text-B64": _b64_header(transcribed_text),
                "X-Response-Text-B64": _b64_header(response_text)
            }
        )
    
    except HTTPException as e:
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        if output_path and os.path.exists(output_path):
            os.unlink(output_path)
        raise e
    except RuntimeError as e:
        logger.exception("Speech-to-text engine error")
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        if output_path and os.path.exists(output_path):
            os.unlink(output_path)
        raise HTTPException(
            status_code=502,
            detail=f"Speech-to-text engine error: {e}"
        )
    except Exception as e:
        logger.exception("Voice processing failed")
        # Clean up temp files on error
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        if output_path and os.path.exists(output_path):
            os.unlink(output_path)
        
        raise HTTPException(status_code=500, detail="Voice processing failed.")


@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Text-to-speech endpoint.
    Converts text to speech and returns audio file.
    """
    if tts is None:
        raise HTTPException(
            status_code=503,
            detail="TTS not initialized."
        )
    
    output_path = None
    
    try:
        # Generate TTS audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
            output_path = temp_output.name
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            executor,
            _generate_tts,
            request.text,
            output_path
        )
        
        # Read audio file
        with open(output_path, 'rb') as f:
            audio_data = f.read()
        
        # Clean up
        os.unlink(output_path)
        
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/wav"
        )
    
    except Exception as e:
        if output_path and os.path.exists(output_path):
            os.unlink(output_path)
        
        raise HTTPException(status_code=500, detail=str(e))


class ProcessDirectoryRequest(BaseModel):
    directory_path: str = "./data/documents"
    rebuild_index: bool = False


@app.post("/process-pdf-directory")
async def process_pdf_directory(request: ProcessDirectoryRequest):
    """
    Process all PDFs in a directory and rebuild the index.
    """
    global rag_system, index_loaded
    
    try:
        # Check if directory exists
        if not os.path.exists(request.directory_path):
            raise HTTPException(status_code=404, detail="Directory not found")
        
        # Rebuild index
        if request.rebuild_index:
            # Delete existing index
            vector_store_path = "./database/vector_store"
            if os.path.exists(vector_store_path):
                import shutil
                shutil.rmtree(vector_store_path)
            
            # Reinitialize RAG system
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                executor,
                lambda: RAGSystem()
            )
            rag_system = RAGSystem()
            index_loaded = True
        
        # Count chunks
        chunks_created = len(rag_system.chunks) if hasattr(rag_system, 'chunks') else 0
        
        return {
            "status": "success",
            "directory": request.directory_path,
            "chunks_created": chunks_created
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-documents")
async def upload_documents(files: list[UploadFile] = File(...)):
    """
    Upload documents and rebuild the index.
    Deletes all existing documents before uploading new ones.
    """
    global rag_system, index_loaded
    
    try:
        docs_dir = "./data/documents"
        vector_store_path = "./database/vector_store"
        
        # Delete ALL existing documents
        if os.path.exists(docs_dir):
            shutil.rmtree(docs_dir)
        os.makedirs(docs_dir, exist_ok=True)
        
        # Delete existing vector store
        if os.path.exists(vector_store_path):
            shutil.rmtree(vector_store_path)
        
        print("[Upload] Cleared existing documents and vector store")
        
        # Save new uploaded files
        uploaded_files = []
        for file in files:
            file_path = os.path.join(docs_dir, file.filename)
            with open(file_path, 'wb') as f:
                content = await file.read()
                f.write(content)
            uploaded_files.append(file.filename)
        
        print(f"[Upload] Saved {len(uploaded_files)} new files")
        
        # Rebuild index from scratch
        loop = asyncio.get_event_loop()
        new_rag = await loop.run_in_executor(
            executor,
            RAGSystem
        )
        
        rag_system = new_rag
        index_loaded = True
        
        # Count chunks
        chunks_created = len(rag_system.chunks) if hasattr(rag_system, 'chunks') else 0
        
        print(f"[Upload] Index rebuilt with {chunks_created} chunks")
        
        return {
            "status": "success",
            "files_uploaded": len(uploaded_files),
            "chunks_created": chunks_created,
            "filenames": uploaded_files
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat-history")
async def get_chat_history(username: Optional[str] = None, limit: int = 0):
    """Get recent chat history for a user"""
    try:
        _ensure_chat_history_table()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        normalized_username = (username or "").strip()
        normalized_limit = max(0, limit)

        if normalized_username and normalized_limit > 0:
            cursor.execute(
                """
                SELECT id, username, question, response, model_used, timestamp, time_taken
                FROM chat_history
                WHERE username = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (normalized_username, normalized_limit),
            )
        elif normalized_username:
            cursor.execute(
                """
                SELECT id, username, question, response, model_used, timestamp, time_taken
                FROM chat_history
                WHERE username = ?
                ORDER BY timestamp DESC
                """,
                (normalized_username,),
            )
        elif normalized_limit > 0:
            cursor.execute(
                """
                SELECT id, username, question, response, model_used, timestamp, time_taken
                FROM chat_history
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (normalized_limit,),
            )
        else:
            cursor.execute(
                """
                SELECT id, username, question, response, model_used, timestamp, time_taken
                FROM chat_history
                ORDER BY timestamp DESC
                """
            )
        rows = cursor.fetchall()
        conn.close()
        return {
            "username": normalized_username or None,
            "history": [
                {
                    "id": row[0],
                    "username": row[1],
                    "question": row[2],
                    "response": row[3],
                    "model_used": row[4],
                    "timestamp": row[5],
                    "time_taken": row[6]
                }
                for row in rows
            ]
        }
    except Exception as e:
        print(f"[DB] Chat history fetch error: {e}")
        return {"username": username, "history": []}


@app.get("/stats")
async def get_stats():
    """Get real system statistics"""
    try:
        docs_path = "./data/documents"
        files = [f for f in os.listdir(docs_path) if f.endswith(('.pdf', '.txt'))] if os.path.exists(docs_path) else []
        total_size = sum(os.path.getsize(os.path.join(docs_path, f)) for f in files) / (1024*1024) if files else 0
        pdf_count = len([f for f in files if f.endswith('.pdf')])
        txt_count = len([f for f in files if f.endswith('.txt')])
        
        _ensure_chat_history_table()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        total_queries = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT username) FROM chat_history WHERE date(timestamp) = date('now')")
        active_users = cursor.fetchone()[0]
        conn.close()
        
        return {
            "totalDocuments": len(files),
            "totalSizeMB": round(total_size, 1),
            "totalChunks": rag_system.index.ntotal if rag_system and hasattr(rag_system, 'index') else 0,
            "totalQueries": total_queries,
            "activeUsers": active_users,
            "documentTypes": [
                {"name": "PDF", "value": pdf_count, "color": "#3533cd"},
                {"name": "TXT", "value": txt_count, "color": "#7c96fd"}
            ]
        }
    except Exception as e:
        print(f"[Stats] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
