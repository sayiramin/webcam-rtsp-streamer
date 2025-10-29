# Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        WEBCAM RTSP STREAMER                              │
│                                                                          │
│  ┌────────────┐      ┌──────────────┐      ┌─────────────┐             │
│  │   main.py  │─────▶│   config.py  │◀────▶│ config.json │             │
│  └────────────┘      └──────────────┘      └─────────────┘             │
│        │                     │                                          │
│        │                     │                                          │
│        ▼                     ▼                                          │
│  ┌────────────┐      ┌──────────────┐                                  │
│  │   gui.py   │◀────▶│ streamer.py  │                                  │
│  │ (PySide6)  │      │              │                                  │
│  └────────────┘      └──────────────┘                                  │
│        │                     │                                          │
│        │                     │                                          │
│   [User Input]          [Controls]                                     │
│        │                     │                                          │
└────────┼─────────────────────┼──────────────────────────────────────────┘
         │                     │
         │                     ▼
         │            ┌─────────────────┐
         │            │  MediaMTX RTSP  │◀─────── Auto-started on launch
         │            │     Server      │
         │            │  (Port 8554)    │
         │            └─────────────────┘
         │                     ▲
         │                     │
         │                     │ Publishes stream via RTSP/TCP
         │                     │
         │            ┌─────────────────┐
         │            │     FFmpeg      │
         │            │   Subprocess    │
         │            │                 │
         │            │  ┌───────────┐  │
         │            │  │  H.264    │  │
         │            │  │  Encoder  │  │
         │            │  └───────────┘  │
         │            │       ▲         │
         │            │       │         │
         │            │  ┌───────────┐  │
         │            │  │Watermark  │  │◀─── Optional (text/image/timestamp)
         │            │  │  Filter   │  │
         │            │  └───────────┘  │
         │            │       ▲         │
         │            └───────┼─────────┘
         │                    │
         │                    │ Raw BGR24 frames via stdin pipe
         │                    │
         │            ┌───────────────────┐
         │            │   OpenCV          │
         │            │   VideoCapture    │
         │            │                   │
         │            │  ┌─────────────┐  │
         │            │  │   Camera    │  │
         │            │  │   Index 0   │  │
         │            │  └─────────────┘  │
         │            └───────────────────┘
         │                    ▲
         │                    │
         │            ┌───────────────────┐
         │            │   Webcam Device   │
         │            │   (Hardware)      │
         │            └───────────────────┘
         │
         │
         │            ┌───────────────────────────────────────┐
         │            │         CLIENT CONNECTIONS            │
         │            │                                       │
         │            │  ┌──────────┐  ┌──────────┐          │
         └───────────▶│  │   VLC    │  │  FFplay  │  ...     │
                      │  │  Player  │  │          │          │
                      │  └──────────┘  └──────────┘          │
                      │                                       │
                      │  rtsp://localhost:8554/stream        │
                      └───────────────────────────────────────┘
```

## Data Flow

### 1. Initialization Phase
```
User starts app
    │
    ├─▶ main.py creates Config object
    │       └─▶ Loads/creates config.json
    │
    ├─▶ main.py creates GUI (StreamerMainWindow)
    │       └─▶ Initializes all UI controls
    │
    └─▶ RTSPStreamer starts MediaMTX subprocess
            └─▶ MediaMTX listens on port 8554
```

### 2. Configuration Phase (User Input)
```
User configures settings in GUI
    │
    ├─▶ Selects camera (index 0-9)
    ├─▶ Chooses quality preset (Low/Medium/High)
    │       └─▶ Auto-sets resolution, FPS, bitrate
    ├─▶ Optionally enables watermark
    │       └─▶ Text, Image, or Timestamp
    └─▶ Clicks "Start Streaming"
            └─▶ Config saved to config.json
```

### 3. Streaming Phase
```
┌─────────────────────────────────────────────────────────────┐
│                   Background Thread                         │
│                                                             │
│  1. OpenCV opens webcam (VideoCapture)                     │
│          │                                                  │
│          ▼                                                  │
│  2. Read frame (BGR24, 1280x720@30fps)                     │
│          │                                                  │
│          ▼                                                  │
│  3. Write raw bytes to FFmpeg stdin pipe                   │
│          │                                                  │
│          └──────────────┐                                   │
│                         │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    FFmpeg Process                           │
│                                                             │
│  1. Reads raw BGR24 frames from stdin                      │
│          │                                                  │
│          ▼                                                  │
│  2. [OPTIONAL] Apply watermark filter                      │
│          │                                                  │
│          ▼                                                  │
│  3. Convert to YUV420p (standard format)                   │
│          │                                                  │
│          ▼                                                  │
│  4. Encode as H.264 (libx264, ultrafast/fast)              │
│          │  - Bitrate: 500k-3000k depending on preset      │
│          │  - Tune: zerolatency                            │
│          │                                                  │
│          ▼                                                  │
│  5. Publish to MediaMTX via RTSP/TCP                       │
│          │  - URL: rtsp://localhost:8554/stream            │
│          │                                                  │
└──────────┼─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                   MediaMTX Server                           │
│                                                             │
│  1. Receives RTSP stream from FFmpeg                       │
│          │                                                  │
│          ▼                                                  │
│  2. Serves stream to multiple clients simultaneously       │
│          │  - Protocol: RTSP over TCP                      │
│          │  - Port: 8554                                   │
│          │  - Path: /stream                                │
│          │                                                  │
│          ▼                                                  │
│  3. Clients connect and receive stream                     │
│          │                                                  │
└──────────┴─────────────────────────────────────────────────┘
```

## Component Details

### main.py
- **Role**: Application entry point
- **Responsibilities**: 
  - Initialize Qt application
  - Create Config and GUI instances
  - Start event loop

### gui.py (StreamerMainWindow)
- **Role**: User interface
- **Framework**: PySide6 (Qt6)
- **Responsibilities**:
  - Display controls (resolution, FPS, quality presets)
  - Watermark configuration
  - Start/stop streaming
  - Show status log
  - Disable controls during streaming

### config.py (Config)
- **Role**: Configuration management
- **Responsibilities**:
  - Load/save settings from/to config.json
  - Provide default values
  - Quality presets (Low/Medium/High)
  - Generate RTSP URL

### streamer.py (RTSPStreamer)
- **Role**: Core streaming engine
- **Responsibilities**:
  - Manage MediaMTX subprocess
  - Detect available cameras
  - Open webcam with OpenCV
  - Spawn FFmpeg subprocess
  - Pipe frames to FFmpeg
  - Build watermark filters
  - Handle cleanup

### Threading Model
```
Main Thread (Qt Event Loop)
    │
    ├─▶ GUI updates and user interactions
    │
    └─▶ Spawns Background Thread
            │
            └─▶ Stream Loop
                    │
                    ├─▶ Read frames from OpenCV (blocking)
                    ├─▶ Write to FFmpeg stdin
                    └─▶ Update FPS stats every 5 seconds
```

## Network Quality Presets

| Preset | Resolution | FPS | Bitrate | Use Case |
|--------|-----------|-----|---------|----------|
| **Low** | 640x360 | 15 | 800k | 450 MHz networks, up to 5 Mbps |
| **Medium** | 1280x720 | 25 | 1500k | 4G networks, normal WiFi |
| **High** | 1920x1080 | 30 | 3000k | 5G, fast WiFi, wired connections |

## Watermark Types

### Text Watermark
```
FFmpeg filter: drawtext
    ├─▶ Custom text
    ├─▶ White text with semi-transparent black box
    ├─▶ Positioned using tw/th (text width/height)
    └─▶ 5 positions: top-left, top-right, bottom-left, bottom-right, center
```

### Timestamp Watermark
```
FFmpeg filter: drawtext with localtime expansion
    ├─▶ Custom text + live timestamp (updates every second)
    ├─▶ Format: "Camera Stream 2025-10-29 19:22:10"
    └─▶ Same positioning as text watermark
```

### Image Watermark
```
FFmpeg filter: movie + scale + overlay
    ├─▶ Load PNG/JPG image
    ├─▶ Scale to 10% of video width (maintains aspect ratio)
    ├─▶ Positioned using W/H (video) and w/h (overlay)
    └─▶ Supports transparency (PNG alpha channel)
```

## Port and Protocol Information

- **MediaMTX RTSP Server**: TCP port 8554 (configurable)
- **RTSP URL**: `rtsp://localhost:8554/stream`
- **Protocol**: RTSP over TCP (reliable, firewall-friendly)
- **Video Codec**: H.264 (libx264)
- **Pixel Format**: YUV420p (standard, compatible with all players)

## Platform Compatibility

| Platform | Camera Backend | FFmpeg | MediaMTX |
|----------|---------------|--------|----------|
| macOS | AVFoundation | ✅ | ✅ |
| Windows | DirectShow | ✅ | ✅ |
| Linux | V4L2 | ✅ | ✅ |

## Process Lifecycle

```
App Start
    │
    ├─▶ MediaMTX starts (subprocess)
    │
User clicks "Start Streaming"
    │
    ├─▶ OpenCV opens webcam
    ├─▶ FFmpeg spawns (subprocess)
    ├─▶ Background thread starts
    │       └─▶ Continuously reads and pipes frames
    │
User clicks "Stop Streaming"
    │
    ├─▶ is_streaming = False (stops loop)
    ├─▶ FFmpeg process terminates
    └─▶ OpenCV releases camera
    │
App Close
    │
    └─▶ MediaMTX process terminates
```
