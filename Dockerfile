# ==============================================
# Stage 1: Conda Builder (for AI/ML packages)
# ==============================================
FROM continuumio/miniconda3:latest as conda-builder

# Create conda environment with all AI/ML packages
RUN conda create -n tamil python=3.10 -y && \
    conda install -n tamil -c pytorch -c conda-forge \
    pytorch==2.1.0 \
    torchvision==0.16.0 \
    torchaudio==2.1.0 \
    transformers==4.35.0 \
    numpy==1.24.0 \
    pandas==2.1.0 \
    scikit-learn==1.3.0 \
    pip \
    -y

# Activate environment and install pip packages
ENV PATH /opt/conda/envs/tamil/bin:$PATH
RUN pip install --no-cache-dir \
    langchain==0.0.340 \
    chromadb==0.4.18 \
    openai-whisper==20231117

# ==============================================
# Stage 2: Runtime (smaller final image)
# ==============================================
FROM python:3.10-slim-bookworm

# Set environment variables
ENV LANG=ta_IN.UTF-8 \
    LC_ALL=ta_IN.UTF-8 \
    TZ=Asia/Kolkata \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH=/opt/conda/envs/tamil/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Audio processing
    portaudio19-dev \
    libsndfile1 \
    ffmpeg \
    sox \
    # System utilities
    curl \
    wget \
    git \
    # Tamil locale support
    locales \
    tzdata \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    # Configure Tamil locale
    && sed -i '/ta_IN.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen ta_IN.UTF-8 \
    # Set timezone
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash april && \
    mkdir -p /app && chown april:april /app

WORKDIR /app

# Copy conda environment from builder stage
COPY --from=conda-builder /opt/conda /opt/conda

# Install remaining Python packages (lightweight ones)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    pyaudio==0.2.13 \
    SpeechRecognition==3.10.0 \
    gtts==2.3.2 \
    simpleaudio==1.0.4 \
    streamlit==1.28.0 \
    plotly==5.17.0 \
    python-dotenv==1.0.0

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy application code
COPY --chown=april:april . .

# Create necessary directories
RUN mkdir -p /app/data/documents \
             /app/data/audio_cache \
             /app/data/chroma_db \
             /app/logs \
    && chown -R april:april /app

# Create sample Tamil document
RUN echo "வணக்கம்! தமிழ் குரு உதவியாளருக்கு வரவேற்கிறோம்." > /app/data/documents/வரவேற்பு.txt && \
    echo "" >> /app/data/documents/வரவேற்பு.txt && \
    echo "உங்கள் திட்டங்களை இங்கு சேர்க்கவும்:" >> /app/data/documents/வரவேற்பு.txt && \
    echo "1. வார இறுதி திட்டங்கள்" >> /app/data/documents/வரவேற்பு.txt && \
    echo "2. மாதாந்திர நோக்கங்கள்" >> /app/data/documents/வரவேற்பு.txt && \
    echo "3. நீண்டகால இலக்குகள்" >> /app/data/documents/வரவேற்பு.txt && \
    chown april:april /app/data/documents/வரவேற்பு.txt

# Switch to non-root user
USER tamiluser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Expose ports
EXPOSE 8501 
EXPOSE 11434

# ==============================================
# Entrypoint Script
# ==============================================
COPY --chown=tamiluser:tamiluser docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command
CMD ["python", "main.py"]
