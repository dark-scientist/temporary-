#!/bin/bash

echo "Starting Dotryder Voice RAG..."
echo ""

# Check ollama is running
if ! curl -s http://localhost:11434 > /dev/null; then
    echo "Ollama not running. Starting it..."
    ollama serve &
    sleep 3
fi

# Start FastAPI backend
cd "$(dirname "$0")"
source ../venv/bin/activate
echo "Starting API on http://localhost:8000"
python api.py &
API_PID=$!
sleep 2

# Start React frontend
echo "Starting Frontend on http://localhost:5173"
cd frontend && npm run dev &
FRONT_PID=$!

echo ""
echo "============================================"
echo " Dotryder is running!"
echo " Open: http://localhost:5173"
echo " API Docs: http://localhost:8000/docs"
echo " Press Ctrl+C to stop everything"
echo "============================================"

# Wait and cleanup on Ctrl+C
trap "kill $API_PID $FRONT_PID; echo 'Stopped.'; exit" INT
wait
