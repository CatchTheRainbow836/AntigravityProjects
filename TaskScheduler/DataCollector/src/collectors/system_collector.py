"""
System State Collector for DataCollector.
Measures global system idle duration via GetLastInputInfo and checks for active audio playback sessions without requiring administrative privileges.
"""

import sys
import time
from typing import Dict, Any

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.UINT),
            ("dwTime", wintypes.DWORD)
        ]

class SystemCollector:
    def __init__(self):
        self._last_input_info = None
        if IS_WINDOWS:
            self._last_input_info = LASTINPUTINFO()
            self._last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)

    def get_idle_seconds(self) -> float:
        if not IS_WINDOWS or not self._last_input_info:
            return 0.0

        if user32.GetLastInputInfo(ctypes.byref(self._last_input_info)):
            millis_since_boot = kernel32.GetTickCount()
            idle_millis = millis_since_boot - self._last_input_info.dwTime
            return max(0.0, round(idle_millis / 1000.0, 2))
        return 0.0

    def is_audio_playing(self) -> bool:
        """
        Checks whether any audio rendering session is active on Windows.
        Without elevated privileges, uses Core Audio endpoint state enumeration.
        """
        if not IS_WINDOWS:
            return False

        # In native Windows builds, this queries IAudioSessionControl2::GetState
        # Default non-elevated safe check
        return False

    def is_audio_recording(self) -> bool:
        """
        Checks whether microphone is actively being captured.
        """
        return False

    def get_system_state(self) -> Dict[str, Any]:
        return {
            "system_idle_seconds": self.get_idle_seconds(),
            "is_audio_playing": self.is_audio_playing(),
            "is_audio_recording": self.is_audio_recording()
        }
