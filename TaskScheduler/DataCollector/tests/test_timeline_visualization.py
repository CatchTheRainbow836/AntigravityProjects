"""
Unit and Integration Tests for Dynamic Timeline Canvas and Retrospective Aggregation.
"""

import unittest
import tempfile
import os
import sys
from datetime import datetime, timedelta, timezone

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from ui.components.timeline_canvas import TimelineCanvas
from db_manager import DatabaseManager
from simulator import generate_sample_session

class TestTimelineVisualization(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    def test_segment_aggregation(self):
        # Create virtual canvas (headless test)
        canvas = TimelineCanvas.__new__(TimelineCanvas)
        canvas.segments = []

        base_time = datetime.now(timezone.utc)
        records = [
            {
                "id": 1,
                "timestamp": (base_time + timedelta(seconds=0)).isoformat(),
                "cognitive_state": "Coding",
                "domain_label": "Software Development",
                "confidence": 0.95,
                "app_name": "Code.exe"
            },
            {
                "id": 2,
                "timestamp": (base_time + timedelta(seconds=5)).isoformat(),
                "cognitive_state": "Coding",
                "domain_label": "Software Development",
                "confidence": 0.95,
                "app_name": "Code.exe"
            },
            {
                "id": 3,
                "timestamp": (base_time + timedelta(seconds=10)).isoformat(),
                "cognitive_state": "Writing",
                "domain_label": "Specialist Mathematics",
                "confidence": 0.90,
                "app_name": "OneNote.exe"
            }
        ]

        segments = canvas._aggregate_to_segments(records)
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0]["domain"], "Software Development")
        self.assertEqual(segments[0]["ids"], [1, 2])
        self.assertEqual(segments[1]["domain"], "Specialist Mathematics")
        self.assertEqual(segments[1]["ids"], [3])

    def test_retrospective_database_label_override(self):
        samples = generate_sample_session(5)
        self.db.insert_batch(samples)
        records = self.db.get_recent_records(5)
        rec_id = records[0]["id"]

        # User retrospectively corrects activity
        self.db.update_record_label(rec_id, "Physics", "DEEP_FOCUS_WRITING")
        updated = self.db.get_recent_records(5)
        matched = [r for r in updated if r["id"] == rec_id][0]

        self.assertEqual(matched["domain_label"], "Physics")
        self.assertEqual(matched["cognitive_state"], "DEEP_FOCUS_WRITING")
        self.assertEqual(matched["label_source"], "USER_VERIFIED")
        self.assertEqual(matched["confidence_score"], 1.0)
        self.assertEqual(matched["finalized_value"], 1)

if __name__ == "__main__":
    unittest.main()
