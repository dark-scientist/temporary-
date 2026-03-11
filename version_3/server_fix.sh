#!/bin/bash

echo "=== Quick Server Fix ==="
echo "Fixing config to use available models only"
echo

# Navigate to project directory
cd ~/version_3 || { echo "Error: version_3 directory not found"; exit 1; }

echo "✓ Config updated to use llama3.2:3b for both primary and fallback"
echo "✓ Timeout increased to 300 seconds"
echo

echo "Starting API server..."
python api.py