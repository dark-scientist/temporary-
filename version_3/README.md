# Dotryder Voice RAG System v3

Complete offline voice-based RAG (Retrieval-Augmented Generation) system with login authentication, personalized dashboard, and chat history tracking.

## 🚀 Features

### Core Functionality
- **Voice Input/Output**: Speech-to-text (Whisper) and text-to-speech (Piper)
- **Document Intelligence**: FAISS vector search with Ollama embeddings
- **LLM Integration**: Local Ollama models (gemma:2b/gemma3:4b)
- **Fully Offline**: No external API calls after setup

### User Interface
- **Login System**: Secure authentication (prithwin, kiran, admin)
- **Personalized Home**: Live dashboard with user-specific data
- **Interactive Charts**: Document analytics and system statistics
- **Chat History**: SQLite-powered conversation tracking
- **Modern UI**: Dotryder brand colors and responsive design

### Performance Optimizations
- **Ultra-low Latency**: <3 second response times
- **Smart Caching**: Keep models hot with 5-minute keep_alive
- **Optimized Settings**: Minimal context, greedy decoding
- **Threaded Processing**: Maximum CPU utilization

## 📋 Prerequisites

- **Python 3.8+** with virtual environment
- **Node.js 16+** and npm
- **Ollama** server running locally
- **ffmpeg** for audio processing
- **Linux/Ubuntu** (tested environment)

## 🛠️ Quick Setup

### 1. Install Dependencies
```bash
# Create virtual environment
python3 -m venv ~/projects/venv
source ~/projects/venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Install Node.js dependencies
cd frontend
npm install
cd ..
```

### 2. Setup Ollama Models
```bash
# Install required models
ollama pull gemma:2b          # Fast model
ollama pull gemma3:4b         # Quality model
ollama pull nomic-embed-text  # Embeddings
```

### 3. Build Document Index
```bash
# Index the included Dotryder documents
python build_index.py
```

### 4. Start Services
```bash
# Terminal 1: Start API backend
source ~/projects/venv/bin/activate
python api.py

# Terminal 2: Start React frontend
cd frontend
npm run dev
```

### 5. Access Application
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔐 Login Credentials

| Username | Password | Role |
|----------|----------|------|
| prithwin | prithwin123 | User |
| kiran | kiran123 | User |
| admin | admin123 | Admin |

## 📊 Included Documents

The system comes pre-loaded with Dotryder company documents:

1. **Dotryder Capabilities Deck** (20MB) - Company overview and services
2. **Bharat Electricity Summit 2026** (1.4MB) - Exhibitor manual
3. **Startup Pavilion Design** (347KB) - Design specifications

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │    │   FastAPI Backend │    │   Ollama Server │
│   (Port 5173)   │◄──►│   (Port 8000)    │◄──►│   (Port 11434)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Login    │    │   SQLite DB      │    │   FAISS Index   │
│   Chat History  │    │   Chat Logs      │    │   Vector Store  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |
| GET | `/stats` | Real-time system statistics |
| GET | `/chat-history` | User chat history |
| POST | `/chat` | Text-based chat |
| POST | `/voice` | Voice-based chat |
| POST | `/tts` | Text-to-speech conversion |
| POST | `/log-login` | Log user sessions |

## ⚡ Performance Tuning

Current optimizations for sub-3 second responses:

```python
# LLM Settings (src/llm.py)
"num_predict": 30,    # Very short responses
"temperature": 0.1,   # Deterministic output
"num_thread": 8,      # Max CPU threads
"num_ctx": 128,       # Minimal context
"top_k": 1,           # Greedy decoding
"keep_alive": "5m"    # Keep model hot
```

## 🔧 Configuration

### Model Selection
```python
# src/config.py
USE_QUALITY_MODEL = False  # True for gemma3:4b, False for gemma:2b
```

### Voice Settings
```python
# src/config.py
WHISPER_MODEL = "small"    # STT model size
TTS_VOICE = "lessac"       # TTS voice model
```

## 📁 Project Structure

```
version_3/
├── api.py                 # FastAPI backend server
├── build_index.py         # Document indexing script
├── requirements.txt       # Python dependencies
├── src/                   # Core modules
│   ├── config.py         # Configuration settings
│   ├── llm.py            # Ollama LLM integration
│   ├── rag.py            # RAG system logic
│   ├── stt.py            # Speech-to-text
│   └── tts.py            # Text-to-speech
├── frontend/             # React application
│   ├── src/components/   # UI components
│   └── package.json      # Node dependencies
├── data/documents/       # PDF documents
├── database/vector_store/ # FAISS index
├── logs/                 # SQLite database
└── piper/               # TTS models and binaries
```

## 🐛 Troubleshooting

### Common Issues

**API won't start:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Verify models are installed
ollama list
```

**Slow responses:**
```bash
# Check model is loaded
ollama ps

# Verify system resources
htop
```

**Voice not working:**
```bash
# Install ffmpeg
sudo apt install ffmpeg

# Check microphone permissions
arecord -l
```

### Performance Monitoring

```bash
# Test API response time
curl -w "Total: %{time_total}s\n" -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is Dotryder?"}'

# Monitor system resources
watch -n 1 'ps aux | grep -E "(ollama|python|node)"'
```

## 🚀 Production Deployment

### Environment Variables
```bash
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_ORIGINS="*"
export NODE_ENV=production
```

### Systemd Services
Create service files for auto-startup:
- `dotryder-api.service` (FastAPI backend)
- `dotryder-frontend.service` (React build)
- `ollama.service` (Ollama server)

## 📝 Development

### Adding New Documents
```bash
# Copy PDFs to documents folder
cp new_document.pdf data/documents/

# Rebuild index
python build_index.py
```

### Customizing UI
- Brand colors: `frontend/src/index.css`
- Components: `frontend/src/components/`
- Login users: `frontend/src/components/Login.jsx`

### Model Configuration
- Fast responses: `USE_QUALITY_MODEL = False`
- Better quality: `USE_QUALITY_MODEL = True`
- Custom models: Update `OLLAMA_MODEL` in `src/config.py`

## 📄 License

Proprietary - Dotryder Private Limited

## 🤝 Support

For technical support or questions:
- Internal documentation: `/docs`
- System logs: `logs/`
- Health check: `http://localhost:8000/health`

---

**Version**: 3.0  
**Last Updated**: March 2026  
**Optimized for**: Production deployment with <3s response times