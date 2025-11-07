# Use Python 3.9 as base image
# Use NVIDIA's CUDA base image
# FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04 as nvidia_base

# Use Intel's OneAPI base image as alternative
FROM intel/oneapi-basekit:latest as intel_base

# Install AMD support
# FROM rocm/dev-ubuntu-22.04 as amd_base

FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy GPU runtime dependencies from base images
# COPY --from=nvidia_base /usr/local/cuda/lib64 /usr/local/cuda/lib64
COPY --from=intel_base /opt/intel/oneapi /opt/intel/oneapi
# COPY --from=amd_base /opt/rocm /opt/rocm

# Set environment variables
# ENV LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"
ENV ONEAPI_ROOT="/opt/intel/oneapi"
ENV PYTORCH_ENABLE_INTEL_GPU=1
ENV HSA_OVERRIDE_GFX_VERSION=10.3.0
# ENV ROCM_PATH="/opt/rocm"

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Install Ollama (Note: Ollama should ideally run as a separate service)
RUN curl -L https://ollama.ai/download/ollama-linux-amd64 -o /usr/local/bin/ollama \
    && chmod +x /usr/local/bin/ollama

# Create startup script with GPU detection
RUN echo '#!/bin/bash\n\
# if [ -x "$(command -v rocm-smi)" ]; then\n\
#     echo "AMD GPU detected"\n\
#     export HSA_OVERRIDE_GFX_VERSION=10.3.0\n\
# elif [ -x "$(command -v nvidia-smi)" ]; then\n\
#     echo "NVIDIA GPU detected"\n\
#     export CUDA_VISIBLE_DEVICES=0\n\
if [ -d "/opt/intel/oneapi" ]; then\n\
    echo "Intel GPU detected"\n\
    export ONEAPI_DEVICE_SELECTOR=gpu\n\
else\n\
    echo "No GPU detected, using CPU"\n\
fi\n\
ollama serve &\n\
sleep 10\n\
ollama pull mistral:7b\n\
ollama pull mxbai-embed-large\n\
streamlit run app.py --server.address=0.0.0.0 --server.port=8501\n\
' > /app/start.sh \
    && chmod +x /app/start.sh

# Expose Streamlit default port
EXPOSE 8501

# Start the application
CMD ["/app/start.sh"]