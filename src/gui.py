"""
GUI for Webcam RTSP Streamer using PySide6
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QSpinBox, 
    QTextEdit, QGroupBox, QGridLayout, QLineEdit,
    QMessageBox, QSystemTrayIcon, QMenu
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QIcon, QAction
from config import Config
from streamer import RTSPStreamer


class StreamerMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.streamer = RTSPStreamer(config, self.log_message)
        
        self.setWindowTitle("Webcam RTSP Streamer")
        self.setMinimumSize(600, 500)
        
        self.init_ui()
        self.streamer._start_mediamtx()  # Start MediaMTX after GUI is ready
        self.load_cameras()
        
    def init_ui(self):
        """Initialize user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Camera selection group
        camera_group = QGroupBox("Camera Settings")
        camera_layout = QGridLayout()
        
        camera_layout.addWidget(QLabel("Camera:"), 0, 0)
        self.camera_combo = QComboBox()
        camera_layout.addWidget(self.camera_combo, 0, 1)
        
        self.refresh_cameras_btn = QPushButton("Refresh")
        self.refresh_cameras_btn.clicked.connect(self.load_cameras)
        camera_layout.addWidget(self.refresh_cameras_btn, 0, 2)
        
        camera_group.setLayout(camera_layout)
        main_layout.addWidget(camera_group)
        
        # Stream configuration group
        config_group = QGroupBox("Stream Configuration")
        config_layout = QGridLayout()
        
        config_layout.addWidget(QLabel("Resolution:"), 0, 0)
        resolution_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(320, 3840)
        self.width_spin.setValue(self.config.get("video_width", 1280))
        self.width_spin.setSuffix(" px")
        resolution_layout.addWidget(self.width_spin)
        resolution_layout.addWidget(QLabel("×"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(240, 2160)
        self.height_spin.setValue(self.config.get("video_height", 720))
        self.height_spin.setSuffix(" px")
        resolution_layout.addWidget(self.height_spin)
        config_layout.addLayout(resolution_layout, 0, 1)
        
        config_layout.addWidget(QLabel("FPS:"), 1, 0)
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(5, 60)
        self.fps_spin.setValue(self.config.get("video_fps", 30))
        config_layout.addWidget(self.fps_spin, 1, 1)
        
        config_layout.addWidget(QLabel("RTSP Port:"), 2, 0)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(self.config.get("rtsp_port", 8554))
        config_layout.addWidget(self.port_spin, 2, 1)
        
        config_layout.addWidget(QLabel("RTSP Path:"), 3, 0)
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.config.get("rtsp_path", "stream"))
        config_layout.addWidget(self.path_edit, 3, 1)
        
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        # RTSP URL display
        url_group = QGroupBox("Stream URL")
        url_layout = QVBoxLayout()
        
        self.url_label = QLabel()
        self.url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.url_label.setStyleSheet("QLabel { background-color: #2d2d2d; color: #ffffff; padding: 10px; font-family: monospace; font-size: 14px; border-radius: 4px; }")
        self.update_url_display()
        url_layout.addWidget(self.url_label)
        
        self.copy_url_btn = QPushButton("Copy URL")
        self.copy_url_btn.clicked.connect(self.copy_url)
        url_layout.addWidget(self.copy_url_btn)
        
        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Streaming")
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; }")
        self.start_btn.clicked.connect(self.start_streaming)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Streaming")
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 10px; font-weight: bold; }")
        self.stop_btn.clicked.connect(self.stop_streaming)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(button_layout)
        
        # Status/Log area
        log_group = QGroupBox("Status Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # Support info
        support_label = QLabel('Support: sayir.amin@gmail.com')
        support_label.setStyleSheet("QLabel { color: #666; font-size: 10px; }")
        support_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(support_label)
        
        # Connect value change signals to update URL
        self.port_spin.valueChanged.connect(self.update_url_display)
        self.path_edit.textChanged.connect(self.update_url_display)
        
    def load_cameras(self):
        """Load available cameras into combo box"""
        self.log_message("Detecting cameras...")
        cameras = self.streamer.get_available_cameras()
        
        self.camera_combo.clear()
        if cameras:
            for cam_id in cameras:
                self.camera_combo.addItem(f"Camera {cam_id}", cam_id)
            self.log_message(f"Found {len(cameras)} camera(s)")
        else:
            self.camera_combo.addItem("No cameras found", -1)
            self.log_message("No cameras detected")
    
    def update_url_display(self):
        """Update the RTSP URL display"""
        port = self.port_spin.value()
        path = self.path_edit.text()
        url = f"rtsp://localhost:{port}/{path}"
        self.url_label.setText(url)
    
    def copy_url(self):
        """Copy RTSP URL to clipboard"""
        from PySide6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.url_label.text())
        self.log_message("URL copied to clipboard")
    
    def start_streaming(self):
        """Start streaming"""
        # Update config from UI
        self.config.set("camera_index", self.camera_combo.currentData())
        self.config.set("video_width", self.width_spin.value())
        self.config.set("video_height", self.height_spin.value())
        self.config.set("video_fps", self.fps_spin.value())
        self.config.set("rtsp_port", self.port_spin.value())
        self.config.set("rtsp_path", self.path_edit.text())
        
        # Save config
        self.config.save_config()
        
        # Start streaming
        if self.streamer.start_streaming():
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.camera_combo.setEnabled(False)
            self.refresh_cameras_btn.setEnabled(False)
            self.width_spin.setEnabled(False)
            self.height_spin.setEnabled(False)
            self.fps_spin.setEnabled(False)
            self.port_spin.setEnabled(False)
            self.path_edit.setEnabled(False)
        else:
            QMessageBox.critical(self, "Error", "Failed to start streaming. Check the log for details.")
    
    def stop_streaming(self):
        """Stop streaming"""
        self.streamer.stop_streaming()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.camera_combo.setEnabled(True)
        self.refresh_cameras_btn.setEnabled(True)
        self.width_spin.setEnabled(True)
        self.height_spin.setEnabled(True)
        self.fps_spin.setEnabled(True)
        self.port_spin.setEnabled(True)
        self.path_edit.setEnabled(True)
    
    def log_message(self, message: str):
        """Add message to log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.streamer.is_streaming:
            reply = QMessageBox.question(
                self, 
                'Confirm Exit',
                'Streaming is active. Are you sure you want to exit?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.streamer.cleanup()
                event.accept()
            else:
                event.ignore()
        else:
            self.streamer.cleanup()
            event.accept()
