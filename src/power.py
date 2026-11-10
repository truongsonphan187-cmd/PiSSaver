"""
Module quản lý trạng thái nguồn Windows (Power Management).
Ngăn chặn màn hình tắt hoặc hệ thống rơi vào trạng thái Sleep/Hibernate khi screensaver đang chạy.
"""

import ctypes
import logging

# Các cờ Windows API SetThreadExecutionState
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


def prevent_sleep():
    """
    Kích hoạt chế độ thức liên tục:
    Ngăn Windows tắt màn hình và ngăn hệ thống vào Sleep.
    """
    try:
        res = ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED
        )
        if res == 0:
            logging.warning("Không thể thiết lập SetThreadExecutionState để ngăn sleep.")
        else:
            logging.info("Đã kích hoạt ngăn Windows tắt màn hình và sleep.")
    except Exception as e:
        logging.error(f"Lỗi khi gọi prevent_sleep: {e}")


def allow_sleep():
    """
    Hủy bỏ chế độ thức:
    Trả lại quyền quản lý năng lượng cho Windows theo mặc định.
    """
    try:
        res = ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        if res == 0:
            logging.warning("Không thể thiết lập SetThreadExecutionState về mặc định.")
        else:
            logging.info("Đã nhả quyền kiểm soát nguồn, Windows có thể sleep bình thường.")
    except Exception as e:
        logging.error(f"Lỗi khi gọi allow_sleep: {e}")
