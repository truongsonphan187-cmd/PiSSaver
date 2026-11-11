"""
Configuration management (settings.json) and Windows Registry Startup integration.
"""

import os
import sys
import json
import logging
import winreg

APP_NAME = "PiSSaver"
DEFAULT_CONFIG = {
    "image_path": "assets/custom.jpg",
    "led_size": 10,
    "led_spacing_ratio": 0.84,
    "wave_speed": 1.2,
    "wave_negative_dim": 0.28,
    "mouse_move_threshold": 15,
    "run_on_startup": False,
    "fps_target": 60
}


def get_app_dir() -> str:
    """Return application root directory (supports both script execution and frozen PyInstaller .exe)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_config_path() -> str:
    return os.path.join(get_app_dir(), "settings.json")


def load_config() -> dict:
    config_file = get_config_path()
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
                cfg.update(saved)
        except Exception as e:
            logging.error(f"Failed to read config file {config_file}: {e}")
    else:
        save_config(cfg)
    return cfg


def save_config(cfg: dict) -> bool:
    config_file = get_config_path()
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Failed to save config file {config_file}: {e}")
        return False


def resolve_image_path(image_path: str) -> str:
    """
    Resolve the absolute path of the image file.
    Priority:
    1. Explicit absolute path if exists.
    2. Relative to application directory (next to .exe or project root).
    3. Bundled asset in sys._MEIPASS (PyInstaller bundle).
    """
    if not image_path:
        image_path = "assets/custom.jpg"
    if os.path.isabs(image_path) and os.path.exists(image_path):
        return image_path

    app_target = os.path.normpath(os.path.join(get_app_dir(), image_path))
    if os.path.exists(app_target):
        return app_target

    if getattr(sys, "frozen", False):
        meipass_target = os.path.normpath(os.path.join(sys._MEIPASS, image_path))
        if os.path.exists(meipass_target):
            return meipass_target

    return app_target


def is_run_on_startup_enabled() -> bool:
    """Check if the application is registered to run on Windows startup."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, APP_NAME)
            return bool(val)
    except FileNotFoundError:
        return False
    except Exception as e:
        logging.error(f"Failed to query Startup Registry: {e}")
        return False


def set_run_on_startup(enable: bool) -> bool:
    """Add or remove application from Windows startup registry."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
            if enable:
                exe_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
                logging.info(f"Registered Run on Startup: {exe_path}")
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                    logging.info("Removed Run on Startup registration.")
                except FileNotFoundError:
                    pass
        return True
    except Exception as e:
        logging.error(f"Failed to update Startup Registry: {e}")
        return False
