@echo off
echo Building webcam streamer Docker image...
docker build -t webcam-streamer .

echo Starting webcam streamer container...
docker run -p 8554:8554 --privileged webcam-streamer

pause
