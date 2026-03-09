"""
Configuration file for Voice RAG Pipeline
All settings for models, paths, and audio parameters
"""

# Ollama LLM Configuration
OLLAMA_URL = "http://localhost:11434"

# Production models — both available, switch via this config
OLLAMA_MODEL = "gemma3:4b"          # Fast model — default
OLLAMA_MODEL_QUALITY = "gemma3:4b" # Quality model — for complex queries
OLLAMA_MODEL_FALLBACK = "llama3.2:3b"  # Backup model if primary fails

# To use quality model set USE_QUALITY_MODEL = True
USE_QUALITY_MODEL = True

# Active model — used by all modules
ACTIVE_MODEL = OLLAMA_MODEL_QUALITY if USE_QUALITY_MODEL else OLLAMA_MODEL

# Whisper STT Configuration
WHISPER_MODEL_SIZE = "small"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

# Embedding Model Configuration - Using Ollama
EMBEDDING_MODEL = "nomic-embed-text"  # served via Ollama
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
# EMBEDDING_MODEL_PATH = "./model/models/bge-small-en-v1.5"  # Old local model - no longer used

# Piper TTS Configuration
PIPER_EXE = "./piper/piper_exe"
PIPER_VOICE = "./piper/en_US-lessac-medium.onnx"

# RAG Configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3

# Audio Configuration
SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 0.02
SILENCE_DURATION = 1.5

# Paths
DOCUMENTS_PATH = "./data/documents"
VECTOR_STORE_PATH = "./database/vector_store"
