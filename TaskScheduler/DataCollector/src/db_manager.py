"""
Database Manager for DataCollector.
Handles SQLite connection, schema provisioning, batch insertion, querying, and export tracking.
"""

import sqlite3
import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

DB_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "db_schema.sql")

class DatabaseManager:
    def __init__(self, db_path: str = "datacollector.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        if os.path.exists(DB_SCHEMA_PATH):
            with open(DB_SCHEMA_PATH, "r", encoding="utf-8") as f:
                self.conn.executescript(f.read())
        self.conn.commit()

    def insert_record(self, record: Dict[str, Any]) -> int:
        query = """
        INSERT INTO telemetry_records (
            timestamp, duration_seconds, app_name, window_title_sanitized,
            screen_area_pct, is_fullscreen, keystrokes_per_min, typing_burst_rate,
            mouse_velocity_avg, clicks_count, scroll_delta, is_audio_playing,
            is_audio_recording, system_idle_seconds, cognitive_state, domain_label,
            confidence, label_source, is_exported
        ) VALUES (
            :timestamp, :duration_seconds, :app_name, :window_title_sanitized,
            :screen_area_pct, :is_fullscreen, :keystrokes_per_min, :typing_burst_rate,
            :mouse_velocity_avg, :clicks_count, :scroll_delta, :is_audio_playing,
            :is_audio_recording, :system_idle_seconds, :cognitive_state, :domain_label,
            :confidence, :label_source, :is_exported
        )
        """
        params = {
            "timestamp": record.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "duration_seconds": record.get("duration_seconds", 5.0),
            "app_name": record.get("app_name", "UNKNOWN.EXE"),
            "window_title_sanitized": record.get("window_title_sanitized", ""),
            "screen_area_pct": record.get("screen_area_pct", 100.0),
            "is_fullscreen": 1 if record.get("is_fullscreen", False) else 0,
            "keystrokes_per_min": record.get("keystrokes_per_min", 0.0),
            "typing_burst_rate": record.get("typing_burst_rate", 0.0),
            "mouse_velocity_avg": record.get("mouse_velocity_avg", 0.0),
            "clicks_count": record.get("clicks_count", 0),
            "scroll_delta": record.get("scroll_delta", 0),
            "is_audio_playing": 1 if record.get("is_audio_playing", False) else 0,
            "is_audio_recording": 1 if record.get("is_audio_recording", False) else 0,
            "system_idle_seconds": record.get("system_idle_seconds", 0.0),
            "cognitive_state": record.get("cognitive_state", "UNCLASSIFIED"),
            "domain_label": record.get("domain_label", "Unlabeled"),
            "confidence": record.get("confidence", 0.0),
            "label_source": record.get("label_source", "HEURISTIC_RULE"),
            "is_exported": 1 if record.get("is_exported", False) else 0,
        }
        cursor = self.conn.execute(query, params)
        self.conn.commit()
        return cursor.lastrowid

    def insert_batch(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        for r in records:
            self.insert_record(r)
        return len(records)

    def count_records(self) -> int:
        cursor = self.conn.execute("SELECT COUNT(*) FROM telemetry_records")
        return cursor.fetchone()[0]

    def get_unexported_records(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM telemetry_records WHERE is_exported = 0 ORDER BY id ASC"
        if limit:
            query += f" LIMIT {int(limit)}"
        cursor = self.conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def mark_records_exported(self, record_ids: List[int]):
        if not record_ids:
            return
        placeholders = ",".join("?" for _ in record_ids)
        self.conn.execute(
            f"UPDATE telemetry_records SET is_exported = 1 WHERE id IN ({placeholders})",
            record_ids
        )
        self.conn.commit()

    def record_export(self, manifest: Dict[str, Any]):
        query = """
        INSERT INTO export_history (
            export_id, exported_at, record_count, start_timestamp,
            end_timestamp, format, file_path, content_hash
        ) VALUES (
            :export_id, :exported_at, :record_count, :start_timestamp,
            :end_timestamp, :format, :file_path, :content_hash
        )
        """
        self.conn.execute(query, manifest)
        self.conn.commit()

    def close(self):
        self.conn.close()
