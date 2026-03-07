# Dotryder Voice RAG — Setup Guide

## System Requirements
- OS: Ubuntu / Debian Linux
- Python: 3.11+
- RAM: 16GB minimum
- Storage: 15GB free (for models)
- Audio: Microphone and speakers

## Step 1 — System Dependencies
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv portaudio19-dev espeak-ng alsa-utils -y
```

## Step 2 — Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Step 3 — Pull Required Models
```bash
ollama pull gemma:2b
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

## Step 4 — Clone and Setup Project
```bash
cd version_2
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 5 — Add Documents
Place your .pdf or .txt files into:
```
data/documents/
```

## Step 6 — Build Vector Index
```bash
source venv/bin/activate
python build_index.py
```

## Step 7 — Setup Frontend
```bash
cd frontend
npm install
cd ..
```

## Step 8 — Copy Logo Asset
```bash
cp Dot-trans.png frontend/public/Dot-trans.png
```

## Running the Application

Terminal 1 — Start Ollama:
```bash
ollama serve
```

Terminal 2 — Start API:
```bash
source venv/bin/activate
python api.py
```

Terminal 3 — Start Frontend:
```bash
cd frontend
npm run dev
```

Open browser: http://localhost:5173
API Docs: http://localhost:8000/docs

## Switching Models
Edit `src/config.py`:
- For speed: `USE_QUALITY_MODEL = False`  (uses gemma:2b)
- For quality: `USE_QUALITY_MODEL = True`  (uses gemma3:4b)

## Adding New Documents
1. Place files in `data/documents/`
2. Delete `database/vector_store/` folder
3. Run: `python build_index.py`

## Troubleshooting

Ollama not running:
```bash
ollama serve
```

Audio not working:
```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

Index not found:
```bash
python build_index.py
```

Dependencies missing:
```bash
pip install -r requirements.txt --force-reinstall
```

API not responding:
```bash
curl http://localhost:8000/health
```
