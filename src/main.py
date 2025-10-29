#!/usr/bin/env python3
"""
Webcam RTSP Streamer - Main Entry Point
Converts laptop webcam into RTSP streaming server
"""
import sys
from PySide6.QtWidgets import QApplication
from config import Config
from gui import StreamerMainWindow


def main():
    """Main application entry point"""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Webcam RTSP Streamer")
    app.setOrganizationName("WebcamStreamer")
    
    # Load configuration
    config = Config()
    
    # Create and show main window
    window = StreamerMainWindow(config)
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
