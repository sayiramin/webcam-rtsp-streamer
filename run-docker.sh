#!/bin/bash

echo "Building webcam streamer Docker image..."
docker build -t webcam-streamer .

echo "Starting webcam streamer container..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    docker run -p 8554:8554 --device=/dev/video0 webcam-streamer
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    docker run -p 8554:8554 --device=/dev/video0 webcam-streamer
else
    # Windows/WSL2
    docker run -p 8554:8554 --privileged webcam-streamer
fi
