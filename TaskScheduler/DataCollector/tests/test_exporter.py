"""
Unit tests for DatasetExporter — incremental deduplication and content hash validation.
"""

import unittest
import os
import sys
import tempfile
import json
import csv

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from exporter import DatasetExporter
from db_manager import DatabaseManager
from simulator import generate_sample_session


class TestDatasetExporter(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.export_dir = tempfile.mkdtemp()
        self.db = DatabaseManager(self.temp_db.name)
        self.exporter = DatasetExporter(self.db, export_dir=self.export_dir)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)
        # Clean up exports
        for f in os.listdir(self.export_dir):
            os.remove(os.path.join(self.export_dir, f))
        os.rmdir(self.export_dir)

    def test_jsonl_export_correct_count(self):
        self.db.insert_batch(generate_sample_session(10))
        manifest = self.exporter.export_incremental(fmt="jsonl")
        self.assertEqual(manifest["record_count"], 10)
        self.assertTrue(os.path.exists(manifest["file_path"]))

        with open(manifest["file_path"], "r", encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        self.assertEqual(len(lines), 10)
        # Verify each line is valid JSON
        for line in lines:
            row = json.loads(line)
            self.assertIn("app_name", row)
            self.assertIn("cognitive_state", row)

    def test_csv_export_correct_count(self):
        self.db.insert_batch(generate_sample_session(8))
        manifest = self.exporter.export_incremental(fmt="csv")
        self.assertEqual(manifest["record_count"], 8)

        with open(manifest["file_path"], "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), 8)
        self.assertIn("cognitive_state", rows[0])

    def test_deduplication_no_double_export(self):
        """Second incremental export should find 0 new records."""
        self.db.insert_batch(generate_sample_session(5))
        m1 = self.exporter.export_incremental(fmt="jsonl")
        self.assertEqual(m1["record_count"], 5)

        m2 = self.exporter.export_incremental(fmt="jsonl")
        self.assertEqual(m2["record_count"], 0)
        self.assertIsNone(m2["export_id"])

    def test_new_records_exported_incrementally(self):
        """After first export, only newly inserted records should be exported."""
        self.db.insert_batch(generate_sample_session(5))
        m1 = self.exporter.export_incremental(fmt="jsonl")
        self.assertEqual(m1["record_count"], 5)

        # Insert 5 more records
        self.db.insert_batch(generate_sample_session(5))
        m2 = self.exporter.export_incremental(fmt="jsonl")
        self.assertEqual(m2["record_count"], 5)

    def test_content_hash_is_sha256(self):
        self.db.insert_batch(generate_sample_session(3))
        manifest = self.exporter.export_incremental(fmt="jsonl")
        self.assertEqual(len(manifest["content_hash"]), 64)  # SHA256 hex = 64 chars

    def test_export_manifest_recorded_in_db(self):
        self.db.insert_batch(generate_sample_session(4))
        manifest = self.exporter.export_incremental(fmt="jsonl")
        with self.db._lock:
            cursor = self.db.conn.execute(
                "SELECT * FROM export_history WHERE export_id=?", (manifest["export_id"],)
            )
            row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["record_count"], 4)

    def test_empty_db_export_returns_no_data(self):
        manifest = self.exporter.export_incremental(fmt="jsonl")
        self.assertEqual(manifest["record_count"], 0)
        self.assertIsNone(manifest["export_id"])

    def test_full_dump_does_not_alter_export_flags(self):
        self.db.insert_batch(generate_sample_session(6))
        self.exporter.export_all(fmt="jsonl")
        # After full dump, incremental should still find all 6 unexported
        m = self.exporter.export_incremental(fmt="jsonl")
        self.assertEqual(m["record_count"], 6)


if __name__ == "__main__":
    unittest.main()
