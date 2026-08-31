"""
End-to-End GUI Lifecycle and Subsystem Integration Test.
"""

import unittest
import tempfile
import os
import sys
from datetime import datetime, timezone

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from db_manager import DatabaseManager
from classifier import HeuristicClassifier
from engine import TelemetryEngine
from exporter import DatasetExporter
from ui.disclaimer import DisclaimerManager
from simulator import generate_sample_session

class TestE2EGUILifecycle(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_e2e_gui.db")
        self.consent_path = os.path.join(self.temp_dir, "consent.json")
        self.db = DatabaseManager(self.db_path)
        self.classifier = HeuristicClassifier()
        self.disclaimer = DisclaimerManager(config_path=self.consent_path)
        self.engine = TelemetryEngine(db=self.db, sample_interval=0.1, classifier_fn=self.classifier.classify)
        self.exporter = DatasetExporter(db=self.db, export_dir=os.path.join(self.temp_dir, "exports"))

    def tearDown(self):
        self.engine.stop()
        self.db.close()
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_full_pipeline_flow(self):
        # 1. First run consent grant
        self.assertFalse(self.disclaimer.has_consented())
        self.assertTrue(self.disclaimer.grant_consent())
        self.assertTrue(self.disclaimer.has_consented())

        # 2. Insert synthetic multi-state stream
        samples = generate_sample_session(15)
        self.db.insert_batch(samples)
        self.assertEqual(self.db.count_records(), 15)

        # 3. Verify confidence scores & finalized values
        records = self.db.get_recent_records(15)
        for rec in records:
            conf = rec["confidence_score"]
            finalized = rec["finalized_value"]
            if conf >= 0.75:
                self.assertEqual(finalized, 1)
            else:
                self.assertEqual(finalized, 0)

        # 4. Incremental export
        exp_manifest = self.exporter.export_incremental(fmt="jsonl")
        self.assertEqual(exp_manifest["record_count"], 15)
        self.assertTrue(os.path.exists(exp_manifest["file_path"]))

        # 5. Subsequent export should have 0 records (deduplication)
        exp_manifest_2 = self.exporter.export_incremental(fmt="jsonl")
        self.assertEqual(exp_manifest_2["record_count"], 0)

if __name__ == "__main__":
    unittest.main()
