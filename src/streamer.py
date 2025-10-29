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
        self.mediamtx_process = None
        
    def _log_status(self, message: str):
        """Log status message via callback if available"""
        if self.status_callback:
            self.status_callback(message)
        print(message)
    
    def _start_mediamtx(self):
        """Start MediaMTX RTSP server as subprocess"""
        try:
            # Check if MediaMTX is installed
            mediamtx_path = subprocess.check_output(['which', 'mediamtx'], text=True).strip()
            
            # Get config file path
            import os
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mediamtx.yml')
            
            # Start MediaMTX with config file
            startupinfo = None
            if platform.system() == 'Windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.mediamtx_process = subprocess.Popen(
                [mediamtx_path, config_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo
            )
            
            # Give MediaMTX time to start
            time.sleep(2)
            
            if self.mediamtx_process.poll() is not None:
                self._log_status("Warning: MediaMTX failed to start")
                self.mediamtx_process = None
            else:
                self._log_status("MediaMTX RTSP server started")
                
        except FileNotFoundError:
            self._log_status("Warning: MediaMTX not found. Install with: brew install mediamtx")
            self.mediamtx_process = None
        except Exception as e:
            self._log_status(f"Warning: Could not start MediaMTX: {e}")
            self.mediamtx_process = None
    
    def get_available_cameras(self) -> list:
        """Detect available camera devices"""
        import os
        # Suppress OpenCV warnings during camera detection
        os.environ['OPENCV_LOG_LEVEL'] = 'FATAL'
        
        cameras = []
        # Test up to 10 camera indices
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append(i)
                cap.release()
        
        # Restore normal logging
        os.environ['OPENCV_LOG_LEVEL'] = 'INFO'
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
        """Start FFmpeg process to publish to MediaMTX RTSP server"""
        try:
            port = self.config.get("rtsp_port", 8554)
            path = self.config.get("rtsp_path", "stream")
            codec = self.config.get("video_codec", "libx264")
            bitrate = self.config.get("video_bitrate", "2M")
            preset = self.config.get("preset", "ultrafast")
            tune = self.config.get("tune", "zerolatency")
            
            # Build FFmpeg command with optional watermark
            ffmpeg_cmd = [
                'ffmpeg',
                '-f', 'rawvideo',
                '-pixel_format', 'bgr24',
                '-video_size', f'{width}x{height}',
                '-framerate', str(fps),
                '-i', 'pipe:0',  # Read from stdin
            ]
            
            # Add watermark filter if enabled
            watermark_enabled = self.config.get("watermark_enabled", False)
            if watermark_enabled:
                filter_str = self._build_watermark_filter(width, height)
                if filter_str:
                    ffmpeg_cmd.extend(['-vf', filter_str])
            
            # Continue with encoding settings
            ffmpeg_cmd.extend([
                '-pix_fmt', 'yuv420p',  # Convert to standard YUV420p format
                '-c:v', codec,
                '-preset', preset,
                '-tune', tune,
                '-b:v', bitrate,
                '-an',  # No audio
                '-f', 'rtsp',
                '-rtsp_transport', 'tcp',
                '-muxdelay', '0.1',
                f'rtsp://localhost:{port}/{path}'
            ])
            
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
            
            self._log_status("FFmpeg publisher started (requires MediaMTX running)")
            
            # Start thread to monitor FFmpeg stderr (only log errors/warnings)
            def monitor_ffmpeg():
                if self.ffmpeg_process and self.ffmpeg_process.stderr:
                    for line in self.ffmpeg_process.stderr:
                        if line:
                            line_str = line.decode().strip()
                            # Only log errors and warnings, not info
                            if any(x in line_str.lower() for x in ['error', 'warning', 'failed']):
                                self._log_status(f"FFmpeg: {line_str}")
            
            threading.Thread(target=monitor_ffmpeg, daemon=True).start()
            return True
            
        except FileNotFoundError:
            self._log_status("FFmpeg not found. Please install FFmpeg and add it to PATH.")
            return False
        except Exception as e:
            self._log_status(f"Error starting FFmpeg: {e}")
            return False
    
    def _build_watermark_filter(self, width: int, height: int) -> str:
        """Build FFmpeg filter string for watermark"""
        wm_type = self.config.get("watermark_type", "text")
        wm_position = self.config.get("watermark_position", "top-right")
        
        # Calculate position coordinates
        positions = {
            "top-left": "10:10",
            "top-right": f"{width}-tw-10:10",
            "bottom-left": f"10:{height}-th-10",
            "bottom-right": f"{width}-tw-10:{height}-th-10",
            "center": f"({width}-tw)/2:({height}-th)/2"
        }
        pos = positions.get(wm_position, positions["top-right"])
        
        if wm_type == "text":
            text = self.config.get("watermark_text", "Camera Stream")
            # Escape special characters for FFmpeg
            text = text.replace(":", "\\:").replace("'", "'").replace("[", "\\[").replace("]", "\\]")
            return f"drawtext=text='{text}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x={pos.split(':')[0]}:y={pos.split(':')[1]}"
        
        elif wm_type == "timestamp":
            text = self.config.get("watermark_text", "Camera Stream")
            text = text.replace(":", "\\:").replace("'", "'").replace("[", "\\[").replace("]", "\\]")
            # Add timestamp using FFmpeg's text expansion
            return f"drawtext=text='{text} %{{localtime\\:%Y-%m-%d %H\\\\:%M\\\\:%S}}':fontcolor=white:fontsize=20:box=1:boxcolor=black@0.5:boxborderw=5:x={pos.split(':')[0]}:y={pos.split(':')[1]}"
        
        elif wm_type == "image":
            import os
            image_path = self.config.get("watermark_image_path", "")
            if image_path and os.path.exists(image_path):
                # Escape path for FFmpeg
                image_path = image_path.replace("\\", "/").replace(":", "\\:")
                return f"movie={image_path}[wm];[in][wm]overlay={pos.split(':')[0]}:{pos.split(':')[1]}[out]"
            else:
                self._log_status("Warning: Watermark image not found, skipping watermark")
                return ""
        
        return ""
    
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
        # Don't call stop_streaming from within the stream thread
        # Just set the flag and let cleanup happen from GUI thread
        self.is_streaming = False
    
    def stop_streaming(self):
        """Stop webcam capture and RTSP streaming"""
        if not self.is_streaming:
            return
        
        self.is_streaming = False
        
        # Wait for stream thread to finish (only if called from different thread)
        if self.stream_thread and self.stream_thread.is_alive():
            if threading.current_thread() != self.stream_thread:
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
    
    def cleanup(self):
        """Cleanup all resources including MediaMTX"""
        self.stop_streaming()
        
        # Stop MediaMTX
        if self.mediamtx_process:
            try:
                self.mediamtx_process.terminate()
                self.mediamtx_process.wait(timeout=5)
                self._log_status("MediaMTX stopped")
            except:
                self.mediamtx_process.kill()
            self.mediamtx_process = None
    
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
