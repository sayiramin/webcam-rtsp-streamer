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
- MediaMTX (RTSP server - automatically managed by the app)
- Webcam/camera device

### Python Dependencies
- PySide6 >= 6.7.0
- opencv-python >= 4.10.0
- numpy >= 1.26.0
- pyinstaller >= 6.9.0 (for building executables)

## Installation

### macOS Setup

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install FFmpeg and MediaMTX**:
   ```bash
   brew install ffmpeg mediamtx
   ```

3. **Clone the repository**:
   ```bash
   git clone https://github.com/sayiramin/webcam-rtsp-streamer.git
   cd webcam-rtsp-streamer
   ```

4. **Set up Python virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```bash
   python src/main.py
   ```

6. **Grant camera permissions** when prompted by macOS (System Preferences → Privacy & Security → Camera)

### Windows Setup

1. **Install Python 3.11+** from [python.org](https://www.python.org/downloads/)

2. **Install Chocolatey** (package manager) - Open PowerShell as Administrator:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

3. **Install FFmpeg and MediaMTX**:
   ```powershell
   choco install ffmpeg
   choco install mediamtx
   ```

   *Alternatively, download manually:*
   - FFmpeg: [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - MediaMTX: [github.com/bluenviron/mediamtx/releases](https://github.com/bluenviron/mediamtx/releases)
   - Add both to your system PATH

4. **Clone the repository**:
   ```bash
   git clone https://github.com/sayiramin/webcam-rtsp-streamer.git
   cd webcam-rtsp-streamer
   ```

5. **Set up Python virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

6. **Run the application**:
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
   # Download latest release
   wget https://github.com/bluenviron/mediamtx/releases/download/v1.15.3/mediamtx_v1.15.3_linux_amd64.tar.gz
   tar -xzf mediamtx_v1.15.3_linux_amd64.tar.gz
   sudo mv mediamtx /usr/local/bin/
   sudo chmod +x /usr/local/bin/mediamtx
   ```

3. **Clone the repository**:
   ```bash
   git clone https://github.com/sayiramin/webcam-rtsp-streamer.git
   cd webcam-rtsp-streamer
   ```

4. **Set up Python virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Run the application**:
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
