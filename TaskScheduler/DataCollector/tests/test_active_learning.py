"""
Unit tests for ActiveLearningManager.
"""

import unittest
import os
import sys
import tempfile
import time

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from active_learning import ActiveLearningManager
from db_manager import DatabaseManager
from simulator import generate_sample_session

class TestActiveLearning(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)
        self.alm = ActiveLearningManager(self.db, confidence_threshold=0.6, prompt_interval_seconds=1.0)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    def test_prompt_trigger_on_low_confidence(self):
        rec_low = {"app_name": "unknown.exe", "cognitive_state": "UNCLASSIFIED", "confidence": 0.3}
        should_trigger = self.alm.evaluate_prompt_trigger(rec_low)
        self.assertTrue(should_trigger)

        # Immediate next low confidence should not trigger due to interval throttle
        should_trigger_again = self.alm.evaluate_prompt_trigger(rec_low)
        self.assertFalse(should_trigger_again)

        # After interval passes, should trigger again
        time.sleep(1.05)
        should_trigger_after_interval = self.alm.evaluate_prompt_trigger(rec_low)
        self.assertTrue(should_trigger_after_interval)

    def test_apply_user_label(self):
        samples = generate_sample_session(10)
        # Mark some as unclassified
        for s in samples[:5]:
            s["cognitive_state"] = "UNCLASSIFIED"
            s["domain_label"] = "Unlabeled"
            s["confidence"] = 0.3
            s["label_source"] = "HEURISTIC_RULE"
        self.db.insert_batch(samples)

        updated_count = self.alm.apply_user_label("Advanced Calculus", "DEEP_FOCUS_WRITING")
        self.assertGreaterEqual(updated_count, 1)

        unexported = self.db.get_unexported_records()
        labeled_records = [r for r in unexported if r["domain_label"] == "Advanced Calculus"]
        self.assertEqual(len(labeled_records), updated_count)
        self.assertEqual(labeled_records[0]["confidence"], 1.0)

    def test_add_user_preset(self):
        self.alm.add_user_preset("Mathematical Methods", "#10B981", ["methods", "probability"])
        cursor = self.db.conn.execute("SELECT * FROM user_presets WHERE preset_name='Mathematical Methods'")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["color_hex"], "#10B981")

if __name__ == "__main__":
    unittest.main()
