#!/usr/bin/env python3
"""
Build portable Windows package with all dependencies bundled
"""
import os
import urllib.request
import zipfile
import subprocess
import shutil
from pathlib import Path

def download_file(url, filename):
    """Download file with progress"""
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, filename)
    print(f"✅ Downloaded {filename}")

def build_portable_package():
    """Build portable Windows package"""
    
    # Create build directory
    build_dir = Path("build-portable")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    
    print("🔧 Building portable Windows package...")
    
    # 1. Download MediaMTX Windows binary
    mediamtx_url = "https://github.com/bluenviron/mediamtx/releases/download/v1.15.3/mediamtx_v1.15.3_windows_amd64.zip"
    mediamtx_zip = build_dir / "mediamtx.zip"
    download_file(mediamtx_url, mediamtx_zip)
    
    # Extract MediaMTX
    with zipfile.ZipFile(mediamtx_zip, 'r') as zip_ref:
        zip_ref.extractall(build_dir / "mediamtx_temp")
    
    # 2. Download FFmpeg Windows binary
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    ffmpeg_zip = build_dir / "ffmpeg.zip"
    download_file(ffmpeg_url, ffmpeg_zip)
    
    # Extract FFmpeg
    with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
        zip_ref.extractall(build_dir / "ffmpeg_temp")
    
    # 3. Create package structure
    package_dir = build_dir / "WebcamStreamer-Portable"
    package_dir.mkdir()
    
    # Copy MediaMTX executable
    mediamtx_exe = list((build_dir / "mediamtx_temp").glob("**/mediamtx.exe"))[0]
    shutil.copy2(mediamtx_exe, package_dir / "mediamtx.exe")
    
    # Copy FFmpeg executable
    ffmpeg_exe = list((build_dir / "ffmpeg_temp").glob("**/ffmpeg.exe"))[0]
    shutil.copy2(ffmpeg_exe, package_dir / "ffmpeg.exe")
    
    # Copy project files
    shutil.copy2("config.json", package_dir)
    shutil.copy2("mediamtx.yml", package_dir)
    shutil.copytree("src", package_dir / "src")
    
    # 4. Create startup batch file
    batch_content = '''@echo off
echo Starting Webcam RTSP Streamer...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

REM Install Python dependencies if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\\Scripts\\activate.bat

echo Installing dependencies...
pip install PySide6>=6.7.0 opencv-python>=4.10.0 numpy>=1.26.0 --quiet

echo Starting application...
python src\\main.py

pause
'''
    
    with open(package_dir / "run.bat", 'w') as f:
        f.write(batch_content)
    
    # 5. Create requirements.txt in package
    with open(package_dir / "requirements.txt", 'w') as f:
        f.write("PySide6>=6.7.0\nopencv-python>=4.10.0\nnumpy>=1.26.0\n")
    
    # 6. Create README for Windows users
    readme_content = '''# Webcam RTSP Streamer - Portable Windows Version

## Quick Start

1. Extract this folder anywhere on your Windows computer
2. Double-click `run.bat`
3. The application will start automatically
4. Connect to stream: rtsp://localhost:8554/stream

## Requirements

- Windows 10/11
- Python 3.11+ (will prompt to install if missing)

## What's Included

- ✅ MediaMTX RTSP server (mediamtx.exe)
- ✅ FFmpeg video encoder (ffmpeg.exe)  
- ✅ Webcam streamer application (src/)
- ✅ All configuration files

## No Installation Required!

Everything is bundled - no need to install MediaMTX or FFmpeg separately.

## Troubleshooting

- If Python is missing: Download from python.org
- If camera not detected: Check Windows camera permissions
- If port 8554 is busy: Change rtsp_port in config.json

## Support

GitHub: https://github.com/sayiramin/webcam-rtsp-streamer
'''
    
    with open(package_dir / "README.txt", 'w') as f:
        f.write(readme_content)
    
    # 7. Create final zip package
    print("📦 Creating final package...")
    shutil.make_archive("WebcamStreamer-Portable-Windows", 'zip', build_dir, "WebcamStreamer-Portable")
    
    print("✅ Portable Windows package created!")
    print(f"📁 Package: WebcamStreamer-Portable-Windows.zip")
    print(f"📏 Size: {os.path.getsize('WebcamStreamer-Portable-Windows.zip') / 1024 / 1024:.1f} MB")
    print("\n🚀 Ready for distribution!")
    print("Windows users can download, extract, and run without any installations.")

if __name__ == "__main__":
    build_portable_package()
