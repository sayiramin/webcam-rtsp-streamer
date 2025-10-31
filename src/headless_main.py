#!/usr/bin/env python3
"""
Headless version for Docker deployment
"""
import time
import signal
import sys
import cv2
from config import Config
from streamer import RTSPStreamer


class HeadlessStreamer:
    def __init__(self):
        self.config = Config()
        self.streamer = RTSPStreamer(self.config, self.log_message)
        self.running = True
        
    def log_message(self, message):
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
        
    def signal_handler(self, signum, frame):
        print("\nShutting down...")
        self.running = False
        self.streamer.stop_streaming()
        sys.exit(0)
        
    def find_camera(self):
        """Try to find an available camera"""
        for i in range(10):  # Check first 10 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret and frame is not None:
                    print(f"Found working camera at index {i}")
                    return i
        return None
        
    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("Starting headless webcam streamer...")
        
        # Try to find a working camera
        camera_index = self.find_camera()
        if camera_index is None:
            print("ERROR: No working camera found!")
            print("Make sure:")
            print("1. Camera permissions are granted to Docker Desktop")
            print("2. Camera is not being used by another application")
            print("3. On macOS: System Preferences → Privacy & Security → Camera → Docker Desktop ✓")
            return
            
        # Update config with found camera
        self.config.data["camera_index"] = camera_index
        
        if not self.streamer.start_streaming():
            print("Failed to start streaming")
            return
            
        print(f"Stream available at: {self.config.get_rtsp_url()}")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.signal_handler(None, None)


if __name__ == "__main__":
    streamer = HeadlessStreamer()
    streamer.run()
