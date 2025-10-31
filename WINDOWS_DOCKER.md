# Windows Docker Setup

## Camera Access Challenges on Windows

Docker Desktop on Windows uses WSL2, which doesn't have direct camera access. Here are your options:

## Option 1: Run Natively (Recommended for Windows)

**Skip Docker on Windows and run natively:**
```powershell
# Install dependencies
choco install python ffmpeg mediamtx

# Clone and run
git clone https://github.com/sayiramin/webcam-rtsp-streamer.git
cd webcam-rtsp-streamer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

## Option 2: USB Passthrough (Advanced)

**1. Enable USB/IP in WSL2:**
```bash
# In WSL2 terminal
sudo apt update
sudo apt install linux-tools-virtual hwdata
sudo update-alternatives --install /usr/local/bin/usbip usbip `ls /usr/lib/linux-tools/*/usbip | tail -n1` 20
```

**2. Install USB/IP on Windows:**
- Download usbipd-win from GitHub releases
- Install and restart

**3. Connect camera to WSL2:**
```powershell
# In PowerShell as Administrator
usbipd wsl list
usbipd wsl attach --busid <BUSID> --distribution <WSL_DISTRO>
```

**4. Run Docker:**
```bash
docker run -p 8554:8554 --privileged --device=/dev/video0 webcam-streamer
```

## Option 3: Windows Containers (Alternative)

Use Windows containers instead of Linux containers (requires Windows Server base images).

## Recommendation

**For Windows users: Use native installation instead of Docker** to avoid camera access complexity. Docker is most beneficial on Linux/macOS where camera access is straightforward.
