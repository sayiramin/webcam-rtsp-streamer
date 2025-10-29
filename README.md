# Webcam RTSP Streamer

Convert your laptop webcam into an RTSP streaming server with a simple, user-friendly GUI application.

## Features

- 🎥 Stream webcam video over RTSP protocol
- 🖥️ Cross-platform: Works on Windows, macOS, and Linux
- ⚙️ Configurable resolution, FPS, and streaming parameters
- 🎛️ Easy-to-use graphical interface
- 📹 Multiple camera support with auto-detection
- 💾 Persistent configuration settings
- 🔧 Low-latency streaming optimized for real-time applications

## Requirements

### System Requirements
- Python 3.11 or higher
- FFmpeg (must be installed and available in system PATH)
- Webcam/camera device

### Python Dependencies
- PySide6 >= 6.7.0
- opencv-python >= 4.10.0
- numpy >= 1.26.0
- pyinstaller >= 6.9.0 (for building executables)

## Installation

### 1. Install FFmpeg

#### macOS (using Homebrew)
```bash
brew install ffmpeg
```

#### Windows
Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) and add it to your system PATH.

Alternatively, using Chocolatey:
```bash
choco install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### 2. Install Python Dependencies

Clone the repository and install dependencies:
```bash
git clone <repository-url>
cd webcam-rtsp-streamer
pip install -r requirements.txt
```

Or using a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
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

### Streaming Fails to Start
**Possible causes**:
- Port already in use (try changing RTSP port)
- Camera access denied
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
- **Streaming**: FFmpeg subprocess for RTSP server
- **Threading**: Non-blocking streaming in background thread

### How It Works
1. Application captures frames from webcam using OpenCV
2. Frames are sent to FFmpeg via stdin pipe
3. FFmpeg encodes video (H.264) and serves via RTSP
4. Clients connect to RTSP URL to view stream

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

For issues, questions, or feature requests, please open an issue on the GitHub repository.
