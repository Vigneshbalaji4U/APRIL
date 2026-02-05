#!/bin/bash
set -e

echo "========================================="
echo "????? ???? ????????? ????????????"
echo "Tamil Voice Assistant Starting"
echo "========================================="

# Ensure Tamil locale
export LANG=ta_IN.UTF-8
export LC_ALL=ta_IN.UTF-8

# Create directories if they don't exist
mkdir -p /app/data/documents \
         /app/data/audio_cache \
         /app/data/chroma_db \
         /app/logs

# Set proper permissions
chmod 755 /app/data /app/logs

# Start Ollama in background if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "?? Starting Ollama server..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 5  # Give Ollama time to start
    
    # Pull the model we need
    echo "?? Downloading language model..."
    ollama pull llama3.2:3b || echo "?? Model download failed, will retry later"
fi

# Check if knowledge base exists
if [ ! -d "/app/data/chroma_db" ] || [ -z "$(ls -A /app/data/chroma_db 2>/dev/null)" ]; then
    echo "?? Creating knowledge base from documents..."
    python -c "
import sys
sys.path.append('/app')
try:
    from src.knowledge_base import TamilKnowledgeBase
    kb = TamilKnowledgeBase('/app/data/documents', '/app/data/chroma_db')
    kb.build_knowledge_base()
    print('? Knowledge base created successfully')
except Exception as e:
    print(f'?? Knowledge base creation failed: {e}')
"
else
    echo "? Knowledge base found"
fi

# Count Tamil documents
DOC_COUNT=$(find /app/data/documents -name "*.txt" -o -name "*.pdf" -o -name "*.docx" 2>/dev/null | wc -l)
echo "?? Found $DOC_COUNT document(s) in /app/data/documents/"

# Display audio status
if command -v arecord > /dev/null 2>&1; then
    echo "?? Audio input available"
else
    echo "?? Audio input not detected (text mode only)"
fi

echo "========================================="
echo "?? Web Interface: http://localhost:8501"
echo "?? Ollama API:    http://localhost:11434"
echo "?? Documents:     /app/data/documents/"
echo "========================================="
echo ""
echo "???????? ????????: '????' ????? ?????????"
echo "Voice Mode: Say '????' (Uthavi)"
echo ""
echo "???????: '????????' ?????? Ctrl+C"
echo "Stop: Say '????????' (Niruthu) or Ctrl+C"
echo "========================================="

# Execute the main command
exec "$@"