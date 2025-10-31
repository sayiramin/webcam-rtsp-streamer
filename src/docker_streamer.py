"""
Docker-optimized version of the streamer
"""
import os
import subprocess
from streamer import RTSPStreamer


class DockerRTSPStreamer(RTSPStreamer):
    """Docker-optimized RTSP streamer"""
    
    def _start_mediamtx(self):
        """MediaMTX is already running in Docker, just check if it's available"""
        try:
            # In Docker, MediaMTX should already be running
            # Just verify it's accessible
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8554))
            sock.close()
            
            if result == 0:
                self._log_status("MediaMTX server is running")
                return True
            else:
                # Start MediaMTX if not running
                self.mediamtx_process = subprocess.Popen(
                    ['mediamtx', '/app/mediamtx.yml'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                import time
                time.sleep(2)
                self._log_status("Started MediaMTX server")
                return True
                
        except Exception as e:
            self._log_status(f"MediaMTX check failed: {e}")
            return False
    
    def get_available_cameras(self):
        """Get available cameras in Docker environment"""
        cameras = []
        
        # Check for video devices
        for i in range(10):  # Check first 10 possible cameras
            device_path = f"/dev/video{i}"
            if os.path.exists(device_path):
                try:
                    import cv2
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        cameras.append(f"Camera {i}")
                        cap.release()
                except:
                    pass
        
        return cameras if cameras else ["Camera 0"]  # Default fallback
