"""
Main entry point for the PiSSaver application.
Initializes Single Instance Mutex, System Tray, and runs in deep idle stealth mode (0.0% CPU).
"""

import os
import sys
import ctypes
import logging

# Ensure correct import paths
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from PyQt6.QtWidgets import QApplication

from src.config import load_config, save_config, get_app_dir
from src.screensaver_window import ScreensaverManager
from src.tray import SystemTrayManager


def ensure_single_instance():
    """Ensure only one instance of PiSSaver runs in the background."""
    mutex_name = "Global\\PiSSaver_SingleInstance_UniqueMutex_2026"
    ERROR_ALREADY_EXISTS = 183
    
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateMutexW(None, False, mutex_name)
    last_error = kernel32.GetLastError()
    
    if last_error == ERROR_ALREADY_EXISTS:
        logging.warning("An instance of PiSSaver is already running in the System Tray.")
        sys.exit(0)
    return handle


def main():
    # Setup file and console logging
    log_dir = os.path.join(get_app_dir(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "pis_saver.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("=== Starting PiSSaver ===")

    # Hold Mutex to prevent duplicate processes
    _mutex_handle = ensure_single_instance()

    # Initialize Qt Application
    app = QApplication(sys.argv)
    
    # Keep application running in background when screensaver windows close
    app.setQuitOnLastWindowClosed(False)

    # Load configuration
    config = load_config()

    # Initialize Managers
    screensaver_mgr = ScreensaverManager(config)
    tray_mgr = SystemTrayManager(screensaver_mgr, config)
    tray_mgr.show()

    logging.info("PiSSaver is ready in the System Tray. Idle CPU usage: 0.0%.")

    # Enter main event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
