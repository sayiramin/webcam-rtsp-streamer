# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Webcam RTSP Streamer is a cross-platform desktop application that converts laptop webcams into RTSP streaming servers. The application uses:
- **PySide6 (Qt6)** for the GUI
- **OpenCV** for webcam capture
- **FFmpeg** (subprocess) for RTSP server and H.264 encoding
- **Threading** for non-blocking streaming

## Common Commands

### Running the Application
```bash
# From project root
python src/main.py

# Or from src directory
cd src && python main.py
```

### Installing Dependencies
```bash
# Virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Building Executables
```bash
# Build platform-specific executable
pyinstaller build.spec

# Output will be in dist/ directory
# - Windows: dist/WebcamRTSPStreamer.exe
# - macOS: dist/WebcamRTSPStreamer.app
```

### Testing Stream
```bash
# After starting the app, test with FFplay
ffplay rtsp://localhost:8554/stream

# Or with VLC (GUI): Media → Open Network Stream
```

## Architecture

### Core Components

1. **main.py** - Entry point that initializes Qt application and Config
2. **config.py** - Configuration manager with JSON persistence (config.json)
3. **streamer.py** - Core streaming engine with RTSPStreamer class
4. **gui.py** - PySide6-based GUI with StreamerMainWindow

### Data Flow

```
GUI (gui.py)
  ↓ user input
Config (config.py) ← saves/loads config.json
  ↓ settings
RTSPStreamer (streamer.py)
  ↓ camera index
OpenCV VideoCapture
  ↓ raw frames (BGR24)
FFmpeg subprocess (stdin pipe)
  ↓ H.264 encoding
RTSP Server (rtsp://localhost:8554/stream)
```

### Threading Model

- **Main thread**: Qt event loop (GUI)
- **Background thread**: `_stream_loop()` continuously reads frames from OpenCV and pipes to FFmpeg stdin
- Thread is daemon and joins on stop with 2s timeout

### FFmpeg Integration

The application spawns FFmpeg as a subprocess:
- Reads raw BGR24 frames from stdin (pipe:0)
- Encodes as H.264 with ultrafast preset and zerolatency tune
- Serves RTSP stream on configurable port (default 8554)
- On Windows, hides console window via STARTUPINFO flags

### Configuration Persistence

All settings are saved to `config.json` in working directory with defaults:
- Camera: index 0
- Resolution: 1280x720
- FPS: 30
- RTSP port: 8554, path: "stream"
- Codec: libx264, bitrate: 2M, preset: ultrafast, tune: zerolatency

## Development Guidelines

### External Dependencies
- **FFmpeg must be installed** and in system PATH - the app will fail gracefully with clear error if missing
- Check FFmpeg with: `ffmpeg -version`

### Camera Access
- macOS requires camera permissions in System Preferences
- Camera detection iterates indices 0-9 via OpenCV VideoCapture
- Actual resolution may differ from requested if camera doesn't support it

### Platform-Specific Code
- Windows: subprocess.STARTUPINFO to hide FFmpeg console window
- Build executables on target platform (no cross-compilation)

### Error Handling
- Status messages go through callback (status_callback) to GUI
- FFmpeg stderr is captured if process fails to start
- Stream loop breaks on frame read failure or pipe write error

### State Management
- `is_streaming` flag controls stream loop
- GUI disables/enables controls based on streaming state
- Config is saved before each stream start

### GUI Threading
- Never call OpenCV/FFmpeg operations from Qt main thread
- Use daemon threads for streaming operations
- Status updates via callback are thread-safe with Qt signals

## Code Patterns

### Adding New Configuration Options
1. Add default value to `Config.DEFAULT_CONFIG` in config.py
2. Add UI control in `gui.py` `init_ui()` method
3. Read value in `start_streaming()` and set to config
4. Use value in `streamer.py` where needed

### Extending Stream Settings
When modifying FFmpeg command in `_start_ffmpeg()`:
- Maintain stdin pipe mode (`-i pipe:0`)
- Keep RTSP transport as TCP for reliability
- Test that FFmpeg process doesn't terminate immediately after start
- Consider platform differences (especially Windows)

### Camera Selection
Camera indices are discovered by attempting to open VideoCapture(0-9). If adding backend-specific selection:
- macOS: consider AVFoundation backend
- Linux: consider V4L2 backend
- Windows: DirectShow is default
