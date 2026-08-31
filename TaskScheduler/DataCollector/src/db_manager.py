"""
Database Manager for DataCollector.
Handles SQLite connection with WAL mode, schema v2 provisioning, migrations, batch insertion, querying, and export tracking.
"""

import sqlite3
import os
import json
import threading
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

DB_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "db_schema.sql")

class DatabaseManager:
    def __init__(self, db_path: str = "datacollector.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        with self._lock:
            # Enable WAL mode and normal synchronous for fast crash-safe autosave
            self.conn.execute("PRAGMA journal_mode = WAL;")
            self.conn.execute("PRAGMA synchronous = NORMAL;")
            self.conn.execute("PRAGMA foreign_keys = ON;")

            if os.path.exists(DB_SCHEMA_PATH):
                with open(DB_SCHEMA_PATH, "r", encoding="utf-8") as f:
                    self.conn.executescript(f.read())

            # Perform column migrations if opening an existing v1 database
            self._migrate_v2()
            self.conn.commit()

    def _migrate_v2(self):
        cursor = self.conn.execute("PRAGMA table_info(telemetry_records)")
        columns = [row[1] for row in cursor.fetchall()]
        if columns:
            if "confidence_score" not in columns:
                self.conn.execute("ALTER TABLE telemetry_records ADD COLUMN confidence_score REAL NOT NULL DEFAULT 0.0")
            if "finalized_value" not in columns:
                self.conn.execute("ALTER TABLE telemetry_records ADD COLUMN finalized_value INTEGER NOT NULL DEFAULT 0")
            if "active_states_json" not in columns:
                self.conn.execute("ALTER TABLE telemetry_records ADD COLUMN active_states_json TEXT DEFAULT '{}'")

    def insert_record(self, record: Dict[str, Any]) -> int:
        conf = float(record.get("confidence", record.get("confidence_score", 0.0)))
        # Finalized value: strictly 1 if confidence >= 0.75, else 0 (or explicitly passed)
        finalized_val = int(record.get("finalized_value", 1 if conf >= 0.75 else 0))
        active_states = record.get("active_states", record.get("active_states_json", {}))
        if isinstance(active_states, dict) or isinstance(active_states, list):
            active_states_str = json.dumps(active_states)
        else:
            active_states_str = str(active_states)

        query = """
        INSERT INTO telemetry_records (
            timestamp, duration_seconds, app_name, window_title_sanitized,
            screen_area_pct, is_fullscreen, keystrokes_per_min, typing_burst_rate,
            mouse_velocity_avg, clicks_count, scroll_delta, is_audio_playing,
            is_audio_recording, system_idle_seconds, cognitive_state, domain_label,
            confidence, confidence_score, finalized_value, active_states_json,
            label_source, is_exported
        ) VALUES (
            :timestamp, :duration_seconds, :app_name, :window_title_sanitized,
            :screen_area_pct, :is_fullscreen, :keystrokes_per_min, :typing_burst_rate,
            :mouse_velocity_avg, :clicks_count, :scroll_delta, :is_audio_playing,
            :is_audio_recording, :system_idle_seconds, :cognitive_state, :domain_label,
            :confidence, :confidence_score, :finalized_value, :active_states_json,
            :label_source, :is_exported
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
            "confidence": conf,
            "confidence_score": conf,
            "finalized_value": finalized_val,
            "active_states_json": active_states_str,
            "label_source": record.get("label_source", "HEURISTIC_RULE"),
            "is_exported": 1 if record.get("is_exported", False) else 0,
        }
        with self._lock:
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
        with self._lock:
            cursor = self.conn.execute("SELECT COUNT(*) FROM telemetry_records")
            return cursor.fetchone()[0]

    def get_recent_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        query = "SELECT * FROM telemetry_records ORDER BY id DESC LIMIT ?"
        with self._lock:
            cursor = self.conn.execute(query, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_unexported_records(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM telemetry_records WHERE is_exported = 0 ORDER BY id ASC"
        if limit:
            query += f" LIMIT {int(limit)}"
        with self._lock:
            cursor = self.conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def mark_records_exported(self, record_ids: List[int]):
        if not record_ids:
            return
        placeholders = ",".join("?" for _ in record_ids)
        with self._lock:
            self.conn.execute(
                f"UPDATE telemetry_records SET is_exported = 1 WHERE id IN ({placeholders})",
                record_ids
            )
            self.conn.commit()

    def update_record_label(self, record_id: int, domain_label: str, cognitive_state: Optional[str] = None):
        with self._lock:
            if cognitive_state:
                self.conn.execute(
                    "UPDATE telemetry_records SET domain_label = ?, cognitive_state = ?, label_source = 'USER_VERIFIED', confidence = 1.0, confidence_score = 1.0, finalized_value = 1 WHERE id = ?",
                    (domain_label, cognitive_state, record_id)
                )
            else:
                self.conn.execute(
                    "UPDATE telemetry_records SET domain_label = ?, label_source = 'USER_VERIFIED', confidence = 1.0, confidence_score = 1.0, finalized_value = 1 WHERE id = ?",
                    (domain_label, record_id)
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
        with self._lock:
            self.conn.execute(query, manifest)
            self.conn.commit()

    def close(self):
        with self._lock:
            self.conn.close()
