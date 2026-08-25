"""
Unit tests for SQLite database operations, indexing, and simulator data insertion.
"""

import unittest
import os
import tempfile
import sys

# Ensure src path is accessible
CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from db_manager import DatabaseManager
from simulator import generate_sample_session

class TestStorageManager(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    def test_schema_initialization(self):
        cursor = self.db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        self.assertIn("telemetry_records", tables)
        self.assertIn("behavior_segments", tables)
        self.assertIn("export_history", tables)
        self.assertIn("user_presets", tables)

    def test_insert_and_count(self):
        samples = generate_sample_session(15)
        self.assertEqual(len(samples), 15)
        inserted = self.db.insert_batch(samples)
        self.assertEqual(inserted, 15)
        self.assertEqual(self.db.count_records(), 15)

    def test_unexported_filtering_and_marking(self):
        samples = generate_sample_session(10)
        self.db.insert_batch(samples)

        unexported = self.db.get_unexported_records()
        self.assertEqual(len(unexported), 10)

        # Mark first 5 as exported
        first_five_ids = [row["id"] for row in unexported[:5]]
        self.db.mark_records_exported(first_five_ids)

        remaining_unexported = self.db.get_unexported_records()
        self.assertEqual(len(remaining_unexported), 5)

    def test_export_manifest_recording(self):
        manifest = {
            "export_id": "EXP-001",
            "exported_at": "2026-08-25T09:00:00Z",
            "record_count": 25,
            "start_timestamp": "2026-08-25T08:00:00Z",
            "end_timestamp": "2026-08-25T08:59:55Z",
            "format": "jsonl",
            "file_path": "exports/dataset_001.jsonl",
            "content_hash": "a1b2c3d4e5f6"
        }
        self.db.record_export(manifest)
        cursor = self.db.conn.execute("SELECT * FROM export_history WHERE export_id='EXP-001'")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["record_count"], 25)

if __name__ == "__main__":
    unittest.main()
