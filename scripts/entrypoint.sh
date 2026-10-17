#!/usr/bin/env bash
set -e

# Run FastAPI backend in the background
echo "Starting Cascade FastAPI backend on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait for backend to be ready
sleep 2

# Run Streamlit frontend in the foreground
echo "Starting Cascade Streamlit Dashboard on port 7860..."
streamlit run ui/dashboard.py \
    --server.port=7860 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
