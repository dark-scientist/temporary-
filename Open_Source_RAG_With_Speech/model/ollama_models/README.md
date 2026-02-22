# Ollama Models Information

This folder contains information about Ollama models used in the Voice RAG Pipeline.

## Available Models

See `models_info.json` for detailed specifications of each model.

## Quick Reference

### llama3.2:3b (Fastest)
- **Speed**: ⚡⚡⚡ (~34s per response)
- **Quality**: ⭐⭐⭐
- **Best for**: Quick interactions, fast Q&A
- **Size**: 2.0 GB

### qwen2.5:7b (Balanced)
- **Speed**: ⚡⚡ (~74s per response)
- **Quality**: ⭐⭐⭐⭐
- **Best for**: Balanced performance, good reasoning
- **Size**: 4.7 GB

### deepseek-r1:7b (Most Capable)
- **Speed**: ⚡ (~157s per response)
- **Quality**: ⭐⭐⭐⭐⭐
- **Best for**: Complex reasoning, detailed analysis
- **Size**: 4.7 GB

## How to Switch Models

### Method 1: Model Selector (Recommended)
Run the app and select from the menu:
```bash
python app.py
```

### Method 2: Edit Config
Edit `src/config.py`:
```python
OLLAMA_MODEL = "llama3.2:3b"  # Change to desired model
```

### Method 3: Utility Script
```bash
python util/run_with_model.py qwen2.5:7b
```

## Installing New Models

1. Browse available models:
```bash
ollama list
```

2. Pull a new model:
```bash
ollama pull <model-name>
```

3. It will automatically appear in the model selector

## Model Storage

Ollama stores models in:
- Linux: `~/.ollama/models/`
- The models are shared across all applications using Ollama

## Performance Tips

- **For speed**: Use llama3.2:3b
- **For quality**: Use deepseek-r1:7b
- **For balance**: Use qwen2.5:7b
- **Low RAM**: Stick to 3B models
- **More RAM**: Try 7B or 13B models

## Benchmarking

To compare models on your hardware:
```bash
python util/compare_models.py
```

This will test all installed models with the same question and show:
- Response time
- Response length
- Which is fastest
