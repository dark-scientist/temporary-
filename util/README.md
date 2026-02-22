# Utility Scripts

This folder contains utility scripts for managing and testing the Voice RAG Pipeline.

## Available Scripts

### model_manager.py
Interactive model selector that lists all installed Ollama models and allows you to choose one.

Usage:
```bash
python util/model_manager.py
```

Features:
- Lists all installed Ollama models
- Interactive selection menu
- Automatically updates `src/config.py` with selected model

### compare_models.py
Benchmarks multiple Ollama models with the same question to compare speed and quality.

Usage:
```bash
python util/compare_models.py
```

Features:
- Tests all installed models
- Measures response time for each
- Shows response length
- Identifies fastest model
- Custom question support

### run_with_model.py
Directly run the Voice RAG pipeline with a specific model (bypasses the selector).

Usage:
```bash
python util/run_with_model.py <model-name>
```

Examples:
```bash
python util/run_with_model.py llama3.2:3b
python util/run_with_model.py qwen2.5:7b
python util/run_with_model.py deepseek-r1:7b
```

Features:
- Quick model switching
- Updates config automatically
- Launches pipeline immediately

## When to Use Each Script

- **model_manager.py**: When you want to see all available models and choose interactively
- **compare_models.py**: When you want to benchmark models on your hardware
- **run_with_model.py**: When you know which model you want and want to start quickly

## Notes

All scripts require:
- Ollama to be installed and running
- At least one Ollama model pulled
- Python virtual environment activated (if using venv)
