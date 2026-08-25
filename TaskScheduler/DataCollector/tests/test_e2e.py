"""
End-to-end integration test for the full DataCollector application lifecycle:
Consent → Simulate Recording → Heuristic Classification → Timeline Edit → Incremental Export
"""

import unittest
import os
import sys
import tempfile
import json
import time

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from db_manager import DatabaseManager
from classifier import HeuristicClassifier
from engine import TelemetryEngine
from exporter import DatasetExporter
from active_learning import ActiveLearningManager
from ui.disclaimer import DisclaimerManager
from ui.dashboard import DashboardPresenter
from ui.timeline import RetrospectiveTimeline
from simulator import generate_sample_session


class TestEndToEndLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.temp_consent = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_consent.close()
        self.export_dir = tempfile.mkdtemp()

        self.db = DatabaseManager(self.temp_db.name)
        self.classifier = HeuristicClassifier()
        self.disclaimer = DisclaimerManager(self.temp_consent.name)
        self.engine = TelemetryEngine(
            db=self.db, sample_interval=0.05,
            classifier_fn=self.classifier.classify
        )
        self.dashboard = DashboardPresenter(
            engine=self.engine, db=self.db, disclaimer_mgr=self.disclaimer
        )
        self.exporter = DatasetExporter(self.db, export_dir=self.export_dir)

    def tearDown(self):
        self.engine.stop()
        self.db.close()
        for path in [self.temp_db.name, self.temp_consent.name]:
            if os.path.exists(path):
                os.remove(path)
        for f in os.listdir(self.export_dir):
            os.remove(os.path.join(self.export_dir, f))
        os.rmdir(self.export_dir)

    def test_full_lifecycle(self):
        # Step 1: No consent → recording blocked
        self.assertFalse(self.dashboard.can_start_recording())
        self.assertFalse(self.dashboard.start_recording())
        self.assertEqual(self.db.count_records(), 0)

        # Step 2: Grant consent → recording can start
        self.disclaimer.grant_consent()
        self.assertTrue(self.dashboard.can_start_recording())

        # Step 3: Simulate telemetry records via engine
        self.assertTrue(self.dashboard.start_recording())
        time.sleep(0.2)
        self.dashboard.stop_recording()
        records_from_engine = self.db.count_records()
        self.assertGreaterEqual(records_from_engine, 2)

        # Step 4: Also insert batch of simulated records directly
        samples = generate_sample_session(20)
        self.db.insert_batch(samples)
        total_records = self.db.count_records()
        self.assertGreaterEqual(total_records, records_from_engine + 20)

        # Step 5: Timeline shows grouped blocks
        timeline = RetrospectiveTimeline(self.db)
        blocks = timeline.get_timeline_blocks()
        self.assertGreater(len(blocks), 0)

        # Step 6: Apply retrospective label edit to first block
        first_block = blocks[0]
        updated = timeline.update_block_label(
            first_block["record_ids"],
            new_domain_label="Specialist Mathematics",
            new_cognitive_state="DEEP_FOCUS_WRITING"
        )
        self.assertGreater(updated, 0)

        # Step 7: First incremental export — all records
        m1 = self.exporter.export_incremental(fmt="jsonl")
        self.assertEqual(m1["record_count"], total_records)
        self.assertTrue(os.path.exists(m1["file_path"]))
        self.assertEqual(len(m1["content_hash"]), 64)

        # Verify JSON file is valid and labelled record is present
        with open(m1["file_path"], "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        retroactively_edited = [l for l in lines if l["label_source"] == "RETROSPECTIVE_EDIT"]
        self.assertGreaterEqual(len(retroactively_edited), updated)

        # Step 8: Second export is empty (deduplication guaranteed)
        m2 = self.exporter.export_incremental(fmt="jsonl")
        self.assertEqual(m2["record_count"], 0)

        # Step 9: Dashboard state is coherent
        state = self.dashboard.get_dashboard_state()
        self.assertTrue(state["has_consented"])
        self.assertFalse(state["is_recording"])
        self.assertGreater(state["total_db_records"], 0)


if __name__ == "__main__":
    unittest.main()
