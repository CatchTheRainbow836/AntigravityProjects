"""
Unit and Integration Tests for Multi-State Activity Classifier and 75% Confidence Thresholding.
"""

import unittest
import tempfile
import os
import json
import sys

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from classifier import HeuristicClassifier, CONFIDENCE_THRESHOLD
from db_manager import DatabaseManager

class TestMultiStateClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = HeuristicClassifier()
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    def test_concurrent_coding_and_music(self):
        sample = {
            "app_name": "Code.exe",
            "window_title_sanitized": "main.py - DataCollector - Visual Studio Code",
            "keystrokes_per_min": 45.0,
            "mouse_velocity_avg": 80.0,
            "is_audio_playing": True,
            "visible_windows": [
                {"title": "Spotify Premium", "process": "Spotify.exe", "is_foreground": False}
            ]
        }
        res = self.classifier.classify(sample)
        self.assertEqual(res["cognitive_state"], "ACTIVE_CODING")
        self.assertGreaterEqual(res["confidence"], CONFIDENCE_THRESHOLD)
        self.assertEqual(res["finalized_value"], 1)
        self.assertEqual(res["active_states"]["Coding"], 1)
        self.assertEqual(res["active_states"]["Music"], 1)

    def test_multi_screen_research_and_video(self):
        sample = {
            "app_name": "msedge.exe",
            "window_title_sanitized": "Quantum Mechanics & Kinematics - Physics Lecture",
            "scroll_delta": 40,
            "is_audio_playing": True,
            "visible_windows": [
                {"title": "PhET Physics Simulation", "process": "chrome.exe", "is_foreground": False}
            ]
        }
        res = self.classifier.classify(sample)
        self.assertGreaterEqual(res["confidence"], CONFIDENCE_THRESHOLD)
        self.assertEqual(res["finalized_value"], 1)
        self.assertEqual(res["domain_label"], "Physics")
        self.assertEqual(res["active_states"]["Research"], 1)
        self.assertEqual(res["active_states"]["Music"], 1)

    def test_low_confidence_ambiguous_activity(self):
        sample = {
            "app_name": "Explorer.exe",
            "window_title_sanitized": "Downloads Folder",
            "keystrokes_per_min": 0.0,
            "mouse_velocity_avg": 5.0,
            "is_audio_playing": False,
            "system_idle_seconds": 10.0
        }
        res = self.classifier.classify(sample)
        self.assertLess(res["confidence"], CONFIDENCE_THRESHOLD)
        self.assertEqual(res["finalized_value"], 0)

    def test_database_persistence_of_multistate_v2(self):
        sample = {
            "timestamp": "2026-08-31T12:00:00Z",
            "app_name": "Code.exe",
            "window_title_sanitized": "classifier.py - Visual Studio Code",
            "keystrokes_per_min": 60.0,
            "mouse_velocity_avg": 95.0,
            "is_audio_playing": True,
            "visible_windows": [{"title": "Spotify", "process": "Spotify.exe"}]
        }
        classification = self.classifier.classify(sample)
        record = {**sample, **classification}
        record_id = self.db.insert_record(record)
        self.assertGreater(record_id, 0)

        recent = self.db.get_recent_records(1)
        self.assertEqual(len(recent), 1)
        db_rec = recent[0]
        self.assertEqual(db_rec["finalized_value"], 1)
        self.assertAlmostEqual(db_rec["confidence_score"], classification["confidence"], places=2)
        active_states_saved = json.loads(db_rec["active_states_json"])
        self.assertEqual(active_states_saved["Coding"], 1)
        self.assertEqual(active_states_saved["Music"], 1)

if __name__ == "__main__":
    unittest.main()
