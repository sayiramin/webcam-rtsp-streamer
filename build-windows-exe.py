#!/usr/bin/env python3
"""
Build Windows executable using PyInstaller
Run this on Windows machine or use GitHub Actions
"""
import os
import subprocess
import sys

def build_executable():
    """Build Windows executable"""
    
    # PyInstaller spec for Windows
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/*.py', 'src'),
        ('config.json', '.'),
        ('mediamtx.yml', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets', 
        'PySide6.QtGui',
        'cv2',
        'numpy'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WebcamRTSPStreamer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    # Write spec file
    with open('windows-build.spec', 'w') as f:
        f.write(spec_content)
    
    print("Building Windows executable...")
    
    # Build with PyInstaller
    result = subprocess.run([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        'windows-build.spec'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Build successful!")
        print("Executable created: dist/WebcamRTSPStreamer.exe")
        print("\nTo distribute:")
        print("1. Copy dist/WebcamRTSPStreamer.exe")
        print("2. Install FFmpeg and MediaMTX on target Windows machine")
        print("3. Run WebcamRTSPStreamer.exe")
    else:
        print("❌ Build failed:")
        print(result.stderr)

if __name__ == "__main__":
    if os.name != 'nt':
        print("This script should be run on Windows for best results")
        print("Or use GitHub Actions for cross-platform builds")
    
    build_executable()
