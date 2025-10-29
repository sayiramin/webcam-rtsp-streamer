"""
Webcam capture and RTSP streaming module
"""
import cv2
import subprocess
import threading
import time
import platform
from typing import Optional, Callable
from config import Config


class RTSPStreamer:
    """Handles webcam capture and RTSP streaming via FFmpeg"""
    
    def __init__(self, config: Config, status_callback: Optional[Callable] = None):
        self.config = config
        self.status_callback = status_callback
        self.is_streaming = False
        self.capture = None
        self.ffmpeg_process = None
        self.stream_thread = None
        
    def _log_status(self, message: str):
        """Log status message via callback if available"""
        if self.status_callback:
            self.status_callback(message)
        print(message)
    
    def get_available_cameras(self) -> list:
        """Detect available camera devices"""
        cameras = []
        # Test up to 10 camera indices
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append(i)
                cap.release()
        return cameras
    
    def start_streaming(self) -> bool:
        """Start webcam capture and RTSP streaming"""
        if self.is_streaming:
            self._log_status("Already streaming")
            return False
        
        try:
            # Open webcam
            camera_index = self.config.get("camera_index", 0)
            self.capture = cv2.VideoCapture(camera_index)
            
            if not self.capture.isOpened():
                self._log_status(f"Failed to open camera {camera_index}")
                return False
            
            # Set camera properties
            width = self.config.get("video_width", 1280)
            height = self.config.get("video_height", 720)
            fps = self.config.get("video_fps", 30)
            
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.capture.set(cv2.CAP_PROP_FPS, fps)
            
            # Get actual resolution (camera may not support requested resolution)
            actual_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.capture.get(cv2.CAP_PROP_FPS))
            
            self._log_status(f"Camera opened: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            # Start FFmpeg RTSP server
            if not self._start_ffmpeg(actual_width, actual_height, actual_fps):
                self.capture.release()
                return False
            
            # Start streaming thread
            self.is_streaming = True
            self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
            self.stream_thread.start()
            
            rtsp_url = self.config.get_rtsp_url()
            self._log_status(f"Streaming started: {rtsp_url}")
            return True
            
        except Exception as e:
            self._log_status(f"Error starting stream: {e}")
            return False
    
    def _start_ffmpeg(self, width: int, height: int, fps: int) -> bool:
        """Start FFmpeg process as RTSP server"""
        try:
            port = self.config.get("rtsp_port", 8554)
            path = self.config.get("rtsp_path", "stream")
            codec = self.config.get("video_codec", "libx264")
            bitrate = self.config.get("video_bitrate", "2M")
            preset = self.config.get("preset", "ultrafast")
            tune = self.config.get("tune", "zerolatency")
            
            # FFmpeg command to read from stdin and output RTSP
            ffmpeg_cmd = [
                'ffmpeg',
                '-f', 'rawvideo',
                '-pixel_format', 'bgr24',
                '-video_size', f'{width}x{height}',
                '-framerate', str(fps),
                '-i', 'pipe:0',  # Read from stdin
                '-c:v', codec,
                '-preset', preset,
                '-tune', tune,
                '-b:v', bitrate,
                '-f', 'rtsp',
                '-rtsp_transport', 'tcp',
                f'rtsp://localhost:{port}/{path}'
            ]
            
            # On Windows, hide console window
            startupinfo = None
            if platform.system() == 'Windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo
            )
            
            # Give FFmpeg time to start
            time.sleep(1)
            
            if self.ffmpeg_process.poll() is not None:
                stderr = self.ffmpeg_process.stderr.read().decode()
                self._log_status(f"FFmpeg failed to start: {stderr}")
                return False
            
            self._log_status("FFmpeg RTSP server started")
            return True
            
        except FileNotFoundError:
            self._log_status("FFmpeg not found. Please install FFmpeg and add it to PATH.")
            return False
        except Exception as e:
            self._log_status(f"Error starting FFmpeg: {e}")
            return False
    
    def _stream_loop(self):
        """Main streaming loop - captures frames and pipes to FFmpeg"""
        frame_count = 0
        start_time = time.time()
        
        while self.is_streaming:
            ret, frame = self.capture.read()
            
            if not ret:
                self._log_status("Failed to read frame from camera")
                break
            
            try:
                # Write frame to FFmpeg stdin
                self.ffmpeg_process.stdin.write(frame.tobytes())
                frame_count += 1
                
                # Log stats every 5 seconds
                if frame_count % (self.config.get("video_fps", 30) * 5) == 0:
                    elapsed = time.time() - start_time
                    actual_fps = frame_count / elapsed
                    self._log_status(f"Streaming: {frame_count} frames, {actual_fps:.1f} fps")
                    
            except Exception as e:
                self._log_status(f"Error writing frame: {e}")
                break
        
        self._log_status("Stream loop ended")
        self.stop_streaming()
    
    def stop_streaming(self):
        """Stop webcam capture and RTSP streaming"""
        if not self.is_streaming:
            return
        
        self.is_streaming = False
        
        # Wait for stream thread to finish
        if self.stream_thread and self.stream_thread.is_alive():
            self.stream_thread.join(timeout=2)
        
        # Close FFmpeg
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.stdin.close()
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=5)
            except:
                self.ffmpeg_process.kill()
            self.ffmpeg_process = None
        
        # Release camera
        if self.capture:
            self.capture.release()
            self.capture = None
        
        self._log_status("Streaming stopped")
    
    def get_preview_frame(self) -> Optional[bytes]:
        """Get current frame as JPEG for preview (optional feature)"""
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                # Resize for preview
                small_frame = cv2.resize(frame, (320, 240))
                ret, jpeg = cv2.imencode('.jpg', small_frame)
                if ret:
                    return jpeg.tobytes()
        return None
