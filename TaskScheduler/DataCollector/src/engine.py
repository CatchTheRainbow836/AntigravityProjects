"""
Telemetry Engine for DataCollector.
Coordinates all non-admin Win32 sensor collectors, aggregates data into 5-second feature slices, executes rule-based baseline classification, and writes to SQLite storage.
"""

import time
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable

from collectors.kinetic_collector import KineticCollector
from collectors.window_collector import WindowCollector
from collectors.system_collector import SystemCollector
from db_manager import DatabaseManager

class TelemetryEngine:
    def __init__(
        self,
        db: Optional[DatabaseManager] = None,
        sample_interval: float = 5.0,
        classifier_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    ):
        self.db = db if db is not None else DatabaseManager()
        self.sample_interval = sample_interval
        self.classifier_fn = classifier_fn

        self.kinetic = KineticCollector()
        self.window = WindowCollector()
        self.system = SystemCollector()

        self._is_running = False
        self._is_paused = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._latest_record: Optional[Dict[str, Any]] = None
        self._total_records_collected = 0

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    def start(self):
        with self._lock:
            if self._is_running:
                return
            self._is_running = True
            self._is_paused = False
            self.kinetic.start()
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def pause(self):
        with self._lock:
            self._is_paused = True

    def resume(self):
        with self._lock:
            self._is_paused = False

    def stop(self):
        with self._lock:
            if not self._is_running:
                return
            self._is_running = False
            self._is_paused = False
            self.kinetic.stop()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)

    def _loop(self):
        while self._is_running:
            start_time = time.time()
            time.sleep(self.sample_interval)

            if not self._is_running:
                break
            if self._is_paused:
                continue

            record = self._collect_slice()
            with self._lock:
                self._latest_record = record
                self._total_records_collected += 1

            if self.db:
                self.db.insert_record(record)

    def _collect_slice(self) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        kinetic_data = self.kinetic.sample()
        window_data = self.window.get_active_window_info()
        system_data = self.system.get_system_state()

        record = {
            "timestamp": timestamp,
            "duration_seconds": kinetic_data.get("sample_duration", self.sample_interval),
            "app_name": window_data["app_name"],
            "window_title_sanitized": window_data["window_title_sanitized"],
            "screen_area_pct": window_data["screen_area_pct"],
            "is_fullscreen": window_data["is_fullscreen"],
            "visible_windows": window_data.get("visible_windows", []),
            "keystrokes_per_min": kinetic_data["keystrokes_per_min"],
            "typing_burst_rate": kinetic_data["typing_burst_rate"],
            "mouse_velocity_avg": kinetic_data["mouse_velocity_avg"],
            "clicks_count": kinetic_data["clicks_count"],
            "scroll_delta": kinetic_data["scroll_delta"],
            "is_audio_playing": system_data["is_audio_playing"],
            "is_audio_recording": system_data["is_audio_recording"],
            "system_idle_seconds": system_data["system_idle_seconds"],
            "cognitive_state": "UNCLASSIFIED",
            "domain_label": "Unlabeled",
            "confidence": 0.0,
            "confidence_score": 0.0,
            "finalized_value": 0,
            "active_states": {},
            "label_source": "HEURISTIC_RULE",
            "is_exported": False
        }

        # Apply classifier if provided
        if self.classifier_fn:
            classification = self.classifier_fn(record)
            record.update(classification)

        return record

    def get_current_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "is_running": self._is_running,
                "is_paused": self._is_paused,
                "total_records": self._total_records_collected,
                "latest_record": self._latest_record
            }
