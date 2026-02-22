# Voice RAG Pipeline - Fully Offline

A complete voice-based Retrieval-Augmented Generation system running entirely offline on Linux, optimized for CPU-only processing with 16GB RAM.

## Features

- **Fully Offline**: Works without internet after initial setup
- **Voice Input**: Automatic silence detection for hands-free recording
- **RAG System**: FAISS vector database with BGE embeddings
- **Local LLM**: Ollama integration (llama3.2:3b, qwen2.5:7b, deepseek-r1:7b)
- **Voice Output**: Natural TTS using Piper
- **CPU Optimized**: int8 quantization for efficient inference
- **Automatic Logging**: Every search is logged with timestamps and performance metrics

## Tech Stack

- **STT**: faster-whisper (small model, CPU, int8)
- **Embeddings**: BAAI/bge-small-en-v1.5 (384 dimensions)
- **Vector DB**: FAISS with cosine similarity
- **LLM**: Ollama (localhost:11434)
- **TTS**: Piper TTS (en_US-lessac-medium)
- **Audio**: sounddevice with automatic silence detection

## Quick Start

### Prerequisites

1. **Python 3.11+** installed
2. **Ollama** installed from https://ollama.ai

### Installation

1. Navigate to the project directory:
```bash
cd Open_Source_RAG_With_Speech
```

2. Create virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Pull Ollama models (choose at least one):
```bash
ollama pull llama3.2:3b      # Fastest (2GB)
ollama pull qwen2.5:7b        # Balanced (4.7GB)
ollama pull deepseek-r1:7b    # Most capable (4.7GB)
```

4. Add your documents:
- Place .txt or .pdf files in `data/documents/`
- The system will automatically index them on first run

### Usage

1. Start Ollama server (in a separate terminal):
```bash
ollama serve
```

2. Run the application:
```bash
python app.py
```

3. Select your preferred model from the menu

4. Interact:
- Press Enter when prompted
- Speak your question clearly
- Wait for silence detection (visual feedback: █ loud, ▓ medium, ░ silence)
- Listen to the AI response

5. Exit: Press Ctrl+C

## Project Structure

```
Open_Source_RAG_With_Speech/
├── app.py                    # Entry point
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
│
├── src/                     # Core application code
│   ├── main.py              # Model selector + launcher
│   ├── voice_rag.py         # Main voice RAG pipeline
│   ├── config.py            # Configuration settings
│   ├── audio.py             # Audio recording with silence detection
│   ├── stt.py               # Speech-to-text (Whisper)
│   ├── rag.py               # RAG system (FAISS + embeddings)
│   ├── llm.py               # Ollama LLM integration
│   ├── tts.py               # Text-to-speech (Piper)
│   └── logger.py            # Logging system
│
├── util/                    # Utility scripts
│   ├── model_manager.py     # Interactive model selection
│   ├── compare_models.py    # Benchmark different models
│   └── run_with_model.py    # Run with specific model
│
├── data/                    # User data
│   └── documents/           # Your PDF/TXT knowledge base
│
├── database/                # Vector database
│   └── vector_store/        # FAISS index + chunks (auto-generated)
│
├── model/                   # AI models
│   ├── models/              # BGE embedding model
│   │   └── bge-small-en-v1.5/
│   └── ollama_models/       # Ollama model information
│
├── piper/                   # Piper TTS files
│   ├── piper_exe            # TTS executable
│   ├── en_US-lessac-medium.onnx
│   └── espeak-ng-data/
│
└── logs/                    # Application logs
    ├── searches.log         # All searches (JSON format)
    └── session_*.log        # Detailed session logs
```

## File Descriptions

### Core Application (`src/`)

- **main.py**: Model selector that runs on startup, allows choosing which Ollama model to use
- **voice_rag.py**: Main pipeline orchestrating STT → RAG → LLM → TTS
- **config.py**: Central configuration (model names, paths, audio settings)
- **audio.py**: Records audio with automatic silence detection and visual feedback
- **stt.py**: Transcribes audio to text using faster-whisper
- **rag.py**: Manages document indexing, embedding, and retrieval using FAISS
- **llm.py**: Interfaces with Ollama for text generation
- **tts.py**: Converts text responses to speech using Piper
- **logger.py**: Logs all searches with timestamps, context, responses, and performance

### Utilities (`util/`)

- **model_manager.py**: Lists available Ollama models and handles selection
- **compare_models.py**: Benchmarks multiple models on the same question
- **run_with_model.py**: Directly run with a specific model (bypasses selector)

## Configuration

Edit `src/config.py` to customize behavior:

### Model Settings
```python
OLLAMA_MODEL = "llama3.2:3b"  # Change to qwen2.5:7b or deepseek-r1:7b
WHISPER_MODEL_SIZE = "small"   # Options: tiny, base, small, medium
EMBEDDING_MODEL_PATH = "./model/models/bge-small-en-v1.5"
```

### RAG Settings
```python
CHUNK_SIZE = 500        # Characters per chunk
CHUNK_OVERLAP = 50      # Overlap between chunks
TOP_K = 3               # Number of context chunks to retrieve
```

### Audio Settings
```python
SAMPLE_RATE = 16000           # Audio sample rate
SILENCE_THRESHOLD = 0.02      # Lower = more sensitive
SILENCE_DURATION = 1.5        # Seconds of silence before stopping
```

## How to Modify the Code

### Adding New Documents

1. Place files in `data/documents/`
2. Delete `database/vector_store/` to force reindexing
3. Run the app - it will automatically rebuild the index

### Switching Models

Option 1: Use the built-in selector (runs on every startup)
```bash
python app.py
```

Option 2: Edit `src/config.py` directly
```python
OLLAMA_MODEL = "qwen2.5:7b"  # Change this line
```

Option 3: Use the utility script
```bash
python util/run_with_model.py qwen2.5:7b
```

### Adjusting Silence Detection

If recording stops too early or too late, edit `src/config.py`:

```python
SILENCE_THRESHOLD = 0.02  # Increase if stops too early (0.03-0.05)
SILENCE_DURATION = 1.5    # Increase if stops too early (2.0-3.0)
```

### Changing TTS Voice

1. Download a different Piper voice from https://github.com/rhasspy/piper/releases
2. Place .onnx and .onnx.json files in `piper/`
3. Update `src/config.py`:
```python
PIPER_VOICE = "./piper/your-new-voice.onnx"
```

### Adding Custom Processing

To add custom logic between steps, edit `src/voice_rag.py`:

```python
# After STT
text = stt.transcribe(audio_data)
text = your_custom_function(text)  # Add your processing here

# After RAG
context = rag.retrieve(text)
context = your_filter_function(context)  # Filter context

# After LLM
response = llm.generate(text, context)
response = your_postprocess(response)  # Modify response
```

## Logging

Every search interaction is automatically logged to two files:

### searches.log (JSON format)
```json
{"timestamp": "2026-02-22T...", "question": "...", "model": "llama3.2:3b", "response": "...", "duration_seconds": 33.8, "context_length": 1500}
```

### session_YYYYMMDD_HHMMSS.log (Detailed)
```
[2026-02-22T...]
Question: What does the text say about difficulties?
Model: llama3.2:3b
Duration: 33.82s
Context Length: 1500 chars
Response: The text suggests...
--------------------------------------------------
```

Logs are stored in the `logs/` directory and never deleted automatically.

## Model Comparison

### Performance Benchmarks (on sample question)

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| llama3.2:3b | 2.0 GB | ~34s | Good for quick responses |
| qwen2.5:7b | 4.7 GB | ~74s | Balanced performance |
| deepseek-r1:7b | 4.7 GB | ~157s | Most detailed reasoning |

To benchmark on your hardware:
```bash
python util/compare_models.py
```

## Troubleshooting

### Ollama Not Running
```bash
# Start Ollama server
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

### Audio Recording Issues
```bash
# Test audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Vector Store Rebuild
```bash
# Force reindexing of documents
rm -rf database/vector_store/
python app.py
```

### Model Not Found
```bash
# List installed models
ollama list

# Pull missing model
ollama pull llama3.2:3b
```

### Import Errors
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## System Requirements

- **OS**: Linux (tested on Ubuntu)
- **Python**: 3.11+
- **RAM**: 16GB minimum
- **CPU**: AVX2 support recommended
- **Storage**: ~10GB for models and dependencies
- **Audio**: Microphone and speakers/headphones

## Ollama Models

The system supports any Ollama model. Recommended models:

- **llama3.2:3b** - Fastest, good for quick interactions
- **qwen2.5:7b** - Balanced speed and quality
- **deepseek-r1:7b** - Best reasoning, slower
- **mistral:7b** - Alternative 7B option

Pull models with:
```bash
ollama pull <model-name>
```

View installed models:
```bash
ollama list
```

## Tips for Best Results

1. **Speak clearly** and at a normal pace
2. **Wait for silence detection** - don't interrupt the recording
3. **Use specific questions** - "What does Marcus Aurelius say about anger?" vs "Tell me about anger"
4. **Add relevant documents** - The more context, the better the answers
5. **Choose the right model** - Use llama3.2:3b for speed, deepseek-r1:7b for depth
6. **Check logs** - Review `logs/searches.log` to see what's being retrieved

## License

MIT License - Feel free to use and modify
