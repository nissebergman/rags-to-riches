#!/bin/bash

# Start Ollama service
ollama serve &

# Wait for Ollama to be fully up
sleep 8

# Pull models
ollama pull mistral:7b
ollama pull mxbai-embed-large

# Start Streamlit
exec streamlit run app.py --server.address=0.0.0.0 --server.port=8501