"""
Window and Screen Geometry Collector for DataCollector.
Extracts foreground process name, sanitized window titles, bounding boxes, and screen ratio coverage without requiring administrative privileges.
"""

import sys
import os
import re
from typing import Dict, Any

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi

class WindowCollector:
    def __init__(self):
        self._cached_screen_width = 1920
        self._cached_screen_height = 1080
        if IS_WINDOWS:
            self._cached_screen_width = user32.GetSystemMetrics(0) # SM_CXSCREEN
            self._cached_screen_height = user32.GetSystemMetrics(1) # SM_CYSCREEN

    def sanitize_title(self, raw_title: str) -> str:
        if not raw_title:
            return "Untitled Window"

        title = raw_title.strip()
        # Remove emails
        title = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', title)
        # Remove URL parameters (tokens, auth queries)
        title = re.sub(r'(\?|&)(token|key|auth|session|code)=[^&\s]+', r'\1\2=[REDACTED]', title)
        # Clean excessive whitespace
        title = re.sub(r'\s+', ' ', title)
        return title[:200]

    def get_active_window_info(self) -> Dict[str, Any]:
        if not IS_WINDOWS:
            return {
                "app_name": "DevelopmentEnvironment.exe",
                "window_title_sanitized": "Active Development Window",
                "screen_area_pct": 100.0,
                "is_fullscreen": False,
                "window_rect": {"left": 0, "top": 0, "right": 1920, "bottom": 1080}
            }

        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return {
                "app_name": "System.exe",
                "window_title_sanitized": "Desktop",
                "screen_area_pct": 100.0,
                "is_fullscreen": False,
                "window_rect": {"left": 0, "top": 0, "right": self._cached_screen_width, "bottom": self._cached_screen_height}
            }

        # Get window title
        length = user32.GetWindowTextLengthW(hwnd)
        title_buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, title_buffer, length + 1)
        raw_title = title_buffer.value

        # Get Process Name
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        app_name = "Unknown.exe"

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        h_process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
        if h_process:
            exe_buffer = ctypes.create_unicode_buffer(1024)
            size = wintypes.DWORD(1024)
            if kernel32.QueryFullProcessImageNameW(h_process, 0, exe_buffer, ctypes.byref(size)):
                app_name = os.path.basename(exe_buffer.value)
            kernel32.CloseHandle(h_process)

        # Get Window Geometry
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        width = max(0, rect.right - rect.left)
        height = max(0, rect.bottom - rect.top)

        screen_area = max(1, self._cached_screen_width * self._cached_screen_height)
        window_area = width * height
        area_pct = min(100.0, round((window_area / screen_area) * 100.0, 1))

        is_fullscreen = (width >= self._cached_screen_width and height >= self._cached_screen_height)

        return {
            "app_name": app_name,
            "window_title_sanitized": self.sanitize_title(raw_title),
            "screen_area_pct": area_pct,
            "is_fullscreen": is_fullscreen,
            "window_rect": {"left": rect.left, "top": rect.top, "right": rect.right, "bottom": rect.bottom}
        }
