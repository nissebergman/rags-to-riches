FROM ollama/ollama:latest

# Install bash
RUN apt-get update && apt-get install -y bash

# Copy start script
COPY start-ollama.sh /start-ollama.sh
RUN chmod +x /start-ollama.sh

ENTRYPOINT ["/start-ollama.sh"]