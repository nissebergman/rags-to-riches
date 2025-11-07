#!/bin/bash

# Start Ollama service
ollama serve &

# Wait for Ollama to initialize
sleep 15  # increase if needed

# Pull models
ollama pull gemma2:2b
while ! ollama show | grep -q "gemma2:2b"; do
    echo "Waiting for gemma2:2b to finish downloading..."
    sleep 5
done

ollama pull mxbai-embed-large
while ! ollama show | grep -q "mxbai-embed-large"; do
    echo "Waiting for mxbai-embed-large to finish downloading..."
    sleep 5
done


# Start Streamlit
exec streamlit run app.py --server.address=0.0.0.0 --server.port=8501