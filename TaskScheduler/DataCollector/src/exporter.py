"""
Dataset Exporter for DataCollector.
Exports local SQLite telemetry records to machine-learning friendly formats (JSONL, CSV) with cryptographic hash tracking and strict deduplication guarantees.
"""

import os
import json
import csv
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from db_manager import DatabaseManager

DEFAULT_EXPORT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "exports"))

class DatasetExporter:
    def __init__(self, db: DatabaseManager, export_dir: str = DEFAULT_EXPORT_DIR):
        self.db = db
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    def _compute_file_hash(self, file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def export_incremental(
        self,
        fmt: str = "jsonl",
        filename_prefix: str = "telemetry_dataset"
    ) -> Dict[str, Any]:
        """
        Exports only unexported records and marks them as exported to guarantee zero duplicates.
        """
        records = self.db.get_unexported_records()
        if not records:
            return {
                "export_id": None,
                "record_count": 0,
                "message": "No new unexported records available."
            }

        now_utc = datetime.now(timezone.utc)
        timestamp_str = now_utc.strftime("%Y%m%d_%H%M%S_%f")
        export_id = f"EXP_{timestamp_str}_{len(records)}"
        file_name = f"{filename_prefix}_{timestamp_str}.{fmt}"
        file_path = os.path.join(self.export_dir, file_name)

        if fmt == "jsonl":
            with open(file_path, "w", encoding="utf-8") as f:
                for r in records:
                    f.write(json.dumps(r) + "\n")
        elif fmt == "csv":
            if records:
                keys = list(records[0].keys())
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(records)
        else:
            raise ValueError(f"Unsupported export format: {fmt}. Use 'jsonl' or 'csv'.")

        file_hash = self._compute_file_hash(file_path)
        record_ids = [r["id"] for r in records]

        manifest = {
            "export_id": export_id,
            "exported_at": now_utc.isoformat(),
            "record_count": len(records),
            "start_timestamp": records[0]["timestamp"],
            "end_timestamp": records[-1]["timestamp"],
            "format": fmt,
            "file_path": file_path,
            "content_hash": file_hash
        }

        # Atomically record export manifest and update exported flags
        self.db.record_export(manifest)
        self.db.mark_records_exported(record_ids)

        return manifest

    def export_all(
        self,
        fmt: str = "jsonl",
        filename_prefix: str = "telemetry_full_dump"
    ) -> Dict[str, Any]:
        """
        Dumps the entire database contents to a standalone timestamped snapshot without altering export flags.
        """
        with self.db._lock:
            cursor = self.db.conn.execute("SELECT * FROM telemetry_records ORDER BY id ASC")
            records = [dict(row) for row in cursor.fetchall()]

        if not records:
            return {"record_count": 0, "message": "Database is empty."}

        now_utc = datetime.now(timezone.utc)
        timestamp_str = now_utc.strftime("%Y%m%d_%H%M%S")
        export_id = f"FULL_{timestamp_str}_{len(records)}"
        file_name = f"{filename_prefix}_{timestamp_str}.{fmt}"
        file_path = os.path.join(self.export_dir, file_name)

        if fmt == "jsonl":
            with open(file_path, "w", encoding="utf-8") as f:
                for r in records:
                    f.write(json.dumps(r) + "\n")
        elif fmt == "csv":
            keys = list(records[0].keys())
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(records)

        file_hash = self._compute_file_hash(file_path)
        return {
            "export_id": export_id,
            "exported_at": now_utc.isoformat(),
            "record_count": len(records),
            "format": fmt,
            "file_path": file_path,
            "content_hash": file_hash
        }
