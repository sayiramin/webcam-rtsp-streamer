Write-Host "Building webcam streamer Docker image..." -ForegroundColor Green
docker build -t webcam-streamer .

Write-Host "Starting webcam streamer container..." -ForegroundColor Green
docker run -p 8554:8554 --privileged webcam-streamer

Read-Host "Press Enter to exit"
