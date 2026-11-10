"""
Điểm khởi động chính của ứng dụng PiSSaver.
Khởi tạo Single Instance Mutex, System Tray và chạy ngầm 0% CPU.
"""

import os
import sys
import ctypes
import logging

# Đảm bảo đường dẫn import luôn hoạt động chính xác
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
    """Đảm bảo chỉ có duy nhất một tiến trình PiSSaver chạy ngầm dưới System Tray."""
    mutex_name = "Global\\PiSSaver_SingleInstance_UniqueMutex_2026"
    ERROR_ALREADY_EXISTS = 183
    
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateMutexW(None, False, mutex_name)
    last_error = kernel32.GetLastError()
    
    if last_error == ERROR_ALREADY_EXISTS:
        logging.warning("Một phiên bản của PiSSaver đã đang chạy dưới System Tray!")
        # Đã có app chạy, thoát instance thứ hai
        sys.exit(0)
    return handle


def main():
    # Cấu hình logging
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
    logging.info("=== Khởi động PiSSaver ===")

    # Giữ Mutex tránh chạy trùng lặp
    _mutex_handle = ensure_single_instance()

    # Khởi tạo Qt Application
    app = QApplication(sys.argv)
    
    # Quan trọng: Không thoát app khi các cửa sổ screensaver đóng lại!
    # App phải tiếp tục sống ngầm dưới System Tray.
    app.setQuitOnLastWindowClosed(False)

    # Nạp cấu hình
    config = load_config()

    # Khởi tạo Quản lý Screensaver
    screensaver_mgr = ScreensaverManager(config)

    # Khởi tạo Quản lý Khay hệ thống (System Tray)
    tray_mgr = SystemTrayManager(screensaver_mgr, config)
    tray_mgr.show()

    logging.info("PiSSaver đã sẵn sàng dưới System Tray. Trạng thái CPU = 0.0%.")

    # Bắt đầu vòng lặp sự kiện
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
