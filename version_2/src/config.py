"""
Configuration file for Voice RAG Pipeline
All settings for models, paths, and audio parameters
"""

# Ollama LLM Configuration
OLLAMA_MODEL = "llama3.2:3b"  # Change this to switch models: llama3.2:3b, qwen2.5:7b, deepseek-r1:7b
OLLAMA_URL = "http://localhost:11434"

# Whisper STT Configuration
WHISPER_MODEL_SIZE = "small"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

# Embedding Model Configuration
EMBEDDING_MODEL_PATH = "./model/models/bge-small-en-v1.5"

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
