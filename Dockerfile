FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install MediaMTX
RUN wget -O /tmp/mediamtx.tar.gz https://github.com/bluenviron/mediamtx/releases/download/v1.15.3/mediamtx_v1.15.3_linux_amd64.tar.gz \
    && tar -xzf /tmp/mediamtx.tar.gz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/mediamtx \
    && rm /tmp/mediamtx.tar.gz

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY mediamtx.yml .
COPY config.json .

# Expose RTSP port
EXPOSE 8554

# Create entrypoint script
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Default to headless mode, but allow GUI override
CMD ["python", "src/headless_main.py"]
