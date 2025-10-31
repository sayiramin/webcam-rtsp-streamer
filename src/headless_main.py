#!/usr/bin/env python3
"""
Headless version for Docker deployment
"""
import time
import signal
import sys
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
        
    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("Starting headless webcam streamer...")
        
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
