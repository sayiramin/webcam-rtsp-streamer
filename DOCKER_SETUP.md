# Docker Setup Guide

## Why Docker?
- **No MediaMTX installation issues**: Everything is pre-installed in the container
- **Cross-platform compatibility**: Works identically on Windows, macOS, and Linux
- **Isolated environment**: No conflicts with system dependencies
- **Easy deployment**: One command to run anywhere

## Prerequisites

1. **Install Docker Desktop**:
   - Windows: Download from [docker.com](https://www.docker.com/products/docker-desktop/)
   - macOS: `brew install --cask docker` or download from docker.com
   - Linux: Follow [official Docker installation guide](https://docs.docker.com/engine/install/)

2. **Enable camera access** (platform-specific steps below)

## Quick Start

### 1. Build the Docker image
```bash
docker build -t webcam-streamer .
```

### 2. Run the container

**On Linux/macOS:**
```bash
docker run -p 8554:8554 --device=/dev/video0 webcam-streamer
```

**On Windows (with WSL2):**
```bash
docker run -p 8554:8554 --privileged webcam-streamer
```

### 3. Access the stream
Open VLC or any RTSP client and connect to:
```
rtsp://localhost:8554/stream
```

## Platform-Specific Setup

### Windows Setup

1. **Enable WSL2** (required for Docker Desktop):
   ```powershell
   wsl --install
   ```

2. **Install Docker Desktop** and enable WSL2 integration

3. **Camera access in WSL2**:
   - Install USB/IP tools in WSL2:
   ```bash
   sudo apt update
   sudo apt install linux-tools-virtual hwdata
   sudo update-alternatives --install /usr/local/bin/usbip usbip `ls /usr/lib/linux-tools/*/usbip | tail -n1` 20
   ```

4. **Run with camera access**:
   ```bash
   docker run -p 8554:8554 --privileged -v /dev:/dev webcam-streamer
   ```

### macOS Setup

1. **Install Docker Desktop**:
   ```bash
   brew install --cask docker
   ```

2. **Grant camera permissions** to Docker Desktop in System Preferences

3. **Run with camera device**:
   ```bash
   docker run -p 8554:8554 --device=/dev/video0 webcam-streamer
   ```

### Linux Setup

1. **Add user to docker group**:
   ```bash
   sudo usermod -aG docker $USER
   ```

2. **Run with camera device**:
   ```bash
   docker run -p 8554:8554 --device=/dev/video0 webcam-streamer
   ```

## Using Docker Compose (Recommended)

### 1. Start the service
```bash
docker-compose up -d
```

### 2. View logs
```bash
docker-compose logs -f
```

### 3. Stop the service
```bash
docker-compose down
```

## Configuration

### Modify settings
Edit `config.json` before building, or mount it as a volume:
```bash
docker run -p 8554:8554 --device=/dev/video0 -v $(pwd)/config.json:/app/config.json webcam-streamer
```

### Environment variables
```bash
docker run -p 8554:8554 --device=/dev/video0 -e CAMERA_INDEX=1 webcam-streamer
```

## Troubleshooting

### Camera not detected
- **Linux**: Check `ls /dev/video*` and use correct device
- **Windows**: Ensure WSL2 is properly configured
- **macOS**: Grant camera permissions to Docker Desktop

### Port already in use
```bash
# Use different port
docker run -p 8555:8554 --device=/dev/video0 webcam-streamer
# Then connect to rtsp://localhost:8555/stream
```

### Container won't start
```bash
# Check logs
docker logs <container-id>

# Run interactively for debugging
docker run -it --device=/dev/video0 webcam-streamer /bin/bash
```

## Benefits of Docker Approach

1. **Consistent Environment**: Same behavior across all platforms
2. **No Dependency Hell**: FFmpeg and MediaMTX pre-installed
3. **Easy Scaling**: Run multiple instances on different ports
4. **Simple Deployment**: One command deployment anywhere
5. **Version Control**: Tag and version your streaming setup
6. **Resource Isolation**: Contained resource usage

## Advanced Usage

### Multiple cameras
```bash
# Camera 1 on port 8554
docker run -d -p 8554:8554 --device=/dev/video0 --name cam1 webcam-streamer

# Camera 2 on port 8555  
docker run -d -p 8555:8554 --device=/dev/video1 --name cam2 webcam-streamer
```

### Custom configuration per container
```bash
# Create custom config
cp config.json config-hd.json
# Edit config-hd.json for HD settings

# Run with custom config
docker run -p 8554:8554 --device=/dev/video0 -v $(pwd)/config-hd.json:/app/config.json webcam-streamer
```
