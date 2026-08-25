"""
Unit tests for Kinetic, Window, and System Collectors.
"""

import unittest
import os
import sys
import time

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from collectors.kinetic_collector import KineticCollector
from collectors.window_collector import WindowCollector
from collectors.system_collector import SystemCollector

class TestCollectors(unittest.TestCase):
    def test_kinetic_collector_lifecycle(self):
        collector = KineticCollector()
        collector.start()
        collector.record_keystroke(10)
        collector.record_click(2)
        collector.record_scroll(150)
        time.sleep(0.05)
        sample = collector.sample()
        
        self.assertIn("keystrokes_per_min", sample)
        self.assertIn("mouse_velocity_avg", sample)
        self.assertIn("clicks_count", sample)
        self.assertIn("scroll_delta", sample)
        self.assertEqual(sample["clicks_count"], 2)
        self.assertEqual(sample["scroll_delta"], 150)
        collector.stop()

    def test_window_title_sanitization(self):
        collector = WindowCollector()
        raw = "Inbox - student.user@university.edu - Google Chrome ?token=secret12345&auth=true"
        sanitized = collector.sanitize_title(raw)
        self.assertNotIn("student.user@university.edu", sanitized)
        self.assertIn("[REDACTED_EMAIL]", sanitized)
        self.assertNotIn("secret12345", sanitized)
        self.assertIn("token=[REDACTED]", sanitized)

    def test_system_collector_state(self):
        collector = SystemCollector()
        state = collector.get_system_state()
        self.assertIn("system_idle_seconds", state)
        self.assertIn("is_audio_playing", state)
        self.assertIn("is_audio_recording", state)
        self.assertIsInstance(state["system_idle_seconds"], float)
        self.assertIsInstance(state["is_audio_playing"], bool)

if __name__ == "__main__":
    unittest.main()
