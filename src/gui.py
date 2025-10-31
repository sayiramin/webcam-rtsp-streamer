"""
GUI for Webcam RTSP Streamer using PySide6
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QSpinBox, 
    QTextEdit, QGroupBox, QGridLayout, QLineEdit,
    QMessageBox, QSystemTrayIcon, QMenu, QCheckBox, QFileDialog,
    QTabWidget
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
        
        # Create tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Main tab
        main_tab = QWidget()
        tab_widget.addTab(main_tab, "Streaming")
        
        # Watermark tab
        watermark_tab = QWidget()
        tab_widget.addTab(watermark_tab, "Watermark")
        
        # Setup main tab layout
        main_tab_layout = QVBoxLayout(main_tab)
        
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
        main_tab_layout.addWidget(camera_group)
        
        # Stream configuration group
        config_group = QGroupBox("Stream Configuration")
        config_layout = QGridLayout()
        
        # Quality preset
        config_layout.addWidget(QLabel("Quality Preset:"), 0, 0)
        self.quality_preset = QComboBox()
        from config import Config as ConfigClass
        for key, preset in ConfigClass.QUALITY_PRESETS.items():
            self.quality_preset.addItem(preset["name"], key)
        
        # Set current preset
        current_preset = self.config.get("quality_preset", "medium")
        for i in range(self.quality_preset.count()):
            if self.quality_preset.itemData(i) == current_preset:
                self.quality_preset.setCurrentIndex(i)
                break
        
        self.quality_preset.currentIndexChanged.connect(self.on_quality_preset_changed)
        config_layout.addWidget(self.quality_preset, 0, 1, 1, 2)
        
        config_layout.addWidget(QLabel("Resolution:"), 1, 0)
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
        config_layout.addLayout(resolution_layout, 1, 1)
        
        config_layout.addWidget(QLabel("FPS:"), 2, 0)
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(5, 60)
        self.fps_spin.setValue(self.config.get("video_fps", 30))
        config_layout.addWidget(self.fps_spin, 2, 1)
        
        config_layout.addWidget(QLabel("RTSP Port:"), 3, 0)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(self.config.get("rtsp_port", 8554))
        config_layout.addWidget(self.port_spin, 3, 1)
        
        config_layout.addWidget(QLabel("RTSP Path:"), 4, 0)
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.config.get("rtsp_path", "stream"))
        config_layout.addWidget(self.path_edit, 4, 1)
        
        config_group.setLayout(config_layout)
        main_tab_layout.addWidget(config_group)
        
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
        main_tab_layout.addWidget(url_group)
        
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
        
        main_tab_layout.addLayout(button_layout)
        
        # Setup watermark tab
        self.setup_watermark_tab(watermark_tab)
        
        # Status/Log area (add to main layout, not tab)
        log_group = QGroupBox("Status Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
    
    def setup_watermark_tab(self, watermark_tab):
        """Setup watermark configuration tab"""
        watermark_layout = QVBoxLayout(watermark_tab)
        
        # Watermark configuration group
        watermark_group = QGroupBox("Watermark Settings")
        watermark_grid = QGridLayout()
        
        # Enable watermark checkbox
        self.watermark_enabled = QCheckBox("Enable Watermark")
        self.watermark_enabled.setChecked(self.config.get("watermark_enabled", False))
        self.watermark_enabled.stateChanged.connect(self.toggle_watermark_controls)
        watermark_grid.addWidget(self.watermark_enabled, 0, 0, 1, 3)
        
        # Watermark type
        watermark_grid.addWidget(QLabel("Type:"), 1, 0)
        self.watermark_type = QComboBox()
        self.watermark_type.addItems(["Text", "Image", "Timestamp"])
        watermark_type_value = self.config.get("watermark_type", "text")
        self.watermark_type.setCurrentText(watermark_type_value.capitalize())
        self.watermark_type.currentTextChanged.connect(self.on_watermark_type_changed)
        watermark_grid.addWidget(self.watermark_type, 1, 1, 1, 2)
        
        # Text input
        watermark_grid.addWidget(QLabel("Text:"), 2, 0)
        self.watermark_text = QLineEdit()
        self.watermark_text.setText(self.config.get("watermark_text", "Camera Stream"))
        watermark_grid.addWidget(self.watermark_text, 2, 1, 1, 2)
        
        # Image file picker
        watermark_grid.addWidget(QLabel("Image:"), 3, 0)
        self.watermark_image = QLineEdit()
        self.watermark_image.setText(self.config.get("watermark_image_path", ""))
        self.watermark_image.setPlaceholderText("Select image file...")
        watermark_grid.addWidget(self.watermark_image, 3, 1)
        
        self.watermark_browse_btn = QPushButton("Browse")
        self.watermark_browse_btn.clicked.connect(self.browse_watermark_image)
        watermark_grid.addWidget(self.watermark_browse_btn, 3, 2)
        
        # Position
        watermark_grid.addWidget(QLabel("Position:"), 4, 0)
        self.watermark_position = QComboBox()
        self.watermark_position.addItems(["Top Left", "Top Right", "Bottom Left", "Bottom Right", "Center"])
        position_value = self.config.get("watermark_position", "top-right")
        position_map = {"top-left": "Top Left", "top-right": "Top Right", 
                       "bottom-left": "Bottom Left", "bottom-right": "Bottom Right", "center": "Center"}
        self.watermark_position.setCurrentText(position_map.get(position_value, "Top Right"))
        watermark_grid.addWidget(self.watermark_position, 4, 1, 1, 2)
        
        watermark_group.setLayout(watermark_grid)
        watermark_layout.addWidget(watermark_group)
        
        # Add stretch to push everything to top
        watermark_layout.addStretch()
        
        # Initialize watermark controls state
        self.toggle_watermark_controls()
        self.on_watermark_type_changed(self.watermark_type.currentText())
        
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
    
    def toggle_watermark_controls(self):
        """Enable/disable watermark controls based on checkbox"""
        enabled = self.watermark_enabled.isChecked()
        self.watermark_type.setEnabled(enabled)
        self.watermark_text.setEnabled(enabled)
        self.watermark_image.setEnabled(enabled)
        self.watermark_browse_btn.setEnabled(enabled)
        self.watermark_position.setEnabled(enabled)
        if enabled:
            self.on_watermark_type_changed(self.watermark_type.currentText())
    
    def on_watermark_type_changed(self, wm_type):
        """Show/hide appropriate controls based on watermark type"""
        is_text = wm_type == "Text"
        is_timestamp = wm_type == "Timestamp"
        is_image = wm_type == "Image"
        
        enabled = self.watermark_enabled.isChecked()
        self.watermark_text.setVisible((is_text or is_timestamp) and enabled)
        self.watermark_image.setVisible(is_image and enabled)
        self.watermark_browse_btn.setVisible(is_image and enabled)
    
    def browse_watermark_image(self):
        """Open file dialog to select watermark image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Watermark Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.watermark_image.setText(file_path)
    
    def on_quality_preset_changed(self, index):
        """Update settings based on quality preset selection"""
        from config import Config as ConfigClass
        preset_key = self.quality_preset.itemData(index)
        preset = ConfigClass.QUALITY_PRESETS.get(preset_key)
        
        if preset:
            self.width_spin.setValue(preset["width"])
            self.height_spin.setValue(preset["height"])
            self.fps_spin.setValue(preset["fps"])
    
    def start_streaming(self):
        """Start streaming"""
        # Update config from UI
        self.config.set("camera_index", self.camera_combo.currentData())
        self.config.set("quality_preset", self.quality_preset.currentData())
        self.config.set("video_width", self.width_spin.value())
        self.config.set("video_height", self.height_spin.value())
        self.config.set("video_fps", self.fps_spin.value())
        self.config.set("rtsp_port", self.port_spin.value())
        self.config.set("rtsp_path", self.path_edit.text())
        
        # Update bitrate based on quality preset
        from config import Config as ConfigClass
        preset = ConfigClass.QUALITY_PRESETS.get(self.quality_preset.currentData())
        if preset:
            self.config.set("video_bitrate", preset["bitrate"])
            self.config.set("preset", preset["preset"])
        
        # Update watermark config
        self.config.set("watermark_enabled", self.watermark_enabled.isChecked())
        self.config.set("watermark_type", self.watermark_type.currentText().lower())
        self.config.set("watermark_text", self.watermark_text.text())
        self.config.set("watermark_image_path", self.watermark_image.text())
        position_map = {"Top Left": "top-left", "Top Right": "top-right", 
                       "Bottom Left": "bottom-left", "Bottom Right": "bottom-right", "Center": "center"}
        self.config.set("watermark_position", position_map.get(self.watermark_position.currentText(), "top-right"))
        
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
