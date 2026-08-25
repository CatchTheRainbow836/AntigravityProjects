"""
Unit and integration tests for TelemetryEngine.
"""

import unittest
import os
import sys
import time
import tempfile

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from engine import TelemetryEngine
from db_manager import DatabaseManager

class TestTelemetryEngine(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    def test_engine_recording_loop(self):
        engine = TelemetryEngine(db=self.db, sample_interval=0.1)
        engine.start()
        self.assertTrue(engine.is_running)

        # Let it collect a few slices
        time.sleep(0.35)
        stats = engine.get_current_stats()
        self.assertGreaterEqual(stats["total_records"], 2)
        self.assertIsNotNone(stats["latest_record"])

        engine.pause()
        self.assertTrue(engine.is_paused)

        engine.stop()
        self.assertFalse(engine.is_running)

        # Verify DB records
        count = self.db.count_records()
        self.assertGreaterEqual(count, 2)

    def test_engine_with_classifier_hook(self):
        def mock_classifier(record):
            return {
                "cognitive_state": "ACTIVE_CODING",
                "domain_label": "Software Engineering",
                "confidence": 0.95
            }

        engine = TelemetryEngine(db=self.db, sample_interval=0.05, classifier_fn=mock_classifier)
        engine.start()
        time.sleep(0.12)
        engine.stop()

        records = self.db.get_unexported_records()
        self.assertGreaterEqual(len(records), 1)
        self.assertEqual(records[0]["cognitive_state"], "ACTIVE_CODING")
        self.assertEqual(records[0]["domain_label"], "Software Engineering")
        self.assertEqual(records[0]["confidence"], 0.95)

if __name__ == "__main__":
    unittest.main()
