"""
Unit tests for HeuristicClassifier.
"""

import unittest
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from classifier import HeuristicClassifier

class TestHeuristicClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = HeuristicClassifier()

    def test_idle_classification(self):
        record = {
            "app_name": "LockApp.exe",
            "window_title_sanitized": "Windows Lock Screen",
            "system_idle_seconds": 120.0,
            "keystrokes_per_min": 0.0,
            "mouse_velocity_avg": 0.0,
            "clicks_count": 0,
            "scroll_delta": 0,
            "is_audio_playing": False,
            "is_fullscreen": True
        }
        res = self.classifier.classify(record)
        self.assertEqual(res["cognitive_state"], "IDLE_AWAY")
        self.assertEqual(res["confidence"], 1.0)

    def test_coding_classification(self):
        record = {
            "app_name": "code.exe",
            "window_title_sanitized": "engine.py - DataCollector - Visual Studio Code",
            "system_idle_seconds": 0.0,
            "keystrokes_per_min": 120.0,
            "mouse_velocity_avg": 45.0,
            "clicks_count": 3,
            "scroll_delta": 0,
            "is_audio_playing": True,
            "is_fullscreen": False
        }
        res = self.classifier.classify(record)
        self.assertEqual(res["cognitive_state"], "ACTIVE_CODING")
        self.assertEqual(res["domain_label"], "Software Development")
        self.assertGreaterEqual(res["confidence"], 0.85)

    def test_specialist_math_classification(self):
        record = {
            "app_name": "OneNote.exe",
            "window_title_sanitized": "OneNote - Specialist Mathematics - Unit 3 Vectors and Calculus",
            "system_idle_seconds": 0.0,
            "keystrokes_per_min": 80.0,
            "mouse_velocity_avg": 120.0,
            "clicks_count": 5,
            "scroll_delta": 20,
            "is_audio_playing": False,
            "is_fullscreen": False
        }
        res = self.classifier.classify(record)
        self.assertEqual(res["cognitive_state"], "DEEP_FOCUS_WRITING")
        self.assertEqual(res["domain_label"], "Specialist Mathematics")
        self.assertGreaterEqual(res["confidence"], 0.85)

    def test_physics_reading_classification(self):
        record = {
            "app_name": "chrome.exe",
            "window_title_sanitized": "Thermodynamics and Kinematics Lecture Notes - PDF",
            "system_idle_seconds": 0.0,
            "keystrokes_per_min": 5.0,
            "mouse_velocity_avg": 25.0,
            "clicks_count": 2,
            "scroll_delta": 150,
            "is_audio_playing": False,
            "is_fullscreen": False
        }
        res = self.classifier.classify(record)
        self.assertEqual(res["cognitive_state"], "RESEARCH_READING")
        self.assertEqual(res["domain_label"], "Physics")
        self.assertGreaterEqual(res["confidence"], 0.80)

if __name__ == "__main__":
    unittest.main()
