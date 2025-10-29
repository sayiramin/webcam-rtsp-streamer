"""
Configuration management for Webcam RTSP Streamer
"""
import json
import os
from pathlib import Path
from typing import Any, Dict


class Config:
    """Application configuration manager"""
    
    DEFAULT_CONFIG = {
        "rtsp_port": 8554,
        "rtsp_path": "stream",
        "video_width": 1280,
        "video_height": 720,
        "video_fps": 30,
        "camera_index": 0,
        "video_codec": "libx264",
        "video_bitrate": "2M",
        "preset": "ultrafast",
        "tune": "zerolatency",
        # Network quality preset
        "quality_preset": "medium",  # low, medium, high
        # Watermark settings
        "watermark_enabled": False,
        "watermark_type": "text",  # text, image, timestamp
        "watermark_text": "Camera Stream",
        "watermark_image_path": "",
        "watermark_position": "top-right",  # top-left, top-right, bottom-left, bottom-right, center
    }
    
    # Quality presets optimized for different network conditions
    QUALITY_PRESETS = {
        "low": {
            "name": "Low (450 MHz / Up to 5 Mbps)",
            "width": 640,
            "height": 360,
            "fps": 20,
            "bitrate": "800k",
            "preset": "ultrafast",
        },
        "medium": {
            "name": "Medium (4G / Normal Network)",
            "width": 1280,
            "height": 720,
            "fps": 25,
            "bitrate": "1500k",
            "preset": "ultrafast",
        },
        "high": {
            "name": "High (5G / Fast Network)",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "bitrate": "3000k",
            "preset": "fast",
        },
    }
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded_config)
                    return config
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def get_rtsp_url(self) -> str:
        """Generate RTSP URL based on current configuration"""
        port = self.get("rtsp_port")
        path = self.get("rtsp_path")
        return f"rtsp://localhost:{port}/{path}"
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self.config = self.DEFAULT_CONFIG.copy()
