"""
Autostart Manager for DataCollector.
Manages automatic startup registration in Windows Registry / Startup folder
strictly following user disclaimer consent.
"""

import sys
import os
from typing import Optional

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import winreg

class AutostartManager:
    APP_NAME = "DataCollector"
    REG_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def __init__(self, executable_path: Optional[str] = None):
        if executable_path:
            self.executable_path = executable_path
        else:
            self.executable_path = os.path.abspath(sys.argv[0])

    def is_autostart_enabled(self) -> bool:
        if not IS_WINDOWS:
            return False
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_KEY_PATH, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, self.APP_NAME)
                return bool(value)
        except (FileNotFoundError, OSError):
            return False

    def enable_autostart(self) -> bool:
        """Register executable to run on Windows startup under HKCU."""
        if not IS_WINDOWS:
            return True # Simulated success on non-Windows
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
                # Add background argument if running as standalone exe
                cmd = f'"{self.executable_path}" --background'
                winreg.SetValueEx(key, self.APP_NAME, 0, winreg.REG_SZ, cmd)
                return True
        except OSError as e:
            print(f"Failed to enable autostart in registry: {e}")
            return False

    def disable_autostart(self) -> bool:
        """Remove executable from Windows startup registry."""
        if not IS_WINDOWS:
            return True
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, self.APP_NAME)
                return True
        except FileNotFoundError:
            return True # Already disabled
        except OSError as e:
            print(f"Failed to disable autostart in registry: {e}")
            return False
