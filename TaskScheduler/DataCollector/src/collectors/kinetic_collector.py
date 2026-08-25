"""
Kinetic Collector for DataCollector.
Measures aggregate keyboard activity cadence and mouse kinetics without recording raw characters or compromising user privacy.
"""

import time
import math
import sys
from typing import Dict, Any, Tuple

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32

class KineticCollector:
    def __init__(self):
        self.is_running = False
        self._last_sample_time = time.time()
        self._last_mouse_pos = (0, 0)
        self._keystroke_count = 0
        self._click_count = 0
        self._scroll_delta = 0
        self._total_distance_px = 0.0

    def start(self):
        self.is_running = True
        self._last_sample_time = time.time()
        self._last_mouse_pos = self._get_cursor_pos()
        self._keystroke_count = 0
        self._click_count = 0
        self._scroll_delta = 0
        self._total_distance_px = 0.0

    def stop(self):
        self.is_running = False

    def _get_cursor_pos(self) -> Tuple[int, int]:
        if IS_WINDOWS:
            point = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(point))
            return (point.x, point.y)
        return (0, 0)

    def record_keystroke(self, count: int = 1):
        """Aggregate keystroke accumulator — no raw key characters recorded."""
        self._keystroke_count += count

    def record_click(self, count: int = 1):
        self._click_count += count

    def record_scroll(self, delta: int):
        self._scroll_delta += delta

    def sample(self) -> Dict[str, Any]:
        """Slices and resets the kinetic metrics for the current window."""
        now = time.time()
        elapsed = max(0.001, now - self._last_sample_time)
        
        # Calculate mouse movement
        current_mouse_pos = self._get_cursor_pos()
        dx = current_mouse_pos[0] - self._last_mouse_pos[0]
        dy = current_mouse_pos[1] - self._last_mouse_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        self._total_distance_px += distance
        velocity = self._total_distance_px / elapsed

        # Calculate keystrokes per minute
        kpm = (self._keystroke_count / elapsed) * 60.0
        burst_rate = round(self._keystroke_count / elapsed, 2)

        data = {
            "keystrokes_per_min": round(kpm, 1),
            "typing_burst_rate": burst_rate,
            "mouse_velocity_avg": round(velocity, 1),
            "clicks_count": self._click_count,
            "scroll_delta": self._scroll_delta,
            "sample_duration": round(elapsed, 3)
        }

        # Reset counters for next slice
        self._last_sample_time = now
        self._last_mouse_pos = current_mouse_pos
        self._keystroke_count = 0
        self._click_count = 0
        self._scroll_delta = 0
        self._total_distance_px = 0.0

        return data
