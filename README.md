# Webcam RTSP Streamer

Convert your laptop webcam into an RTSP streaming server with a simple, user-friendly GUI application.

## How It Works

```
┌─────────────┐
│   Webcam    │  Your laptop camera
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   OpenCV    │  Captures raw video frames
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   FFmpeg    │  Encodes to H.264 + optional watermark
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  MediaMTX   │  RTSP server (handles multiple clients)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  VLC, FFplay, or any RTSP   │  Watch from anywhere
│  compatible player/device   │  rtsp://localhost:8554/stream
└─────────────────────────────┘
```

**Full architecture details**: [docs/architecture.md](docs/architecture.md)

## Features

- 🎥 Stream webcam video over RTSP protocol
- 🖥️ Cross-platform: Works on Windows, macOS, and Linux
- ⚙️ Configurable resolution, FPS, and streaming parameters
- 🎛️ Easy-to-use graphical interface with tabbed layout
- 📹 Multiple camera support with auto-detection
- 💾 Persistent configuration settings
- 🔧 Low-latency streaming optimized for real-time applications
- 🎨 Watermark support (text, image, timestamp)

## 🚀 Quick Start

### Windows (Portable - No Installation Required)
1. **Download**: Clone or download this repository
2. **Build**: Run `python build-portable-windows.py`
3. **Extract**: Extract `WebcamStreamer-Portable-Windows.zip`
4. **Run**: Double-click `run.bat`
5. **Stream**: Connect to `rtsp://localhost:8554/stream`

### macOS/Linux (Native Installation)
```bash
# Install dependencies
brew install ffmpeg mediamtx  # macOS
# sudo apt install ffmpeg && install MediaMTX manually  # Linux

# Clone and setup
git clone https://github.com/sayiramin/webcam-rtsp-streamer.git
cd webcam-rtsp-streamer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python src/main.py
```

## Requirements

### System Requirements
- Python 3.11 or higher
- FFmpeg (must be installed and available in system PATH)
- MediaMTX (RTSP server - automatically managed by the app)
- Webcam/camera device

### Python Dependencies
- PySide6 >= 6.7.0
- opencv-python >= 4.10.0
- numpy >= 1.26.0
- pyinstaller >= 6.9.0 (for building executables)

## Installation & Setup

### Windows Setup (Portable Package)

**No installation required! Everything is bundled.**

1. **Clone the repository**:
   ```cmd
   git clone https://github.com/sayiramin/webcam-rtsp-streamer.git
   cd webcam-rtsp-streamer
   ```

2. **Build portable package**:
   ```cmd
   python build-portable-windows.py
   ```

3. **Extract and run**:
   - Extract `WebcamStreamer-Portable-Windows.zip`
   - Double-click `run.bat`
   - Everything is included: MediaMTX, FFmpeg, Python dependencies

**Requirements**: Only Python 3.11+ (the script handles everything else)

### macOS Setup

1. **Install dependencies**:
   ```bash
   brew install ffmpeg mediamtx
   ```

2. **Clone and setup**:
   ```bash
   git clone https://github.com/sayiramin/webcam-rtsp-streamer.git
   cd webcam-rtsp-streamer
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Grant camera permissions**:
   - System Preferences → Privacy & Security → Camera → Terminal ✓

4. **Run**:
   ```bash
   python src/main.py
   ```

### Linux Setup (Ubuntu/Debian)

1. **Install system dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv ffmpeg
   ```

2. **Install MediaMTX**:
   ```bash
   wget https://github.com/bluenviron/mediamtx/releases/download/v1.15.3/mediamtx_v1.15.3_linux_amd64.tar.gz
   tar -xzf mediamtx_v1.15.3_linux_amd64.tar.gz
   sudo mv mediamtx /usr/local/bin/
   sudo chmod +x /usr/local/bin/mediamtx
   ```

3. **Clone and setup**:
   ```bash
   git clone https://github.com/sayiramin/webcam-rtsp-streamer.git
   cd webcam-rtsp-streamer
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Run**:
   ```bash
   python src/main.py
   ```

## Usage

### Running from Source

```bash
cd src
python main.py
```

Or from the project root:
```bash
python src/main.py
```

### Using the Application

1. **Select Camera**: Choose your webcam from the dropdown (click "Refresh" to detect cameras)
2. **Configure Stream**: Set resolution, FPS, RTSP port, and path
3. **Start Streaming**: Click "Start Streaming" button
4. **Copy URL**: Use the "Copy URL" button to copy the RTSP URL
5. **Connect Client**: Use any RTSP client (VLC, FFplay, etc.) to view the stream

### Connecting to the Stream

Once streaming is active, connect using:
```
rtsp://localhost:8554/stream
```

#### Using VLC Media Player
1. Open VLC
2. Go to Media → Open Network Stream
3. Enter the RTSP URL: `rtsp://localhost:8554/stream`
4. Click Play

#### Using FFplay (Command Line)
```bash
ffplay rtsp://localhost:8554/stream
```

#### Accessing from Another Device
Replace `localhost` with the IP address of the machine running the streamer:
```
rtsp://192.168.1.100:8554/stream
```

## Configuration

Configuration is automatically saved to `config.json` in the working directory.

### Default Settings
```json
{
    "rtsp_port": 8554,
    "rtsp_path": "stream",
    "video_width": 1280,
    "video_height": 720,
    "video_fps": 30,
    "camera_index": 0,
    "video_codec": "libx264",
    "video_bitrate": "2M",
    "preset": "ultrafast",
    "tune": "zerolatency"
}
```

## Building Executables

### For Windows (on Windows machine)
```bash
pyinstaller build.spec
```

The executable will be created in the `dist/` directory.

### For macOS (on Mac)
```bash
pyinstaller build.spec
```

This creates a `.app` bundle in the `dist/` directory.

### Cross-platform Notes
- Build the Windows executable on a Windows machine
- Build the macOS app on a Mac
- Linux executables can be built on Linux systems

## Troubleshooting

### FFmpeg Not Found
**Error**: "FFmpeg not found. Please install FFmpeg and add it to PATH."

**Solution**: 
- Verify FFmpeg is installed: `ffmpeg -version`
- Ensure FFmpeg is in your system PATH
- Restart the application after installing FFmpeg

### Camera Not Detected
**Error**: "No cameras detected"

**Solution**:
- Check camera permissions (especially on macOS)
- Ensure camera is not being used by another application
- Try clicking "Refresh" button
- Check system settings to enable camera access

### MediaMTX Not Found
**Error**: "Warning: MediaMTX not found. Install with: brew install mediamtx"

**Solution**:
- Install MediaMTX using the platform-specific instructions above
- Verify MediaMTX is installed: `mediamtx --version`
- Ensure MediaMTX is in your system PATH
- Restart the application after installing MediaMTX

### Streaming Fails to Start
**Possible causes**:
- Port already in use (try changing RTSP port)
- Camera access denied
- MediaMTX not running (app should auto-start it)
- FFmpeg configuration issues
- Firewall blocking the port

### Low FPS or Laggy Stream
**Solutions**:
- Reduce resolution
- Lower FPS setting
- Ensure sufficient system resources
- Check network bandwidth (for remote viewing)

### Cannot Connect from Another Device
**Solutions**:
- Check firewall settings (allow port 8554)
- Use correct IP address (not localhost)
- Ensure devices are on same network
- Try `rtsp://` protocol explicitly in client

## Technical Details

### Architecture
- **Frontend**: PySide6 (Qt6) for cross-platform GUI
- **Video Capture**: OpenCV for webcam access
- **Video Encoding**: FFmpeg subprocess for H.264 encoding
- **RTSP Server**: MediaMTX for serving RTSP streams
- **Threading**: Non-blocking streaming in background thread

### How It Works
1. Application automatically starts MediaMTX RTSP server on launch
2. OpenCV captures raw frames from webcam
3. Frames are piped to FFmpeg for H.264 encoding
4. FFmpeg publishes encoded stream to MediaMTX via RTSP
5. MediaMTX serves the stream to multiple clients simultaneously
6. Clients connect to `rtsp://localhost:8554/stream` to view

### Network Protocol
- Protocol: RTSP (Real-Time Streaming Protocol)
- Transport: TCP
- Video Codec: H.264 (configurable)
- Container: RTSP

## License

MIT License - Feel free to use, modify, and distribute.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For issues, questions, or feature requests:
- Open an issue on the GitHub repository
- Email: sayir.amin@gmail.com
