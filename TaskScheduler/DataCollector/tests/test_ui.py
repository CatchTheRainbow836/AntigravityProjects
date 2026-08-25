"""
Unit tests for UI components: DisclaimerManager, DashboardPresenter, and RetrospectiveTimeline.
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

from ui.disclaimer import DisclaimerManager
from ui.timeline import RetrospectiveTimeline
from ui.dashboard import DashboardPresenter
from db_manager import DatabaseManager
from engine import TelemetryEngine
from simulator import generate_sample_session

class TestUIComponents(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)

        self.temp_consent = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_consent.close()
        self.disclaimer = DisclaimerManager(self.temp_consent.name)

        self.engine = TelemetryEngine(db=self.db, sample_interval=0.1)
        self.dashboard = DashboardPresenter(
            engine=self.engine,
            db=self.db,
            disclaimer_mgr=self.disclaimer
        )

    def tearDown(self):
        self.engine.stop()
        self.db.close()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)
        if os.path.exists(self.temp_consent.name):
            os.remove(self.temp_consent.name)

    def test_disclaimer_consent_lifecycle(self):
        self.assertFalse(self.disclaimer.has_consented())
        self.assertFalse(self.dashboard.can_start_recording())
        self.assertFalse(self.dashboard.start_recording()) # Blocked without consent

        # Grant consent
        self.assertTrue(self.disclaimer.grant_consent())
        self.assertTrue(self.disclaimer.has_consented())
        self.assertTrue(self.dashboard.can_start_recording())

        # Start recording succeeds with consent
        self.assertTrue(self.dashboard.start_recording())
        self.engine.stop()

        # Revoke consent
        self.disclaimer.revoke_consent()
        self.assertFalse(self.disclaimer.has_consented())

    def test_retrospective_timeline_grouping(self):
        # Insert consecutive samples with matching labels
        samples = [
            {
                "timestamp": "2026-08-25T09:00:00Z", "duration_seconds": 5.0,
                "app_name": "WINWORD.EXE", "window_title_sanitized": "Physics Essay.docx",
                "screen_area_pct": 100.0, "is_fullscreen": False, "keystrokes_per_min": 120.0,
                "typing_burst_rate": 1.2, "mouse_velocity_avg": 30.0, "clicks_count": 2,
                "scroll_delta": 0, "is_audio_playing": False, "is_audio_recording": False,
                "system_idle_seconds": 0.0, "cognitive_state": "DEEP_FOCUS_WRITING",
                "domain_label": "Physics", "confidence": 0.95, "label_source": "HEURISTIC_RULE"
            },
            {
                "timestamp": "2026-08-25T09:00:05Z", "duration_seconds": 5.0,
                "app_name": "WINWORD.EXE", "window_title_sanitized": "Physics Essay.docx",
                "screen_area_pct": 100.0, "is_fullscreen": False, "keystrokes_per_min": 140.0,
                "typing_burst_rate": 1.5, "mouse_velocity_avg": 25.0, "clicks_count": 1,
                "scroll_delta": 0, "is_audio_playing": False, "is_audio_recording": False,
                "system_idle_seconds": 0.0, "cognitive_state": "DEEP_FOCUS_WRITING",
                "domain_label": "Physics", "confidence": 0.95, "label_source": "HEURISTIC_RULE"
            },
            {
                "timestamp": "2026-08-25T09:00:10Z", "duration_seconds": 5.0,
                "app_name": "chrome.exe", "window_title_sanitized": "YouTube",
                "screen_area_pct": 100.0, "is_fullscreen": False, "keystrokes_per_min": 0.0,
                "typing_burst_rate": 0.0, "mouse_velocity_avg": 10.0, "clicks_count": 0,
                "scroll_delta": 0, "is_audio_playing": True, "is_audio_recording": False,
                "system_idle_seconds": 15.0, "cognitive_state": "MEDIA_CONSUMPTION",
                "domain_label": "Unlabeled", "confidence": 0.88, "label_source": "HEURISTIC_RULE"
            }
        ]
        self.db.insert_batch(samples)

        timeline = RetrospectiveTimeline(self.db)
        blocks = timeline.get_timeline_blocks()
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0]["domain_label"], "Physics")
        self.assertEqual(blocks[0]["sample_count"], 2)
        self.assertEqual(blocks[1]["cognitive_state"], "MEDIA_CONSUMPTION")

    def test_timeline_block_update(self):
        samples = generate_sample_session(5)
        self.db.insert_batch(samples)
        timeline = RetrospectiveTimeline(self.db)
        blocks = timeline.get_timeline_blocks()
        first_block = blocks[0]

        updated = timeline.update_block_label(
            first_block["record_ids"],
            new_domain_label="Specialist Mathematics",
            new_cognitive_state="DEEP_FOCUS_WRITING"
        )
        self.assertEqual(updated, len(first_block["record_ids"]))

        updated_blocks = timeline.get_timeline_blocks()
        self.assertEqual(updated_blocks[0]["domain_label"], "Specialist Mathematics")

    def test_dashboard_state_formatting(self):
        self.disclaimer.grant_consent()
        samples = generate_sample_session(3)
        self.db.insert_batch(samples)

        state = self.dashboard.get_dashboard_state()
        self.assertTrue(state["has_consented"])
        self.assertEqual(state["total_db_records"], 3)
        self.assertIn("current_app", state)
        self.assertIn("recent_timeline_blocks", state)

if __name__ == "__main__":
    unittest.main()
