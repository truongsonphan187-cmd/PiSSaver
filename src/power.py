"""
Windows Power Management module.
Prevents display sleep and system idle sleep while screensaver is active.
"""

import ctypes
import logging

# Windows API SetThreadExecutionState flags
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


def prevent_sleep():
    """
    Enable continuous keep-awake mode:
    Prevents display turn-off and system sleep/hibernate.
    """
    try:
        res = ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED
        )
        if res == 0:
            logging.warning("Unable to set SetThreadExecutionState to prevent sleep.")
        else:
            logging.info("Windows sleep prevention activated (Display & System stay awake).")
    except Exception as e:
        logging.error(f"Error calling prevent_sleep: {e}")


def allow_sleep():
    """
    Restore default power management:
    Allows Windows to sleep and turn off display normally.
    """
    try:
        res = ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        if res == 0:
            logging.warning("Unable to restore SetThreadExecutionState to default.")
        else:
            logging.info("Default Windows power state restored.")
    except Exception as e:
        logging.error(f"Error calling allow_sleep: {e}")
