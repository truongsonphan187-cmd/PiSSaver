"""
System Tray management and user interaction menu.
Provides quick access to configuration, image selection, and screensaver launch.
"""

import os
import sys
import logging
from PyQt6.QtWidgets import (
    QSystemTrayIcon, QMenu, QFileDialog, QApplication
)
from PyQt6.QtGui import QIcon, QAction, QActionGroup
from PyQt6.QtCore import QObject

from src.config import (
    load_config, save_config, resolve_image_path,
    is_run_on_startup_enabled, set_run_on_startup, get_app_dir
)
from src.screensaver_window import ScreensaverManager


class SystemTrayManager(QObject):
    """Manages the System Tray icon and the contextual popup menu."""

    def __init__(self, screensaver_mgr: ScreensaverManager, config: dict):
        super().__init__()
        self.mgr = screensaver_mgr
        self.config = config
        
        # Resolve icon path
        icon_path = os.path.join(get_app_dir(), "assets", "icon.ico")
        if not os.path.exists(icon_path):
            base_dir = getattr(sys, '_MEIPASS', get_app_dir())
            icon_path = os.path.join(base_dir, "assets", "icon.ico")
        
        self.icon = QIcon(icon_path)
        self.tray = QSystemTrayIcon(self.icon)
        self.tray.setToolTip("PiSSaver - Circular LED Matrix Screensaver\nLeft-click to start screensaver")
        
        # Setup context menu
        self.menu = QMenu()
        self.setup_menu()
        self.tray.setContextMenu(self.menu)
        
        # Handle left-click activation
        self.tray.activated.connect(self.on_tray_activated)

    def setup_menu(self):
        self.menu.clear()

        # 1. Start Screensaver
        act_start = QAction("🚀 Start Screensaver", self)
        act_start.triggered.connect(self.mgr.start)
        self.menu.addAction(act_start)

        self.menu.addSeparator()

        # 2. Choose Image
        act_change_img = QAction("🖼️ Choose Image...", self)
        act_change_img.triggered.connect(self.on_select_image)
        self.menu.addAction(act_change_img)

        # 3. Submenu: LED Dot Size
        menu_led = self.menu.addMenu("⚙️ LED Dot Size")
        group_led = QActionGroup(self)
        
        current_led = self.config.get("led_size", 10)
        led_options = [
            ("Fine (6px)", 6),
            ("Medium (10px)", 10),
            ("Coarse (16px)", 16)
        ]
        for label, val in led_options:
            act = QAction(label, self, checkable=True)
            act.setChecked(val == current_led)
            act.triggered.connect(lambda checked, v=val: self.on_change_led_size(v))
            group_led.addAction(act)
            menu_led.addAction(act)

        # 4. Submenu: Wave Speed
        menu_wave = self.menu.addMenu("🌊 Wave Speed")
        group_wave = QActionGroup(self)
        
        current_wave = self.config.get("wave_speed", 1.2)
        wave_options = [
            ("Static (Off)", 0.0),
            ("Slow & Chill (0.8)", 0.8),
            ("Standard (1.2)", 1.2),
            ("Fast (2.0)", 2.0)
        ]
        for label, val in wave_options:
            act = QAction(label, self, checkable=True)
            act.setChecked(abs(val - current_wave) < 0.1)
            act.triggered.connect(lambda checked, v=val: self.on_change_wave_speed(v))
            group_wave.addAction(act)
            menu_wave.addAction(act)

        self.menu.addSeparator()

        # 5. Open Image Folder
        act_open_folder = QAction("📁 Open Image Folder", self)
        act_open_folder.triggered.connect(self.on_open_image_folder)
        self.menu.addAction(act_open_folder)

        # 6. Run on Startup
        is_startup = is_run_on_startup_enabled()
        act_startup = QAction("🔄 Run on Windows Startup", self, checkable=True)
        act_startup.setChecked(is_startup)
        act_startup.triggered.connect(self.on_toggle_startup)
        self.menu.addAction(act_startup)

        self.menu.addSeparator()

        # 7. Exit
        act_exit = QAction("❌ Exit", self)
        act_exit.triggered.connect(self.on_exit)
        self.menu.addAction(act_exit)

    def on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.mgr.start()

    def on_select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Image for LED Matrix Screensaver",
            get_app_dir(),
            "Images (*.jpg *.jpeg *.png *.webp *.bmp);;All Files (*.*)"
        )
        if file_path:
            self.config["image_path"] = file_path
            save_config(self.config)
            self.tray.showMessage(
                "PiSSaver",
                f"New image loaded: {os.path.basename(file_path)}",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )

    def on_change_led_size(self, size: int):
        self.config["led_size"] = size
        save_config(self.config)
        self.setup_menu()

    def on_change_wave_speed(self, speed: float):
        self.config["wave_speed"] = speed
        save_config(self.config)
        self.setup_menu()

    def on_open_image_folder(self):
        img_path = resolve_image_path(self.config.get("image_path", "assets/custom.jpg"))
        target_folder = os.path.join(get_app_dir(), "assets")
        os.makedirs(target_folder, exist_ok=True)
        
        target_custom = os.path.join(target_folder, "custom.jpg")
        if not os.path.exists(target_custom) and os.path.exists(img_path):
            try:
                import shutil
                shutil.copyfile(img_path, target_custom)
            except Exception as e:
                logging.error(f"Failed to copy image to {target_custom}: {e}")

        final_folder = target_folder if os.path.exists(target_folder) else get_app_dir()
        os.startfile(final_folder)

    def on_toggle_startup(self, checked: bool):
        set_run_on_startup(checked)
        self.config["run_on_startup"] = checked
        save_config(self.config)

    def on_exit(self):
        logging.info("User requested exit from System Tray.")
        self.mgr.stop()
        self.tray.hide()
        QApplication.quit()

    def show(self):
        self.tray.show()
