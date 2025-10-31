#!/usr/bin/env python3
"""
Docker test streamer using video file instead of camera
"""
import subprocess
import time
import signal
import sys

def signal_handler(signum, frame):
    print("\nShutting down...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Starting MediaMTX...")
    mediamtx_process = subprocess.Popen(
        ['mediamtx', '/app/mediamtx.yml'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    time.sleep(2)
    
    print("Starting FFmpeg stream from test video...")
    ffmpeg_process = subprocess.Popen([
        'ffmpeg',
        '-re',  # Read input at native frame rate
        '-stream_loop', '-1',  # Loop infinitely
        '-i', '/tmp/test_video.mp4',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-f', 'rtsp',
        '-rtsp_transport', 'tcp',
        'rtsp://localhost:8554/stream'
    ])
    
    print("Test stream available at: rtsp://localhost:8554/stream")
    print("This is a test pattern - replace with camera input for real use")
    
    try:
        ffmpeg_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
