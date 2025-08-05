#!/bin/bash
# Script to download required models for AgentGraphSociety

echo "Waiting for Ollama to be ready..."
sleep 10

# Check if Ollama is responding
until curl -f http://ollama:11434/api/tags > /dev/null 2>&1; do
    echo "Waiting for Ollama..."
    sleep 5
done

echo "Ollama is ready. Downloading models..."

# Download models suitable for agent simulation
models=(
    "mistral:7b-instruct"    # Best general purpose model
    "neural-chat:7b"         # Good for conversational agents
    "phi-2"                  # Small, fast model for testing
)

for model in "${models[@]}"; do
    echo "Pulling $model..."
    ollama pull "$model" || echo "Failed to pull $model"
done

echo "Model download complete!"

# List available models
echo "Available models:"
ollama list